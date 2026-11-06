"""Unit tests for fireworks.training.sdk.tokenizer_identity (local only)."""

from __future__ import annotations

import json
import hashlib
from typing import Any
from pathlib import Path

import pytest

from fireworks.training.sdk import tokenizer_identity as identity


def test_reviewed_hub_sources_cannot_fail_open_on_metadata_fetch(monkeypatch):
    def unavailable(*_args, **_kwargs):
        raise AssertionError("known migrated Hub sources must not need advisory reads")

    monkeypatch.setattr(identity, "_hub_download", unavailable)
    for source in identity.DEEPSEEK_V4_REPOSITORIES:
        assert identity.is_deepseek_v4_tokenizer_source(source)


def test_empty_and_missing_inputs_are_not_recognized() -> None:
    assert identity.is_deepseek_v4_tokenizer_source(None) is False
    assert identity.is_deepseek_v4_tokenizer_source("") is False
    assert identity.is_deepseek_v4_tokenizer_source("/nonexistent/path/xyz") is False


def test_config_model_type_branch(tmp_path: Path) -> None:
    (tmp_path / "config.json").write_text(json.dumps({"model_type": "deepseek_v4"}))
    assert identity.is_deepseek_v4_tokenizer_source(str(tmp_path)) is True


def test_other_model_type_is_not_recognized(tmp_path: Path) -> None:
    (tmp_path / "config.json").write_text(json.dumps({"model_type": "qwen3"}))
    assert identity.is_deepseek_v4_tokenizer_source(str(tmp_path)) is False


@pytest.mark.parametrize("model_type", ["qwen3", "llama", "new_model_family"])
def test_explicit_other_model_type_precedes_shared_digest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, model_type: str
) -> None:
    """Shared tokenizer bytes must not change an explicitly selected family."""
    (tmp_path / "config.json").write_text(json.dumps({"model_type": model_type}))
    tokenizer_json = tmp_path / "tokenizer.json"
    tokenizer_json.write_bytes(b"canonical tokenizer bytes")
    digest = hashlib.sha256(tokenizer_json.read_bytes()).hexdigest()
    monkeypatch.setattr(
        identity,
        "DEEPSEEK_V4_TOKENIZER_JSON_SHA256",
        frozenset({digest}),
    )
    assert identity.is_deepseek_v4_tokenizer_source(str(tmp_path)) is False


def test_local_directory_name_may_contain_a_colon(tmp_path: Path) -> None:
    colon_dir = tmp_path / "staging:run-7"
    colon_dir.mkdir()
    (colon_dir / "config.json").write_text(json.dumps({"model_type": "deepseek_v4"}))
    assert identity.is_deepseek_v4_tokenizer_source(str(colon_dir)) is True


def test_config_without_model_type_falls_through_to_digest(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "config.json").write_text(json.dumps({"architectures": ["X"]}))
    tokenizer_json = tmp_path / "tokenizer.json"
    tokenizer_json.write_bytes(b"tokenizer bytes")
    digest = hashlib.sha256(tokenizer_json.read_bytes()).hexdigest()
    monkeypatch.setattr(
        identity,
        "DEEPSEEK_V4_TOKENIZER_JSON_SHA256",
        frozenset({digest}),
    )
    assert identity.is_deepseek_v4_tokenizer_source(str(tmp_path)) is True


def test_configless_digest_branch(tmp_path: Path, monkeypatch) -> None:
    tokenizer_json = tmp_path / "tokenizer.json"
    tokenizer_json.write_bytes(b"tokenizer bytes")
    digest = hashlib.sha256(tokenizer_json.read_bytes()).hexdigest()
    monkeypatch.setattr(
        identity,
        "DEEPSEEK_V4_TOKENIZER_JSON_SHA256",
        frozenset({digest}),
    )
    assert identity.is_deepseek_v4_tokenizer_source(str(tmp_path)) is True
    tokenizer_json.write_bytes(b"different bytes")
    assert identity.is_deepseek_v4_tokenizer_source(str(tmp_path)) is False


