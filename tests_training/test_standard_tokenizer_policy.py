"""Restrictive context and literal JSON loading; no Hub or checkpoint Python."""

from __future__ import annotations

import json
import importlib
from typing import Any
from pathlib import Path

import pytest
import tokenizers
import transformers

from fireworks.training.sdk import tokenizer_identity as identity
from fireworks.training.sdk.client import FiretitanTrainingClient
from fireworks.training.sdk._core.lib.public_interfaces import sampling_client

CONTEXTS = [
    "Qwen/Qwen3.8-27B",
    "google/gemma-4-31B-it",
    "MiniMaxAI/MiniMax-M3",
    "nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16",
    "nvidia/Llama-3.1-Nemotron-70B-Instruct",
    "accounts/fireworks/models/llama-v3p1-nemotron-70b-instruct",
]
OVERRIDES = ["acme/override", "moonshotai/Kimi-K2.5", "moonshotai/Kimi-K2.6", "moonshotai/Kimi-K2-Thinking"]


def load(reader: str, model: str, source: str) -> Any:
    if reader == "sampling":
        return sampling_client._load_tokenizer_from_model_info(model, source)
    client = FiretitanTrainingClient.__new__(FiretitanTrainingClient)
    client._tokenizer_model = source
    client._tokenizer_base_model = model
    return client.get_tokenizer()


@pytest.fixture(autouse=True)
def clear_tokenizer_cache() -> Any:
    sampling_client._load_tokenizer_from_model_info.cache_clear()
    yield
    sampling_client._load_tokenizer_from_model_info.cache_clear()


@pytest.mark.parametrize("context", CONTEXTS)
@pytest.mark.parametrize("override", OVERRIDES)
@pytest.mark.parametrize("reader", ["sampling", "training"])
def test_independent_model_context_overrides_k2_opt_in(
    monkeypatch: pytest.MonkeyPatch, context: str, override: str, reader: str
) -> None:
    calls: list[dict[str, Any]] = []
    monkeypatch.setattr(sampling_client, "is_kimi_k3_k31_tokenizer_source", lambda *_a, **_k: False)
    monkeypatch.setattr(sampling_client, "requires_code_free_tokenizer_loading", lambda *_a, **_k: False)
    monkeypatch.setattr(transformers.AutoTokenizer, "from_pretrained", lambda *_a, **k: calls.append(k) or object())
    monkeypatch.setenv("HF_TRUST_REMOTE_CODE", "true")
    load(reader, context, override)
    assert len(calls) == 1 and calls[0]["trust_remote_code"] is False


def test_independent_architecture_is_restrictive(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict[str, Any]] = []
    monkeypatch.setattr(sampling_client, "is_kimi_k3_k31_tokenizer_source", lambda *_a, **_k: False)
    monkeypatch.setattr(sampling_client, "requires_code_free_tokenizer_loading", lambda *_a, **_k: False)
    monkeypatch.setattr(transformers.AutoTokenizer, "from_pretrained", lambda *_a, **k: calls.append(k) or object())
    sampling_client._load_tokenizer_from_model_info(
        "acme/deployed", "moonshotai/Kimi-K2.6", model_arch="Qwen3ForCausalLM"
    )
    assert calls[0]["trust_remote_code"] is False


@pytest.mark.parametrize("override", OVERRIDES[1:])
def test_unrelated_model_keeps_legacy_k2_policy(monkeypatch: pytest.MonkeyPatch, override: str) -> None:
    calls: list[dict[str, Any]] = []
    monkeypatch.setattr(sampling_client, "is_kimi_k3_k31_tokenizer_source", lambda *_a, **_k: False)
    monkeypatch.setattr(sampling_client, "requires_code_free_tokenizer_loading", lambda *_a, **_k: False)
    monkeypatch.setattr(transformers.AutoTokenizer, "from_pretrained", lambda *_a, **k: calls.append(k) or object())
    sampling_client._load_tokenizer_from_model_info("acme/unrelated", override)
    assert calls[0]["trust_remote_code"] is True and calls[0]["revision"]


