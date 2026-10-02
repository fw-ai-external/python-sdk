from __future__ import annotations

import os
import json
from typing import Any, Dict, List, Iterator, Optional
from pathlib import Path

import httpx
import respx
import pytest

from fireworks import Fireworks
from fireworks.lib import dataset_upload
from fireworks.lib.dataset_upload import (
    DatasetUploadError,
    upload_dataset_shards,
    collect_dataset_shards,
    count_dataset_examples,
)

CHAT_LINE = '{"messages": [{"role": "user", "content": "Hello"}]}\n'

API_BASE_URL = "https://api.test"
STORAGE_BASE_URL = "https://storage.test"
API_KEY = "fw-test-api-key"
ACCOUNT_ID = "my-account"
DATASET_ID = "my-dataset"
DATASET_PATH = f"/v1/accounts/{ACCOUNT_ID}/datasets/{DATASET_ID}"


def _write_shards(dir_path: Path, lines_per_shard: Dict[str, int]) -> Dict[str, int]:
    sizes: Dict[str, int] = {}
    for name, lines in lines_per_shard.items():
        content = CHAT_LINE * lines
        (dir_path / name).write_text(content, encoding="utf-8")
        sizes[name] = len(content.encode("utf-8"))
    return sizes


class _FakeServer:
    """Records the control-plane and signed-URL traffic of one upload."""

    def __init__(
        self,
        router: respx.MockRouter,
        *,
        encryption_state: Optional[str] = None,
        signed_urls: Optional[Dict[str, str]] = None,
        put_status: int = 200,
    ) -> None:
        self.encryption_state = encryption_state
        self.signed_urls = signed_urls
        self.put_status = put_status
        self.events: List[str] = []
        self.endpoint_requests: List[Dict[str, str]] = []
        self.puts: Dict[str, httpx.Request] = {}
        self.put_bodies: Dict[str, bytes] = {}

        router.get(f"{API_BASE_URL}{DATASET_PATH}").mock(side_effect=self._get_dataset)
        router.post(f"{API_BASE_URL}{DATASET_PATH}:getUploadEndpoint").mock(side_effect=self._get_upload_endpoint)
        router.post(f"{API_BASE_URL}{DATASET_PATH}:validateUpload").mock(side_effect=self._validate_upload)
        router.put(url__startswith=STORAGE_BASE_URL).mock(side_effect=self._put)

    def _get_dataset(self, _request: httpx.Request) -> httpx.Response:
        self.events.append("get")
        body: Dict[str, Any] = {"name": f"accounts/{ACCOUNT_ID}/datasets/{DATASET_ID}", "state": "UPLOADING"}
        if self.encryption_state is not None:
            body["encryptionState"] = self.encryption_state
        return httpx.Response(200, json=body)

    def _get_upload_endpoint(self, request: httpx.Request) -> httpx.Response:
        self.events.append("getUploadEndpoint")
        filename_to_size: Dict[str, str] = json.loads(request.content)["filenameToSize"]
        self.endpoint_requests.append(filename_to_size)
        signed_urls = self.signed_urls
        if signed_urls is None:
            signed_urls = {name: f"{STORAGE_BASE_URL}/bucket/{name}" for name in filename_to_size}
        return httpx.Response(200, json={"filenameToSignedUrls": signed_urls})

    def _put(self, request: httpx.Request) -> httpx.Response:
        name = request.url.path.rsplit("/", 1)[-1]
        self.events.append(f"put:{name}")
        self.puts[name] = request
        self.put_bodies[name] = request.read()
        return httpx.Response(self.put_status)

    def _validate_upload(self, _request: httpx.Request) -> httpx.Response:
        self.events.append("validateUpload")
        return httpx.Response(200, json={})


@pytest.fixture
def router() -> Iterator[respx.MockRouter]:
    with respx.mock(assert_all_called=False) as mock_router:
        yield mock_router


@pytest.fixture
def client() -> Iterator[Fireworks]:
    with Fireworks(base_url=API_BASE_URL, api_key=API_KEY, account_id=ACCOUNT_ID, max_retries=0) as fw_client:
        yield fw_client


# --- collect_dataset_shards / count_dataset_examples ---


def test_collect_dataset_shards_single_file(tmp_path: Path) -> None:
    _write_shards(tmp_path, {"train.jsonl": 1})

    assert collect_dataset_shards(str(tmp_path / "train.jsonl")) == [str(tmp_path / "train.jsonl")]


def test_collect_dataset_shards_directory_sorted(tmp_path: Path) -> None:
    _write_shards(tmp_path, {"b.jsonl": 1, "a.jsonl": 1})

    assert collect_dataset_shards(str(tmp_path)) == [str(tmp_path / "a.jsonl"), str(tmp_path / "b.jsonl")]


