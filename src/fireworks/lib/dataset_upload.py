"""Multi-file dataset upload helper.

The generated ``datasets.upload()`` method accepts a single multipart file
(and is limited to 150 MB per request), and generated files are regenerated
from the OpenAPI spec, so this module implements the multi-shard flow on top
of the generated ``datasets.get_upload_endpoint`` / ``datasets.validate_upload``
APIs instead. ``fireworks.lib`` is never modified by the generator (see
CONTRIBUTING.md).

Typical use, for a dataset whose files are uploaded by the caller::

    from fireworks import Fireworks
    from fireworks.lib.dataset_upload import count_dataset_examples, upload_dataset_shards

    client = Fireworks()
    client.datasets.create(
        dataset_id="my-dataset",
        dataset={"user_uploaded": {}, "example_count": str(count_dataset_examples("shards/"))},
    )
    upload_dataset_shards(client, "my-dataset", "shards/")

``upload_dataset_shards``:

1. Resolves the local path into ``.jsonl`` shards (see "Directory policy").
2. Refuses datasets that require client-side (CMEK) encryption: this helper
   does not encrypt, so it fails closed rather than upload plaintext. Use
   ``firectl dataset create`` for CMEK datasets.
3. Registers every shard in a single ``get_upload_endpoint`` request (the
   endpoint overwrites the dataset's registered files on each call, so
   per-shard requests would drop earlier shards), and requires a signed URL
   for every shard.
4. PUTs each shard's bytes to its signed URL with a plain HTTP client that
   carries no Fireworks credentials. Signed URLs expire after one hour, so the
   complete set is re-requested before a later shard if the earlier ones took
   too long.
5. Calls ``validate_upload`` so the dataset becomes ready.

Directory policy: a path can be a single ``.jsonl`` file or a directory of
top-level shards with a lowercase ``.jsonl`` extension uploaded as one dataset
(managed directory loaders do not discover uppercase extensions). Subdirectories are
rejected (the dataset API stores basenames only, so nested files would
flatten and collide), non-``.jsonl`` entries are rejected, symlinked entries
are rejected (so nothing outside the chosen directory is uploaded), empty
(0-byte) files are rejected (the server refuses to validate empty objects),
and an empty directory is an error, so no data is ever silently dropped.
"""

from __future__ import annotations

import os
import time
from typing import TYPE_CHECKING, Dict, List, Optional

import httpx

from .._exceptions import FireworksError

if TYPE_CHECKING:
    from .._client import Fireworks

__all__ = [
    "DatasetUploadError",
    "collect_dataset_shards",
    "count_dataset_examples",
    "upload_dataset_shards",
]

# Dataset shards are large; give signed-URL PUTs a generous default timeout.
_UPLOAD_TIMEOUT = httpx.Timeout(600.0, connect=30.0)

# The server signs upload URLs for one hour; re-request the full set before
# starting a later shard once this much time has passed since signing.
_SIGNED_URL_REFRESH_AFTER_SECONDS = 45 * 60

# Encryption states that mean the dataset is stored as plaintext. Anything
# else (CMEK, or a state this SDK version does not know) fails closed.
_PLAINTEXT_ENCRYPTION_STATES = frozenset({"", "ENCRYPTION_STATE_UNSPECIFIED", "ENCRYPTION_STATE_PLAINTEXT"})


class DatasetUploadError(FireworksError):
    """Raised when a dataset upload cannot be completed safely."""


def collect_dataset_shards(path: str) -> List[str]:
    """Return the local ``.jsonl`` files a dataset path resolves to.

    ``path`` can be a single ``.jsonl`` file or a directory of top-level
    ``.jsonl`` shards (returned sorted by name). Raises ``ValueError`` for
    missing paths, subdirectories, symlinked directory entries, non-``.jsonl``
    files, empty files, and directories with no ``.jsonl`` files.
    """
    if not os.path.exists(path):
        raise ValueError(f"dataset path does not exist: {path}")
    if not os.path.isdir(path):
        if not os.path.isfile(path):
            raise ValueError(f"dataset path is not a regular file or a directory: {path}")
        _require_jsonl(path)
        _require_non_empty(path)
        return [path]

    shards: List[str] = []
    for entry in sorted(os.listdir(path)):
        entry_path = os.path.join(path, entry)
        # Check for symlinks first: isdir/isfile follow them.
        if os.path.islink(entry_path):
            raise ValueError(f"symlinks are not supported in dataset directory {path}: found {entry_path}")
        if os.path.isdir(entry_path):
            raise ValueError(
                f"subdirectories are not supported in dataset directory {path} "
                f"(only top-level .jsonl files): found {entry_path}"
            )
        if not os.path.isfile(entry_path):
            raise ValueError(f"dataset directory entry {entry_path} is not a regular file")
        _require_jsonl(entry_path)
        if os.path.splitext(entry_path)[1] != ".jsonl":
            raise ValueError(
                f"dataset shard {entry_path} must use a lowercase .jsonl extension so managed training can discover it"
            )
        _require_non_empty(entry_path)
        shards.append(entry_path)

    if not shards:
        raise ValueError(f"dataset directory {path} contains no .jsonl files")
    return shards


