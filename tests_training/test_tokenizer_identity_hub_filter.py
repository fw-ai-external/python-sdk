"""Hub prefilter: metadata shortcuts, byte fallbacks and revision coherence."""

from __future__ import annotations

import json
import hashlib
from types import SimpleNamespace
from typing import Any
from pathlib import Path

import pytest
from huggingface_hub import constants, try_to_load_from_cache
from huggingface_hub.utils import EntryNotFoundError, OfflineModeIsEnabled

from fireworks.training.sdk import tokenizer_identity as identity

V4_REPO = "deepseek-ai/DeepSeek-V4-Flash-0731"
V4_REVISION = "7872f01b1d1fe23eabc4c98b48bffcef5a386062"
HEAD_COMMIT = "c" * 40
BRANCH = "topic-branch"
FORMS = {
    "hub": (
        6_367_146,
        "628e3364caad11bdf9e67cea06eae7878122811d",
        "8f9f37ca37fdc4f5fd36d5cf4d3b0e8392edb4e894fd10cc0d70b4957c8633cf",
    ),
    "auto": (
        10_071_664,
        "eac7750db932c0387e426de38863912bb4f348f0",
        "8421075aceec0741baf15179b6c337f443f9029e53ea88d8c1e909dd0d69b70b",
    ),
    "backend": (
        10_071_940,
        "92485c7d3e55b9fb01b453e7629e4c64dbcde423",
        "cc8ae8da67336986713cd73e08ec960320703283e5d6c0f2d50075eedd41a2ab",
    ),
}


@pytest.fixture(scope="module")
def form_bytes(tmp_path_factory: pytest.TempPathFactory) -> dict[str, bytes]:
    cached = try_to_load_from_cache(V4_REPO, "tokenizer.json", revision=V4_REVISION)
    if cached is None:
        pytest.skip("pinned DeepSeek V4 tokenizer.json not in HF cache")
    transformers = pytest.importorskip("transformers")
    # lazy: Transformers is an optional SDK dependency.
    from transformers.tokenization_utils_tokenizers import TokenizersBackend

    root = tmp_path_factory.mktemp("v4-forms")
    result = {"hub": Path(cached).read_bytes()}
    for name, loader, kwargs in (
        ("auto", transformers.AutoTokenizer, {"trust_remote_code": False}),
        ("backend", TokenizersBackend, {"add_bos_token": False, "add_eos_token": False}),
    ):
        tokenizer = loader.from_pretrained(V4_REPO, revision=V4_REVISION, **kwargs)
        tokenizer.save_pretrained(root / name)
        result[name] = (root / name / "tokenizer.json").read_bytes()
    for name, data in result.items():
        size, blob, digest = FORMS[name]
        assert len(data) == size
        assert hashlib.sha256(data).hexdigest() == digest
        assert hashlib.sha1(f"blob {size}\0".encode() + data).hexdigest() == blob
    return result