def test_collect_dataset_shards_rejects_missing_path(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="does not exist"):
        collect_dataset_shards(str(tmp_path / "missing.jsonl"))


def test_collect_dataset_shards_rejects_bad_extension(tmp_path: Path) -> None:
    (tmp_path / "train.txt").write_text(CHAT_LINE, encoding="utf-8")

    with pytest.raises(ValueError, match=r"\.jsonl file extension"):
        collect_dataset_shards(str(tmp_path / "train.txt"))


def test_collect_dataset_shards_rejects_empty_directory(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match=r"contains no \.jsonl files"):
        collect_dataset_shards(str(tmp_path))


def test_collect_dataset_shards_rejects_non_jsonl_entry(tmp_path: Path) -> None:
    _write_shards(tmp_path, {"train.jsonl": 1})
    (tmp_path / "README.md").write_text("notes", encoding="utf-8")

    # Rejected rather than silently skipped.
    with pytest.raises(ValueError, match=r"README\.md"):
        collect_dataset_shards(str(tmp_path))


def test_collect_dataset_shards_rejects_subdirectory(tmp_path: Path) -> None:
    _write_shards(tmp_path, {"train.jsonl": 1})
    (tmp_path / "nested").mkdir()

    with pytest.raises(ValueError, match="subdirectories are not supported"):
        collect_dataset_shards(str(tmp_path))