def _require_jsonl(path: str) -> None:
    if os.path.splitext(path)[1].lower() != ".jsonl":
        raise ValueError(f"dataset file must have .jsonl file extension: {path}")


def _require_non_empty(path: str) -> None:
    if os.path.getsize(path) == 0:
        raise ValueError(f"dataset file {path} is empty")


def count_dataset_examples(path: str) -> int:
    """Return the total number of lines (examples) across a dataset path's shards.

    Use it as ``example_count`` when creating an uploaded dataset. ``path``
    follows the same policy as ``collect_dataset_shards``.
    """
    total = 0
    for shard in collect_dataset_shards(path):
        with open(shard, "rb") as shard_file:
            total += sum(1 for _ in shard_file)
    return total


def upload_dataset_shards(
    client: Fireworks,
    dataset_id: str,
    path: str,
    *,
    account_id: Optional[str] = None,
) -> None:
    """Upload a ``.jsonl`` file or a directory of top-level ``.jsonl`` shards, then validate the upload.

    The dataset must already exist and be awaiting upload. Raises ``ValueError``
    for invalid paths (see ``collect_dataset_shards``), ``DatasetUploadError``
    if the dataset requires CMEK encryption or the upload endpoint does not
    return a usable ``https`` URL for every shard, and ``httpx.HTTPStatusError``
    if a shard upload fails.
    """
    shards = collect_dataset_shards(path)

    filename_to_size: Dict[str, str] = {}
    filename_to_path: Dict[str, str] = {}
    for shard in shards:
        filename = os.path.basename(shard)
        if filename in filename_to_path:
            raise ValueError(f"duplicate dataset file name {filename} ({filename_to_path[filename]} and {shard})")
        filename_to_size[filename] = str(os.path.getsize(shard))
        filename_to_path[filename] = shard

    # Fail closed before any bytes leave the machine: this helper cannot encrypt.
    dataset = client.datasets.get(dataset_id, account_id=account_id)
    encryption_state = dataset.to_dict().get("encryptionState", "")
    if encryption_state not in _PLAINTEXT_ENCRYPTION_STATES:
        raise DatasetUploadError(
            f"dataset {dataset_id} has encryption state {encryption_state}; upload_dataset_shards does not "
            "encrypt, so it refuses to upload plaintext. Use `firectl dataset create` for CMEK datasets."
        )

    def request_signed_urls() -> Dict[str, str]:
        response = client.datasets.get_upload_endpoint(
            dataset_id,
            account_id=account_id,
            filename_to_size=filename_to_size,
        )
        signed_urls = response.filename_to_signed_urls or {}
        missing = sorted(name for name in filename_to_size if not signed_urls.get(name))
        if missing:
            raise DatasetUploadError(f"upload endpoint returned no signed URL for: {', '.join(missing)}")
        unexpected = sorted(set(signed_urls) - set(filename_to_size))
        if unexpected:
            raise DatasetUploadError(
                f"upload endpoint returned signed URLs for unexpected files: {', '.join(unexpected)}"
            )
        insecure = sorted(name for name, url in signed_urls.items() if httpx.URL(url).scheme != "https")
        if insecure:
            raise DatasetUploadError(f"upload endpoint returned non-https upload URLs for: {', '.join(insecure)}")
        return signed_urls

    signed_urls = request_signed_urls()
    signed_at = time.monotonic()

    # A separate plain client: signed URLs must never receive Fireworks API credentials.
    with httpx.Client(timeout=_UPLOAD_TIMEOUT) as http:
        for index, filename in enumerate(filename_to_size):
            if index > 0 and time.monotonic() - signed_at > _SIGNED_URL_REFRESH_AFTER_SECONDS:
                # Re-send the complete map: the endpoint overwrites the registered files.
                signed_urls = request_signed_urls()
                signed_at = time.monotonic()
            size = filename_to_size[filename]
            with open(filename_to_path[filename], "rb") as shard_file:
                upload_response = http.put(
                    signed_urls[filename],
                    content=shard_file,
                    headers={
                        # Both headers are part of the URL signature.
                        "Content-Type": "application/octet-stream",
                        "X-Goog-Content-Length-Range": f"{size},{size}",
                    },
                )
            upload_response.raise_for_status()

    client.datasets.validate_upload(dataset_id, account_id=account_id, body={})
