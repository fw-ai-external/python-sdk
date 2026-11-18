"""Installed tokenizer compatibility without checkpoint Python or a service."""

from __future__ import annotations

import os
import sys
import json
import hashlib
import inspect
import subprocess
from typing import Any
from pathlib import Path

import pytest
import tokenizers
import transformers

from fireworks.training.sdk import tokenizer_compat
from fireworks.training.sdk.client import FiretitanTrainingClient
from fireworks.training.sdk._core.lib.public_interfaces import sampling_client

backend_module = pytest.importorskip("transformers.tokenization_utils_tokenizers")
TokenizersBackend = backend_module.TokenizersBackend


@pytest.fixture(autouse=True)
def isolated_backport(monkeypatch: pytest.MonkeyPatch) -> Any:
    monkeypatch.setattr(TokenizersBackend, "__init__", inspect.unwrap(TokenizersBackend.__init__))
    patch = TokenizersBackend.__dict__["_patch_mistral_regex"].__func__
    monkeypatch.setattr(TokenizersBackend, "_patch_mistral_regex", classmethod(inspect.unwrap(patch)))
    sampling_client._load_tokenizer_from_model_info.cache_clear()
    yield
    sampling_client._load_tokenizer_from_model_info.cache_clear()


def write_tokenizer(path: Path, fix: bool | None) -> None:
    backend = tokenizers.Tokenizer(tokenizers.models.WordLevel({"[UNK]": 0, "hello": 1}, unk_token="[UNK]"))
    backend.pre_tokenizer = tokenizers.pre_tokenizers.WhitespaceSplit()
    backend.save(str(path / "tokenizer.json"))
    # A literal WordLevel fixture is generic, not a Qwen2 BPE checkpoint.
    config: dict[str, Any] = {"tokenizer_class": "PreTrainedTokenizerFast", "unk_token": "[UNK]"}
    if fix is not None:
        config["fix_mistral_regex"] = fix
    (path / "tokenizer_config.json").write_text(json.dumps(config))


def load(reader: str, path: Path) -> Any:
    if reader == "model-info":
        return sampling_client._load_tokenizer_from_model_info("acme/example", str(path))
    client = object.__new__(FiretitanTrainingClient)
    client._tokenizer_model = str(path)
    return client.get_tokenizer()


@pytest.mark.parametrize("reader", ["model-info", "managed-training"])
@pytest.mark.parametrize("fix", [None, False, True])
def test_actual_sdk_loaders_preserve_flag_and_save(tmp_path: Path, reader: str, fix: bool | None) -> None:
    write_tokenizer(tmp_path, fix)
    loaded = load(reader, tmp_path)
    assert type(loaded.backend_tokenizer.model).__name__ == "WordLevel"
    assert tokenizers.Tokenizer.from_file(str(tmp_path / "tokenizer.json")).encode("hello\nhello").ids == [1, 1]
    assert loaded.encode("hello\nhello", add_special_tokens=False) == [1, 1]
    if fix is not None:
        assert loaded.init_kwargs["fix_mistral_regex"] is fix
    saved = tmp_path / "saved"
    loaded.save_pretrained(saved)
    if fix is not None:
        assert json.loads((saved / "tokenizer_config.json").read_text())["fix_mistral_regex"] is fix
    for restored in (
        load(reader, saved),
        transformers.AutoTokenizer.from_pretrained(saved, trust_remote_code=False, local_files_only=True),
    ):
        assert restored.encode("hello\nhello", add_special_tokens=False) == [1, 1]
        assert restored.all_special_ids == loaded.all_special_ids
        if fix is not None:
            assert restored.init_kwargs["fix_mistral_regex"] is fix


def test_backport_is_idempotent() -> None:
    tokenizer_compat.patch_duplicate_mistral_regex_kwarg()
    first = TokenizersBackend.__init__
    patch = TokenizersBackend.__dict__["_patch_mistral_regex"].__func__
    tokenizer_compat.patch_duplicate_mistral_regex_kwarg()
    assert TokenizersBackend.__init__ is first
    assert TokenizersBackend.__dict__["_patch_mistral_regex"].__func__ is patch


@pytest.mark.parametrize("version", ["4.57.6", "5.4.0", "6.0.0"])
def test_version_guard_is_noop_outside_affected_range(monkeypatch: pytest.MonkeyPatch, version: str) -> None:
    monkeypatch.setattr(transformers, "__version__", version)
    original = TokenizersBackend.__init__
    patch = TokenizersBackend.__dict__["_patch_mistral_regex"].__func__
    tokenizer_compat.patch_duplicate_mistral_regex_kwarg()
    assert TokenizersBackend.__init__ is original
    assert TokenizersBackend.__dict__["_patch_mistral_regex"].__func__ is patch


def test_transport_import_does_not_require_transformers() -> None:
    code = """
import builtins
from typing import Any
original = builtins.__import__
def guarded(name: str, *args: Any, **kwargs: Any) -> Any:
    if name == "transformers" or name.startswith("transformers."):
        raise ImportError("optional tokenizer dependency blocked")
    return original(name, *args, **kwargs)
builtins.__import__ = guarded
import fireworks.training.sdk.client
import fireworks.training.sdk._core.lib.public_interfaces.sampling_client
"""
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=30, check=False)
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("reader", ["model-info", "managed-training"])
@pytest.mark.parametrize("precision", ["bf16", "nvfp4"])
def test_retained_supervl_data_ids_flag_and_reload(tmp_path: Path, reader: str, precision: str) -> None:
    fixture_root = os.environ.get("FIREWORKS_TOKENIZER_COMPAT_FIXTURES")
    if fixture_root is None:
        pytest.skip("set FIREWORKS_TOKENIZER_COMPAT_FIXTURES to the retained pinned data directory")
    source = Path(fixture_root) / f"nvidia-nvidia-nemotron-3-5-super-vl-120b-a12b-{precision}"
    assert hashlib.sha256((source / "tokenizer.json").read_bytes()).hexdigest() == (
        "d0432ad8b1c2984a2e2dca82e1933e3fd5628df6e95c51fba4c3ee9950dce299"
    )
    assert hashlib.sha256((source / "tokenizer_config.json").read_bytes()).hexdigest() == (
        "89fa70d31734c0c75ffdcee4114449f8cf8abd64bc233d420b58e25763f91aba"
    )
    oracle = tokenizers.Tokenizer.from_file(str(source / "tokenizer.json"))
    loaded = load(reader, source)
    saved = tmp_path / "saved"
    loaded.save_pretrained(saved)
    for restored in (
        loaded,
        load(reader, saved),
        transformers.AutoTokenizer.from_pretrained(saved, trust_remote_code=False, local_files_only=True),
    ):
        assert restored.init_kwargs["fix_mistral_regex"] is True
        for text in ("hello世界🙂", "a\n\nb\tc", "x" * 25005, "<think>reason</think>"):
            assert restored.encode(text, add_special_tokens=False) == oracle.encode(text, add_special_tokens=False).ids
        assert restored.all_special_ids == loaded.all_special_ids
        assert restored.chat_template == loaded.chat_template