def test_unreadable_config_is_not_an_error(tmp_path: Path) -> None:
    (tmp_path / "config.json").write_text("{ not json")
    assert identity.is_deepseek_v4_tokenizer_source(str(tmp_path)) is False


def test_missing_tokenizer_json_is_not_recognized(tmp_path: Path) -> None:
    assert identity.is_deepseek_v4_tokenizer_source(str(tmp_path)) is False


def test_same_artifact_renamed_has_same_decision(tmp_path: Path) -> None:
    """Directory names never contribute identity: the same artifact keeps the
    decision its data earns under every name."""
    for name in ("totally-unrelated-name", "DeepSeek-V4-clone", "deepseek-v4.1-flash"):
        directory = tmp_path / name
        directory.mkdir()
        (directory / "config.json").write_text(json.dumps({"model_type": "deepseek_v4"}))
        assert identity.is_deepseek_v4_tokenizer_source(str(directory)) is True, name
        (directory / "config.json").write_text(json.dumps({"model_type": "qwen3"}))
        assert identity.is_deepseek_v4_tokenizer_source(str(directory)) is False, name


def test_absent_metadata_renamed_v4_does_not_gain_identity(tmp_path: Path) -> None:
    """An empty directory carrying a canonical-looking name is not recognized:
    local artifact identity comes from data, never from basenames."""
    for name in ("DeepSeek-V4-Pro-0813", "deepseek-v4-flash-0731", "deepseek_v4"):
        directory = tmp_path / name
        directory.mkdir()
        assert identity.is_deepseek_v4_tokenizer_source(str(directory)) is False, name


# ---------------------------------------------------------------------------
# SDK-owned sampling helper dispatch (runs only against the current SDK)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def official_v4_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    hub = pytest.importorskip("huggingface_hub")
    transformers = pytest.importorskip("transformers")
    del transformers
    root = tmp_path_factory.mktemp("dsv4-official")
    for filename in ("config.json", "tokenizer.json", "tokenizer_config.json"):
        local = hub.hf_hub_download(
            "deepseek-ai/DeepSeek-V4-Flash-0731",
            filename,
            revision="7872f01b1d1fe23eabc4c98b48bffcef5a386062",
        )
        (root / filename).write_bytes(Path(local).read_bytes())
    return root


@pytest.mark.parametrize("model_type", ["deepseek_v41", "qwen3", "llama", "new_model_family"])
def test_explicit_other_family_excludes_shared_v4_tokenizer_digest(
    official_v4_dir: Path, tmp_path: Path, model_type: str
) -> None:
    (tmp_path / "config.json").write_text(json.dumps({"model_type": model_type}))
    (tmp_path / "tokenizer.json").write_bytes((official_v4_dir / "tokenizer.json").read_bytes())
    assert not identity.is_deepseek_v4_tokenizer_source(str(tmp_path))
    assert identity.requires_code_free_tokenizer_loading(str(tmp_path))


@pytest.mark.parametrize("model_type", ["deepseek_v41", "qwen3", "llama", "new_model_family"])
def test_explicit_other_hub_config_excludes_shared_v4_digest(
    official_v4_dir: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, model_type: str
) -> None:
    config = tmp_path / "config.json"
    config.write_text(json.dumps({"model_type": model_type}))
    monkeypatch.setattr(identity, "_hub_download", lambda *_args, **_kwargs: config)

    def unexpected_digest_read(*_args: Any, **_kwargs: Any) -> bool:
        raise AssertionError("an explicit other family must not fall through to shared tokenizer bytes")

    monkeypatch.setattr(identity, "_hub_tokenizer_json_matches", unexpected_digest_read)
    assert not identity.is_deepseek_v4_tokenizer_source("acme/shared-tokenizer")
    monkeypatch.setattr(identity, "_hub_tokenizer_json_matches", lambda *_args, **_kwargs: True)
    assert identity.requires_code_free_tokenizer_loading("acme/shared-tokenizer")