def test_collect_dataset_shards_rejects_symlink(tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    _write_shards(outside, {"secret.jsonl": 1})
    shard_dir = tmp_path / "shards"
    shard_dir.mkdir()
    _write_shards(shard_dir, {"train.jsonl": 1})
    os.symlink(outside / "secret.jsonl", shard_dir / "linked.jsonl")

    with pytest.raises(ValueError, match="symlinks are not supported"):
        collect_dataset_shards(str(shard_dir))


def test_collect_dataset_shards_rejects_symlinked_directory_entry(tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    shard_dir = tmp_path / "shards"
    shard_dir.mkdir()
    os.symlink(outside, shard_dir / "linked-dir")

    with pytest.raises(ValueError, match="symlinks are not supported"):
        collect_dataset_shards(str(shard_dir))


def test_collect_dataset_shards_rejects_empty_file(tmp_path: Path) -> None:
    (tmp_path / "train.jsonl").write_bytes(b"")

    with pytest.raises(ValueError, match="is empty"):
        collect_dataset_shards(str(tmp_path / "train.jsonl"))


def test_collect_dataset_shards_rejects_empty_shard_in_directory(tmp_path: Path) -> None:
    _write_shards(tmp_path, {"a.jsonl": 3})
    (tmp_path / "b.jsonl").write_bytes(b"")

    # The positive total must not hide an empty shard the server would refuse.
    with pytest.raises(ValueError, match=r"b\.jsonl is empty"):
        collect_dataset_shards(str(tmp_path))


def test_count_dataset_examples_sums_shards(tmp_path: Path) -> None:
    _write_shards(tmp_path, {"a.jsonl": 3, "b.jsonl": 2})

    assert count_dataset_examples(str(tmp_path)) == 5
    assert count_dataset_examples(str(tmp_path / "a.jsonl")) == 3


# --- upload_dataset_shards ---


def test_upload_directory_registers_all_shards_once_and_validates(
    tmp_path: Path, router: respx.MockRouter, client: Fireworks
) -> None:
    sizes = _write_shards(tmp_path, {"shard-1.jsonl": 2, "shard-2.jsonl": 1})
    server = _FakeServer(router)

    upload_dataset_shards(client, DATASET_ID, str(tmp_path))

    # One request registered every shard with its exact size.
    assert server.endpoint_requests == [{name: str(size) for name, size in sizes.items()}]
    # Every shard was uploaded, then the upload was validated.
    assert server.events == ["get", "getUploadEndpoint", "put:shard-1.jsonl", "put:shard-2.jsonl", "validateUpload"]
    for name, size in sizes.items():
        assert server.put_bodies[name] == (tmp_path / name).read_bytes()
        headers = server.puts[name].headers
        # Both headers are part of the signed URL's signature.
        assert headers["Content-Type"] == "application/octet-stream"
        assert headers["X-Goog-Content-Length-Range"] == f"{size},{size}"
        assert headers["Content-Length"] == str(size)
        # Signed URLs must never receive Fireworks credentials.
        assert "authorization" not in headers
        assert all(API_KEY not in value for value in headers.values())


def test_upload_single_file(tmp_path: Path, router: respx.MockRouter, client: Fireworks) -> None:
    sizes = _write_shards(tmp_path, {"train.jsonl": 4, "other.jsonl": 1})
    server = _FakeServer(router)

    upload_dataset_shards(client, DATASET_ID, str(tmp_path / "train.jsonl"))

    assert server.endpoint_requests == [{"train.jsonl": str(sizes["train.jsonl"])}]
    assert server.events == ["get", "getUploadEndpoint", "put:train.jsonl", "validateUpload"]


def test_upload_missing_signed_url_fails_before_any_put(
    tmp_path: Path, router: respx.MockRouter, client: Fireworks
) -> None:
    _write_shards(tmp_path, {"shard-1.jsonl": 1, "shard-2.jsonl": 1})
    server = _FakeServer(router, signed_urls={"shard-1.jsonl": f"{STORAGE_BASE_URL}/bucket/shard-1.jsonl"})

    with pytest.raises(DatasetUploadError, match=r"no signed URL for: shard-2\.jsonl"):
        upload_dataset_shards(client, DATASET_ID, str(tmp_path))

    assert server.puts == {}
    assert "validateUpload" not in server.events


def test_upload_rejects_non_https_signed_url(tmp_path: Path, router: respx.MockRouter, client: Fireworks) -> None:
    _write_shards(tmp_path, {"train.jsonl": 1})
    server = _FakeServer(router, signed_urls={"train.jsonl": "http://storage.test/bucket/train.jsonl"})

    with pytest.raises(DatasetUploadError, match="non-https"):
        upload_dataset_shards(client, DATASET_ID, str(tmp_path))

    assert server.puts == {}
    assert "validateUpload" not in server.events


@pytest.mark.parametrize("encryption_state", ["ENCRYPTION_STATE_CMEK", "ENCRYPTION_STATE_SOMETHING_NEW"])
def test_upload_fails_closed_for_encrypted_datasets(
    tmp_path: Path, router: respx.MockRouter, client: Fireworks, encryption_state: str
) -> None:
    _write_shards(tmp_path, {"train.jsonl": 1})
    server = _FakeServer(router, encryption_state=encryption_state)

    with pytest.raises(DatasetUploadError, match="refuses to upload plaintext"):
        upload_dataset_shards(client, DATASET_ID, str(tmp_path))

    # Nothing was registered or uploaded.
    assert server.events == ["get"]


@pytest.mark.parametrize("encryption_state", [None, "ENCRYPTION_STATE_UNSPECIFIED", "ENCRYPTION_STATE_PLAINTEXT"])
def test_upload_allows_plaintext_datasets(
    tmp_path: Path, router: respx.MockRouter, client: Fireworks, encryption_state: Optional[str]
) -> None:
    _write_shards(tmp_path, {"train.jsonl": 1})
    server = _FakeServer(router, encryption_state=encryption_state)

    upload_dataset_shards(client, DATASET_ID, str(tmp_path))

    assert server.events[-1] == "validateUpload"


def test_upload_failed_put_raises_without_validating(
    tmp_path: Path, router: respx.MockRouter, client: Fireworks
) -> None:
    _write_shards(tmp_path, {"train.jsonl": 1})
    server = _FakeServer(router, put_status=403)

    with pytest.raises(httpx.HTTPStatusError):
        upload_dataset_shards(client, DATASET_ID, str(tmp_path))

    assert "validateUpload" not in server.events


def test_upload_refreshes_signed_urls_with_full_map(
    tmp_path: Path, router: respx.MockRouter, client: Fireworks, monkeypatch: pytest.MonkeyPatch
) -> None:
    sizes = _write_shards(tmp_path, {"shard-1.jsonl": 1, "shard-2.jsonl": 1})
    server = _FakeServer(router)
    # Treat URLs as stale immediately so a refresh happens before the second shard.
    monkeypatch.setattr(dataset_upload, "_SIGNED_URL_REFRESH_AFTER_SECONDS", -1)

    upload_dataset_shards(client, DATASET_ID, str(tmp_path))

    # Every refresh re-registers the complete map: the endpoint overwrites the file list.
    full_map = {name: str(size) for name, size in sizes.items()}
    assert server.endpoint_requests == [full_map, full_map]
    assert server.events[-1] == "validateUpload"


def test_uppercase_directory_shard_rejected_before_api_calls(tmp_path: Path, client: Fireworks) -> None:
    _write_shards(tmp_path, {"a.jsonl": 1, "b.JSONL": 1})
    with respx.mock(assert_all_called=False):
        with pytest.raises(ValueError, match=r"lowercase \.jsonl extension"):
            upload_dataset_shards(client, DATASET_ID, str(tmp_path))


def test_uppercase_single_file_preserved(tmp_path: Path) -> None:
    _write_shards(tmp_path, {"train.JSONL": 1})
    path = str(tmp_path / "train.JSONL")
    assert collect_dataset_shards(path) == [path]