@pytest.fixture
def hub(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> SimpleNamespace:
    """One concrete fake for the two Hub reads; it never accesses the network."""
    monkeypatch.setattr(constants, "ENDPOINT", "https://huggingface.co")
    monkeypatch.setattr(constants, "HF_HUB_OFFLINE", False)
    state = SimpleNamespace(config=None, tokenizer=None, metadata=None, heads=[], downloads=[])

    def download(repo_id: str, filename: str, *, revision: str | None, local_files_only: bool) -> Path | None:
        state.downloads.append((filename, revision, local_files_only))
        data = state.config if filename == "config.json" else state.tokenizer
        if data is None:
            return None
        path = tmp_path / filename
        path.write_bytes(data)
        return path

    def head(url: str, **kwargs: Any) -> Any:
        state.heads.append(url)
        if isinstance(state.metadata, Exception):
            raise state.metadata
        return state.metadata

    monkeypatch.setattr(identity, "_hub_download", download)
    monkeypatch.setattr("huggingface_hub.get_hf_file_metadata", head)
    return state


def metadata(size: Any, etag: Any, commit: str | None = HEAD_COMMIT, **kwargs: Any) -> SimpleNamespace:
    return SimpleNamespace(size=size, etag=etag, commit_hash=commit, **kwargs)


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("storage", ["lfs", "git"])
def test_supported_forms(hub: SimpleNamespace, form_bytes: dict[str, bytes], form: str, storage: str) -> None:
    size, blob, digest = FORMS[form]
    hub.tokenizer = form_bytes[form]
    hub.metadata = metadata(size, digest if storage == "lfs" else blob)
    assert identity.is_deepseek_v4_tokenizer_source("acme/upload", revision=BRANCH)
    assert len(hub.heads) == 1 and f"resolve/{BRANCH}/" in hub.heads[0]
    assert hub.downloads[1:] == ([] if storage == "lfs" else [("tokenizer.json", HEAD_COMMIT, False)])


@pytest.mark.parametrize("size,etag", [(FORMS["hub"][0], "f" * 40), (FORMS["hub"][0], "e" * 64), (123_456, "f" * 40)])
def test_proven_mismatch_avoids_byte_read(hub: SimpleNamespace, size: int, etag: str) -> None:
    hub.metadata = metadata(size, etag)
    assert not identity.is_deepseek_v4_tokenizer_source("acme/unrelated")
    assert hub.downloads == [("config.json", None, False)]


@pytest.mark.parametrize(
    "size,etag",
    [
        (FORMS["hub"][0], "not-an-etag"),
        (None, None),
        (999, FORMS["hub"][1]),
        (999, FORMS["hub"][2]),
        ("6367146", "f" * 40),
        (True, "f" * 40),
        (6_367_146.0, "f" * 40),
        ([6_367_146], "f" * 40),
        (6_367_146, [FORMS["hub"][2]]),
        (6_367_146, True),
        (6_367_146, 12345),
        (1, "weird/scheme"),
        (1, None),
    ],
)
def test_ambiguous_metadata_defers_to_bytes(
    hub: SimpleNamespace, form_bytes: dict[str, bytes], size: Any, etag: Any
) -> None:
    hub.metadata = metadata(size, etag)
    hub.tokenizer = form_bytes["hub"]
    assert identity.is_deepseek_v4_tokenizer_source("acme/upload", revision=BRANCH)
    assert hub.downloads[-1] == ("tokenizer.json", HEAD_COMMIT, False)


@pytest.mark.parametrize("etag", ["e" * 64, FORMS["hub"][2]])
@pytest.mark.parametrize("commit", [None, "not-a-commit"])
def test_unpinned_metadata_cannot_accept_or_reject(
    hub: SimpleNamespace, form_bytes: dict[str, bytes], etag: str, commit: str | None
) -> None:
    hub.metadata = metadata(FORMS["hub"][0], etag, commit)
    hub.tokenizer = form_bytes["hub"]
    assert identity.is_deepseek_v4_tokenizer_source("acme/upload", revision=BRANCH)
    assert hub.downloads[-1] == ("tokenizer.json", BRANCH, False)


@pytest.mark.parametrize(
    "error,has_bytes,expected,reads",
    [
        (EntryNotFoundError("404"), False, False, 0),
        (ConnectionError("offline"), True, True, 1),
        (OfflineModeIsEnabled("offline"), False, False, 1),
    ],
)
def test_head_errors_preserve_byte_fallback(
    hub: SimpleNamespace, form_bytes: dict[str, bytes], error: Exception, has_bytes: bool, expected: bool, reads: int
) -> None:
    hub.metadata = error
    hub.tokenizer = form_bytes["hub"] if has_bytes else None
    assert identity.is_deepseek_v4_tokenizer_source("acme/upload", revision=BRANCH) is expected
    assert hub.downloads[1:] == ([("tokenizer.json", BRANCH, False)] if reads else [])


@pytest.mark.parametrize("official_bytes", [False, True])
def test_custom_endpoint_ignores_metadata(
    monkeypatch: pytest.MonkeyPatch, hub: SimpleNamespace, form_bytes: dict[str, bytes], official_bytes: bool
) -> None:
    monkeypatch.setattr(constants, "ENDPOINT", "https://mirror.example.com")
    hub.metadata = metadata(1, "0" * 64) if official_bytes else metadata(FORMS["hub"][0], FORMS["hub"][2])
    hub.tokenizer = form_bytes["hub"] if official_bytes else b"random"
    assert identity.is_deepseek_v4_tokenizer_source("acme/upload") is official_bytes
    assert hub.heads == []
    assert hub.downloads[-1] == ("tokenizer.json", None, False)


@pytest.mark.parametrize("global_offline", [False, True])
def test_offline_never_heads(
    monkeypatch: pytest.MonkeyPatch, hub: SimpleNamespace, form_bytes: dict[str, bytes], global_offline: bool
) -> None:
    monkeypatch.setattr(constants, "HF_HUB_OFFLINE", global_offline)
    hub.tokenizer = form_bytes["hub"]
    assert identity.is_deepseek_v4_tokenizer_source("acme/upload", local_files_only=not global_offline)
    assert hub.heads == []
    assert hub.downloads[-1] == ("tokenizer.json", None, not global_offline)


@pytest.mark.parametrize("model_type,expected", [("deepseek_v4", True), ("qwen3", False)])
def test_explicit_family_short_circuits(hub: SimpleNamespace, model_type: str, expected: bool) -> None:
    hub.config = json.dumps({"model_type": model_type}).encode()
    assert identity.is_deepseek_v4_tokenizer_source("acme/upload") is expected
    assert hub.heads == []
    assert hub.downloads == [("config.json", None, False)]


@pytest.mark.parametrize(
    "etag,xet_hash,expected,reads",
    [
        (FORMS["hub"][2], "6aec3963" + "0" * 56, True, 0),
        ("e" * 64, FORMS["hub"][2], False, 0),
        (None, FORMS["hub"][2], True, 1),
    ],
)
def test_only_linked_etag_establishes_xet_identity(
    hub: SimpleNamespace, form_bytes: dict[str, bytes], etag: str | None, xet_hash: str, expected: bool, reads: int
) -> None:
    hub.metadata = metadata(FORMS["hub"][0], etag, xet_file_data=SimpleNamespace(file_hash=xet_hash))
    hub.tokenizer = form_bytes["hub"]
    assert identity.is_deepseek_v4_tokenizer_source("acme/upload") is expected
    assert len(hub.downloads[1:]) == reads


def test_unrecognized_bytes_do_not_gain_identity(hub: SimpleNamespace) -> None:
    hub.metadata = metadata(None, None)
    hub.tokenizer = b"not an official tokenizer"
    assert not identity.is_deepseek_v4_tokenizer_source("acme/upload")


def test_local_and_canonical_sources_do_not_use_hub(
    hub: SimpleNamespace, tmp_path: Path, form_bytes: dict[str, bytes]
) -> None:
    directory = tmp_path / "local"
    directory.mkdir()
    for data, expected in [(form_bytes["hub"], True), (b"tampered", False)]:
        (directory / "tokenizer.json").write_bytes(data)
        assert identity.is_deepseek_v4_tokenizer_source(str(directory)) is expected
    for source in identity.DEEPSEEK_V4_REPOSITORIES:
        assert identity.is_deepseek_v4_tokenizer_source(source)
    assert hub.heads == hub.downloads == []