_ENCODE_BATTERY = [
    "Hello world",
    "DeepSeek V4 tokenizer parity check",
    "unicode battery: café 漢字 ☃",
    "<think>reasoning</think>answer",
    " ".join(f"tok{i}" for i in range(512)),
]


def test_sampling_helper_forces_code_free_for_recognized_v4(
    monkeypatch: pytest.MonkeyPatch, official_v4_dir: Path
) -> None:
    """The SDK sampling helper narrows to explicit False for recognized V4
    data and returns a tokenizer identical to an explicit-False load. This is
    new-SDK behavior and belongs to the SDK's own suite: historical SDK
    releases keep their existing sampling behavior, and no old wheel is
    claimed patched."""
    transformers = pytest.importorskip("transformers")
    from fireworks.training.sdk._core.lib.public_interfaces import sampling_client

    captured: dict[str, Any] = {}
    real_from_pretrained = transformers.AutoTokenizer.from_pretrained

    def spy(model: Any, **kwargs: Any) -> Any:
        captured.update(kwargs)
        return real_from_pretrained(model, **kwargs)

    monkeypatch.setattr(transformers.AutoTokenizer, "from_pretrained", spy)
    sampling_client._load_tokenizer_from_model_info.cache_clear()
    tokenizer = sampling_client._load_tokenizer_from_model_info(str(official_v4_dir))
    assert captured.get("trust_remote_code") is False

    reference = real_from_pretrained(str(official_v4_dir), trust_remote_code=False)
    assert type(tokenizer) is type(reference)
    assert tokenizer.special_tokens_map == reference.special_tokens_map
    assert getattr(tokenizer, "chat_template", None) == getattr(reference, "chat_template", None)
    for text in _ENCODE_BATTERY:
        assert tokenizer.encode(text) == reference.encode(text), text[:40]
        sample = tokenizer.encode(text)
        assert tokenizer.decode(sample) == reference.decode(sample), text[:40]


@pytest.fixture
def unidentified_v4_tokenizer(official_v4_dir: Path, tmp_path: Path):
    import transformers

    original = transformers.AutoTokenizer.from_pretrained(str(official_v4_dir), trust_remote_code=False)
    directory = tmp_path / "unidentified"
    original.save_pretrained(directory)
    data = directory / "tokenizer.json"
    data.write_text(json.dumps(json.loads(data.read_text()), indent=1))
    assert not identity.is_deepseek_v4_tokenizer_source(str(directory))
    marker = tmp_path / "sdk_canary_executed"
    config_path = directory / "tokenizer_config.json"
    config = json.loads(config_path.read_text())
    config["auto_map"] = {"AutoTokenizer": [None, "sdk_canary.CanaryTokenizer"]}
    config_path.write_text(json.dumps(config))
    (directory / "sdk_canary.py").write_text(
        "from pathlib import Path\n"
        f"Path({str(marker)!r}).write_text('executed')\n"
        "from transformers import PreTrainedTokenizerFast\n"
        "class CanaryTokenizer(PreTrainedTokenizerFast):\n    pass\n"
    )
    return directory, original, marker


def _assert_tokenizer_equal(left, right):
    assert type(left) is type(right)
    assert left.special_tokens_map == right.special_tokens_map
    for text in _ENCODE_BATTERY:
        assert left.encode(text) == right.encode(text)
        assert left.decode(left.encode(text)) == right.decode(right.encode(text))