@pytest.mark.parametrize("model", ["moonshotai/Kimi-K3", "moonshotai/Kimi-K3.1-Pro"])
@pytest.mark.parametrize("reader", ["sampling", "training"])
def test_selected_k3_context_keeps_native_dispatch(monkeypatch: pytest.MonkeyPatch, model: str, reader: str) -> None:
    # lazy: exercise native dispatch without loading tokenizer data or checkpoint code.
    from fireworks.training.sdk import kimi_native_tokenizer

    sentinel = object()
    monkeypatch.setattr(kimi_native_tokenizer, "load_native_tokenizer", lambda *_a, **_k: sentinel)
    assert load(reader, model, "Qwen/Qwen3-8B") is sentinel


@pytest.mark.parametrize(
    "name",
    [
        None,
        "",
        "acme/not-qwen3",
        "gemmalike",
        "moonshotai/Kimi-K2.6",
        "acme/Llama-3.1-Nemotron-70B-Instruct",
        "/tmp/Llama-3.1-Nemotron-70B-Instruct",
        "nvidia/Llama-3.1-Nemotron-70B-Instruct-extra",
    ],
)
def test_unrelated_names_do_not_claim_standard_context(name: str | None) -> None:
    assert not identity.is_standard_tokenizer_model_name(name)


@pytest.mark.parametrize("context", CONTEXTS)
def test_standard_context_never_uses_basename_or_substring(context: str) -> None:
    assert identity.is_standard_tokenizer_model_name(context)
    basename = context.rsplit("/", 1)[-1]
    for unknown in (f"acme/{basename}", f"/tmp/{basename}", f"{context}-unreviewed", f"prefix/{context}"):
        assert not identity.is_standard_tokenizer_model_name(unknown), unknown


@pytest.mark.parametrize("dirname", ["opaque", "Qwen3-8B", "MiniMax-M2", "gemma-4-31B-it", "Nemotron-3-Super"])
def test_local_standard_policy_depends_on_data_not_folder(tmp_path: Path, dirname: str) -> None:
    root = tmp_path / dirname
    root.mkdir()
    assert not identity.is_standard_tokenizer_model_name(str(root))
    (root / "config.json").write_text(json.dumps({"model_type": "llama"}))
    assert not identity.is_standard_tokenizer_model_name(str(root))
    (root / "config.json").write_text(json.dumps({"model_type": "qwen3"}))
    assert identity.is_standard_tokenizer_model_name(str(root))
    (root / "config.json").write_text("{")
    assert not identity.is_standard_tokenizer_model_name(str(root))


@pytest.mark.parametrize("name", ["acme/MiniMax-M2", "/tmp/MiniMax-M2", "MiniMaxAI/MiniMax-M2-extra"])
def test_minimax_reader_selection_is_exact_not_basename(name: str) -> None:
    assert not identity.is_minimax_m2_model_name(name)


@pytest.mark.parametrize("name", ["MiniMaxAI/MiniMax-M2.5", "accounts/fireworks/models/minimax-m2p5", "minimax_m2"])
def test_local_directory_precedes_exact_minimax_context(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, name: str
) -> None:
    monkeypatch.chdir(tmp_path)
    root = tmp_path / name
    root.mkdir(parents=True)
    for metadata in ({}, {"model_type": "qwen3"}, {"model_type": "minimax_m2"}):
        (root / "config.json").write_text(json.dumps(metadata))
        expected = metadata.get("model_type") == "minimax_m2"
        for source in (name, str(root)):
            assert identity.is_minimax_m2_model_name(source) is expected
            assert identity.is_minimax_m2_tokenizer_source(source) is expected


@pytest.mark.parametrize(
    "name",
    [
        "MiniMaxAI/MiniMax-M2.1",
        "MiniMaxAI/MiniMax-M2.7",
        "accounts/fireworks/models/minimax-m2p1",
        "accounts/fireworks/models/minimax-m2p7",
    ],
)
def test_additional_reviewed_minimax_context_is_exact(name: str) -> None:
    assert identity.is_minimax_m2_model_name(name)
    assert identity.is_minimax_m2_tokenizer_source(name)