@pytest.mark.parametrize("model_type", ["deepseek_v41", "qwen3", "llama", "new_model_family"])
@pytest.mark.parametrize("boundary", ["client", "core"])
def test_reviewed_shared_bytes_block_sdk_checkpoint_code(
    official_v4_dir: Path,
    unidentified_v4_tokenizer,
    model_type: str,
    boundary: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # lazy: Transformers is an optional SDK dependency, supplied by the fixture.
    import transformers

    # lazy: exercise these SDK boundaries only after the optional Transformers fixture succeeds.
    from fireworks.training.sdk.client import FiretitanTrainingClient
    from fireworks.training.sdk._core.lib.public_interfaces import sampling_client

    directory, original, marker = unidentified_v4_tokenizer
    (directory / "tokenizer.json").write_bytes((official_v4_dir / "tokenizer.json").read_bytes())
    (directory / "config.json").write_text(json.dumps({"model_type": model_type}))
    assert not identity.is_deepseek_v4_tokenizer_source(str(directory))
    real_from_pretrained = transformers.AutoTokenizer.from_pretrained
    policies: list[bool | None] = []

    def load(model: Any, **kwargs: Any) -> Any:
        policies.append(kwargs.get("trust_remote_code"))
        return real_from_pretrained(model, **kwargs)

    monkeypatch.setattr(transformers.AutoTokenizer, "from_pretrained", load)
    if boundary == "client":
        client = FiretitanTrainingClient.__new__(FiretitanTrainingClient)
        client._tokenizer_model = str(directory)
        client._tokenizer_base_model = None
        tokenizer = client.get_tokenizer()
    else:
        sampling_client._load_tokenizer_from_model_info.cache_clear()
        tokenizer = sampling_client._load_tokenizer_from_model_info("unselected-model", str(directory))
    assert policies == [False]
    assert not marker.exists()
    _assert_tokenizer_equal(tokenizer, original)


@pytest.mark.parametrize("override", ["local", "kimi"])
def test_sdk_v4_model_context_cannot_lose_policy_on_tokenizer_override(
    unidentified_v4_tokenizer, monkeypatch, override
):
    """Synthetic Hub staging keeps the actual HF loader/code execution intact."""
    import transformers

    from fireworks.training.sdk._core.lib.public_interfaces import sampling_client

    directory, original, marker = unidentified_v4_tokenizer
    real_load = transformers.AutoTokenizer.from_pretrained
    policies = []

    def load(model, **kwargs):
        policies.append(kwargs.get("trust_remote_code"))
        # Redirect only the synthetic Hub fixture to task-owned data. The
        # production SDK policy and real HF dynamic module loader still run.
        return real_load(str(directory), **kwargs)

    monkeypatch.setattr(transformers.AutoTokenizer, "from_pretrained", load)
    sampling_client._load_tokenizer_from_model_info.cache_clear()
    error = None
    tokenizer = None
    try:
        tokenizer = sampling_client._load_tokenizer_from_model_info(
            "accounts/fireworks/models/deepseek-v4-flash-0731",
            str(directory) if override == "local" else "moonshotai/Kimi-K2.6",
        )
    except ValueError as exc:
        error = exc
    assert not marker.exists(), "Known V4 model cannot inherit another tokenizer's permissive policy"
    assert policies == [False], f"V4 requires explicit False, received {policies}; error={error}"
    assert error is None
    _assert_tokenizer_equal(tokenizer, original)


@pytest.mark.parametrize(
    "base_model,base_model_type",
    [
        ("accounts/fireworks/models/deepseek-v4-flash-0731", ""),
        ("accounts/customer/models/production-model", "deepseek_v4"),
    ],
)
def test_managed_training_client_retains_base_identity_for_tokenizer(
    unidentified_v4_tokenizer, monkeypatch, base_model, base_model_type
):
    from types import SimpleNamespace
    from unittest.mock import MagicMock

    import transformers

    from fireworks.training.sdk.client import FiretitanServiceClient, FiretitanTrainingClient

    directory, original, marker = unidentified_v4_tokenizer
    inner = object.__new__(FiretitanTrainingClient)
    inner_service = MagicMock()
    inner_service.create_training_client.return_value = inner
    handle = SimpleNamespace(service_client=inner_service, training_clients=[], sampler_backend=None)
    service = FiretitanServiceClient.from_firetitan_config(
        api_key="test-key",
        base_model=base_model,
        base_model_type=base_model_type,
        tokenizer_model=str(directory),
        max_lora_rank=32,
    )
    monkeypatch.setattr(service, "_ensure_managed_handle", lambda **_kwargs: handle)
    policies = []
    real_load = transformers.AutoTokenizer.from_pretrained

    def load(model, **kwargs):
        policies.append(kwargs.get("trust_remote_code"))
        return real_load(model, **kwargs)

    monkeypatch.setattr(transformers.AutoTokenizer, "from_pretrained", load)
    client = service.create_training_client(lora_rank=32)
    assert inner_service.create_training_client.call_args.kwargs["base_model"] == base_model
    error = None
    tokenizer = None
    try:
        tokenizer = client.get_tokenizer()
    except ValueError as exc:
        error = exc
    assert not marker.exists()
    assert policies == [False], f"managed base identity was lost; policy={policies}; error={error}"
    assert error is None
    _assert_tokenizer_equal(tokenizer, original)


@pytest.mark.parametrize(
    "model_name,expected",
    [
        (None, False),
        ("", False),
        # Reviewed canonical IDs: the digest-pinned HF repositories, the
        # SGLang FP8 mirrors, and the registry-onboarded Fireworks resource
        # IDs.
        ("deepseek-ai/DeepSeek-V4-Flash-0731", True),
        ("deepseek-ai/DeepSeek-V4-Pro-0813", True),
        ("deepseek-ai/deepseek-v4-flash", True),
        ("deepseek-ai/deepseek-v4-pro", True),
        ("sgl-project/deepseek-v4-flash-fp8", True),
        ("sgl-project/deepseek-v4-pro-fp8", True),
        ("accounts/fireworks/models/deepseek-v4-flash", True),
        ("accounts/fireworks/models/deepseek-v4-flash-0731", True),
        ("accounts/fireworks/models/deepseek-v4-pro", True),
        ("accounts/fireworks/models/deepseek-v4-flash-fp8", True),
        ("accounts/fireworks/models/deepseek-v4-pro-fp8", True),
        # Registry-style normalization: strip, trailing slashes, case.
        ("accounts/fireworks/models/deepseek-v4-flash-0731/", True),
        ("ACCOUNTS/FIREWORKS/MODELS/DEEPSEEK-V4-FLASH-0731", True),
        (" deepseek-ai/DeepSeek-V4-Flash-0731 ", True),
        # Substrings, basenames, ancestors, namespaces and forks never
        # contribute identity.
        ("accounts/team/models/renamed-production-model", False),
        ("accounts/fireworks/models/deepseek-v4-flash-0731/finetune-x", False),
        ("deepseek-ai/DeepSeek-V4-Flash-0731-fork", False),
        ("acme/DeepSeek-V4-Flash-0731", False),
        ("deepseekv4", False),
        ("prefixdeepseek-v4suffix", False),
        ("workspace/deepseek-v4-experiments/qwen3-8b", False),
        ("accounts/fireworks/models/deepseek-v4.1-flash/deepseek-v4-flash-0731", False),
        ("deepseek-v4.1-workspace/deepseek-v4-flash-0731", False),
        ("C:\\models\\deepseek-v4-flash-0731", False),
        # V4.1 stays outside the V4 set.
        ("deepseek-ai/DeepSeek-V4.1", False),
        ("deepseek-ai/DeepSeek-V4.1-Pro", False),
        ("accounts/fireworks/models/deepseek-v41", False),
        ("accounts/fireworks/models/deepseek-v4.1-flash", False),
        ("deepseek-v4p1", False),
        ("deepseek_v41", False),
        ("Qwen/Qwen3-8B", False),
        # The exact architecture string is independently selected context.
        ("deepseek_v4", True),
        ("DeepSeek_V4/", True),
    ],
)
def test_model_name_policy_exact_reviewed_ids(model_name, expected):
    assert identity.is_deepseek_v4_model_name(model_name) is expected


def test_model_type_sentinel_is_context_but_never_source_identity(monkeypatch) -> None:
    """``deepseek_v4`` (the exact model_type) is valid selected context, yet
    as a tokenizer SOURCE it is recognized only through data: with advisory
    reads unavailable it must not be recognized by the string alone."""
    assert identity.is_deepseek_v4_model_name(identity.DEEPSEEK_V4_MODEL_TYPE) is True

    reads = []

    def unavailable(repo_id, filename, **_kwargs):
        reads.append((repo_id, filename))
        return None

    monkeypatch.setattr(identity, "_hub_download", unavailable)
    monkeypatch.setattr(identity, "_hub_tokenizer_json_matches", lambda *_args, **_kwargs: False)
    assert identity.is_deepseek_v4_tokenizer_source("deepseek_v4") is False
    assert reads == [("deepseek_v4", "config.json")]


def test_core_training_tokenizer_uses_existing_architecture_metadata(unidentified_v4_tokenizer, monkeypatch):
    """An opaque model name can still constrain policy from get_info metadata."""
    import asyncio
    from types import SimpleNamespace
    from contextlib import contextmanager
    from concurrent.futures import Future

    import transformers

    from fireworks.training.sdk import types
    from fireworks.training.sdk._core.lib.public_interfaces import sampling_client, training_client

    directory, original, marker = unidentified_v4_tokenizer
    info = types.GetInfoResponse(
        model_id="test-model",
        model_data=types.ModelData(
            arch="DeepseekV4ForCausalLM", model_name="renamed-model", tokenizer_id=str(directory)
        ),
    )

    class Holder:
        @contextmanager
        def aclient(self, _pool):
            async def get_info(**kwargs):
                return info

            yield SimpleNamespace(models=SimpleNamespace(get_info=get_info))

        def run_coroutine_threadsafe(self, coroutine):
            result = Future()
            result.set_result(asyncio.run(coroutine))
            return result

    policies = []
    real_load = transformers.AutoTokenizer.from_pretrained

    def load(model, **kwargs):
        policies.append(kwargs.get("trust_remote_code"))
        return real_load(model, **kwargs)

    monkeypatch.setattr(transformers.AutoTokenizer, "from_pretrained", load)
    sampling_client._load_tokenizer_from_model_info.cache_clear()
    tokenizer = training_client._get_tokenizer("test-model", Holder())
    assert policies == [False]
    assert not marker.exists()
    _assert_tokenizer_equal(tokenizer, original)


@pytest.mark.parametrize(
    "tokenizer,revision",
    [
        ("moonshotai/Kimi-K2-Thinking", "612681931a8c906ddb349f8ad0f582cb552189cd"),
        ("moonshotai/Kimi-K2.5", "2426b45b6af0da48d0dcce71bbce6225e5c73adc"),
        ("moonshotai/Kimi-K2.6", "b5aabbfb20227ed42becbf5541dbffd213942c58"),
    ],
)
def test_other_model_kimi_policies_and_revisions_remain_unchanged(monkeypatch, tokenizer, revision):
    import transformers

    from fireworks.training.sdk._core.lib.public_interfaces import sampling_client

    calls = []
    monkeypatch.setattr(transformers.AutoTokenizer, "from_pretrained", lambda _model, **kwargs: calls.append(kwargs))
    sampling_client._load_tokenizer_from_model_info.cache_clear()
    sampling_client._load_tokenizer_from_model_info("unmigrated-model", tokenizer)
    assert calls == [{"fast": True, "trust_remote_code": True, "revision": revision}]


# ---------------------------------------------------------------------------
# Kimi K3/K3.1 identity (local only)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "model_name,expected",
    [
        (None, False),
        ("", False),
        # Reviewed canonical IDs: the digest-pinned HF repositories and the
        # registry-onboarded Fireworks resource IDs.
        ("moonshotai/Kimi-K3", True),
        ("moonshotai/Kimi-K3.1-Pro", True),
        ("accounts/fireworks/models/kimi-k3", True),
        ("accounts/fireworks/models/kimi-k3p1-pro", True),
        # Registry-style normalization: strip, trailing slashes, case.
        ("accounts/fireworks/models/kimi-k3/", True),
        ("MOONSHOTAI/KIMI-K3.1-PRO", True),
        (" moonshotai/Kimi-K3 ", True),
        # The exact architecture model_type strings are independently
        # selected control-plane context.
        ("kimi_k3", True),
        ("kimi_k31", True),
        ("Kimi_K31/", True),
        # Substrings, basenames, ancestors, namespaces and forks never
        # contribute identity.
        ("accounts/team/models/kimi-k3-finetune", False),
        ("accounts/fireworks/models/kimi-k3p1-pro/finetune-x", False),
        ("acme/Kimi-K3", False),
        ("moonshotai/Kimi-K30", False),
        ("accounts/fireworks/models/kimi-k3p10", False),
        ("kimi", False),
        ("kimi_k3_k31", False),
        # Kimi K2 stays outside the K3/K3.1 set.
        ("moonshotai/Kimi-K2-Thinking", False),
        ("moonshotai/Kimi-K2.6", False),
        ("kimi_k2", False),
        ("Qwen/Qwen3-8B", False),
    ],
)
def test_kimi_model_name_policy_exact_reviewed_ids(model_name, expected):
    assert identity.is_kimi_k3_k31_model_name(model_name) is expected


def test_kimi_reviewed_hub_sources_cannot_fail_open_on_metadata_fetch(monkeypatch):
    def unavailable(*_args, **_kwargs):
        raise AssertionError("reviewed Kimi Hub sources must not need advisory reads")

    monkeypatch.setattr(identity, "_hub_download", unavailable)
    for source in identity.KIMI_K3_K31_REPOSITORIES:
        assert identity.is_kimi_k3_k31_tokenizer_source(source)


def test_kimi_empty_and_missing_inputs_are_not_recognized() -> None:
    assert identity.is_kimi_k3_k31_tokenizer_source(None) is False
    assert identity.is_kimi_k3_k31_tokenizer_source("") is False
    assert identity.is_kimi_k3_k31_tokenizer_source("/nonexistent/path/xyz") is False


@pytest.mark.parametrize("model_type", ["kimi_k3", "kimi_k31"])
def test_kimi_config_model_type_branch(tmp_path: Path, model_type: str) -> None:
    (tmp_path / "config.json").write_text(json.dumps({"model_type": model_type}))
    assert identity.is_kimi_k3_k31_tokenizer_source(str(tmp_path)) is True


def test_kimi_other_model_type_is_not_recognized(tmp_path: Path) -> None:
    (tmp_path / "config.json").write_text(json.dumps({"model_type": "qwen3"}))
    assert identity.is_kimi_k3_k31_tokenizer_source(str(tmp_path)) is False