@pytest.mark.parametrize("override", ["MiniMaxAI/MiniMax-M2.5", "acme/opaque", "moonshotai/Kimi-K2.6"])
@pytest.mark.parametrize("reader", ["sampling", "training"])
def test_minimax_without_optional_backend_keeps_generic_false_and_override(
    monkeypatch: pytest.MonkeyPatch, override: str, reader: str
) -> None:
    transformers = importlib.import_module("transformers")
    monkeypatch.setenv("HF_TRUST_REMOTE_CODE", "true")
    monkeypatch.setattr(sampling_client, "is_kimi_k3_k31_tokenizer_source", lambda *_a, **_k: False)
    monkeypatch.setattr(sampling_client, "requires_code_free_tokenizer_loading", lambda *_a, **_k: False)
    # Simulate an older installed runtime without this optional exported capability.
    monkeypatch.setattr(transformers, "TokenizersBackend", None)
    calls: list[tuple[tuple[Any, ...], dict[str, Any]]] = []
    sentinel = object()
    monkeypatch.setattr(transformers.AutoTokenizer, "from_pretrained", lambda *a, **k: calls.append((a, k)) or sentinel)

    def reject(*_a: Any, **_k: Any) -> None:
        raise AssertionError("missing-backend fallback must not add metadata reads")

    monkeypatch.setattr(transformers.models.auto.tokenization_auto, "get_tokenizer_config", reject)
    assert load(reader, "MiniMaxAI/MiniMax-M2.5", override) is sentinel
    expected: dict[str, Any] = {"trust_remote_code": False}
    if reader == "sampling":
        expected["fast"] = True
    if reader == "sampling" and override == "moonshotai/Kimi-K2.6":
        expected["revision"] = "b5aabbfb20227ed42becbf5541dbffd213942c58"
    assert calls == [((override,), expected)]


@pytest.mark.parametrize("model", [None, "MiniMaxAI/MiniMax-M2", "MiniMaxAI/MiniMax-M2.5"])
@pytest.mark.parametrize("add_bos,add_eos", [(False, False), (True, False), (False, True), (True, True)])
@pytest.mark.parametrize("reader", ["sampling", "training"])
def test_minimax_preserves_literal_ids_flags_and_saved_readers(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, model: str | None, add_bos: bool, add_eos: bool, reader: str
) -> None:
    backend = tokenizers.Tokenizer(
        tokenizers.models.WordLevel({"[UNK]": 0, "<s>": 1, "</s>": 2, "a": 3, "b": 4}, unk_token="[UNK]")
    )
    backend.pre_tokenizer = tokenizers.pre_tokenizers.WhitespaceSplit()
    backend.save(str(tmp_path / "tokenizer.json"))
    (tmp_path / "config.json").write_text(json.dumps({"model_type": "minimax_m2"}))
    (tmp_path / "tokenizer_config.json").write_text(
        json.dumps(
            {
                "tokenizer_class": "GPT2Tokenizer",
                "auto_map": {"AutoTokenizer": ["poison.Bad", None]},
                "bos_token": "<s>",
                "eos_token": "</s>",
                "add_bos_token": add_bos,
                "add_eos_token": add_eos,
            }
        )
    )
    (tmp_path / "poison.py").write_text("raise AssertionError('checkpoint Python executed')\n")

    def reject(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("checkpoint code requested")

    monkeypatch.setattr(transformers.dynamic_module_utils, "get_class_from_dynamic_module", reject)
    loaded = load(reader, model or str(tmp_path), str(tmp_path))
    expected = ([1] if add_bos else []) + [3, 4, 4] + ([2] if add_eos else [])
    assert loaded.encode("a\n\nb\tb", add_special_tokens=False) == [3, 4, 4]
    assert loaded.encode("a\n\nb\tb") == expected
    saved = tmp_path / "saved"
    loaded.save_pretrained(saved)
    assert "auto_map" not in json.loads((saved / "tokenizer_config.json").read_text())
    for restored in (
        load(reader, model or str(saved), str(saved)),
        transformers.AutoTokenizer.from_pretrained(saved, trust_remote_code=False, local_files_only=True),
    ):
        assert restored.encode("a\n\nb\tb") == expected
        assert restored.all_special_ids == loaded.all_special_ids