@pytest.mark.parametrize("model_type", ["qwen3", "llama", "new_model_family"])
def test_kimi_explicit_other_model_type_precedes_shared_vocab_digest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, model_type: str
) -> None:
    """Shared vocabulary bytes must not change an explicitly selected family."""
    (tmp_path / "config.json").write_text(json.dumps({"model_type": model_type}))
    vocab = tmp_path / "tiktoken.model"
    vocab.write_bytes(b"shared vocab bytes")
    config = tmp_path / "tokenizer_config.json"
    config.write_bytes(b"shared tokenizer config")
    monkeypatch.setattr(identity, "KIMI_K3_K31_TIKTOKEN_MODEL_SHA256", hashlib.sha256(vocab.read_bytes()).hexdigest())
    monkeypatch.setattr(
        identity,
        "KIMI_K3_K31_TOKENIZER_CONFIG_SHA256",
        frozenset({hashlib.sha256(config.read_bytes()).hexdigest()}),
    )
    assert identity.is_kimi_k3_k31_tokenizer_source(str(tmp_path)) is False
    assert identity.requires_code_free_tokenizer_loading(str(tmp_path)) is True


def test_kimi_configless_digest_branch(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    vocab = tmp_path / "tiktoken.model"
    vocab.write_bytes(b"shared vocab bytes")
    config = tmp_path / "tokenizer_config.json"
    config.write_bytes(b"shared tokenizer config")
    monkeypatch.setattr(identity, "KIMI_K3_K31_TIKTOKEN_MODEL_SHA256", hashlib.sha256(vocab.read_bytes()).hexdigest())
    monkeypatch.setattr(
        identity,
        "KIMI_K3_K31_TOKENIZER_CONFIG_SHA256",
        frozenset({hashlib.sha256(config.read_bytes()).hexdigest()}),
    )
    assert identity.is_kimi_k3_k31_tokenizer_source(str(tmp_path)) is True
    vocab.write_bytes(b"different bytes")
    assert identity.is_kimi_k3_k31_tokenizer_source(str(tmp_path)) is False


def test_kimi_vocab_digest_alone_is_not_enough(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Both the shared vocabulary and a pinned tokenizer_config must match."""
    vocab = tmp_path / "tiktoken.model"
    vocab.write_bytes(b"shared vocab bytes")
    (tmp_path / "tokenizer_config.json").write_bytes(b"unreviewed config bytes")
    monkeypatch.setattr(identity, "KIMI_K3_K31_TIKTOKEN_MODEL_SHA256", hashlib.sha256(vocab.read_bytes()).hexdigest())
    assert identity.is_kimi_k3_k31_tokenizer_source(str(tmp_path)) is False


def test_kimi_same_artifact_renamed_has_same_decision(tmp_path: Path) -> None:
    """Directory names never contribute identity: the same artifact keeps the
    decision its data earns under every name."""
    for name in ("totally-unrelated-name", "Kimi-K3.1-clone", "kimi-k3p1-pro"):
        directory = tmp_path / name
        directory.mkdir()
        (directory / "config.json").write_text(json.dumps({"model_type": "kimi_k31"}))
        assert identity.is_kimi_k3_k31_tokenizer_source(str(directory)) is True, name
        (directory / "config.json").write_text(json.dumps({"model_type": "qwen3"}))
        assert identity.is_kimi_k3_k31_tokenizer_source(str(directory)) is False, name


def test_kimi_absent_metadata_renamed_does_not_gain_identity(tmp_path: Path) -> None:
    for name in ("Kimi-K3.1-Pro", "kimi-k3", "kimi_k31"):
        directory = tmp_path / name
        directory.mkdir()
        assert identity.is_kimi_k3_k31_tokenizer_source(str(directory)) is False, name


def test_kimi_model_type_sentinel_is_context_but_never_source_identity(monkeypatch) -> None:
    """``kimi_k31`` (the exact model_type) is valid selected context, yet as a
    tokenizer SOURCE it is recognized only through data: with advisory reads
    unavailable it must not be recognized by the string alone."""
    assert identity.is_kimi_k3_k31_model_name(identity.KIMI_K31_MODEL_TYPE) is True

    reads = []

    def unavailable(repo_id, filename, **_kwargs):
        reads.append((repo_id, filename))
        return None

    monkeypatch.setattr(identity, "_hub_download", unavailable)
    monkeypatch.setattr(identity, "_hub_kimi_k3_k31_data_matches", lambda *_args, **_kwargs: False)
    assert identity.is_kimi_k3_k31_tokenizer_source("kimi_k31") is False
    assert reads == [("kimi_k31", "config.json")]
