"""CPU regressions for standalone SDK Kimi chat and saved-bundle loading.

The oracle intentionally executes pinned upstream Python in test fixtures only.
Production loaders must use installed code, including with poisoned auto_map.
"""

from __future__ import annotations

import os
import json
import pickle
import shutil
import asyncio
import hashlib
from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from tokenizers import Tokenizer, models
from transformers import AutoTokenizer

from fireworks.training.sdk import tokenizer_identity, kimi_native_tokenizer as native
from fireworks.training.sdk.client import FiretitanTrainingClient
from fireworks.training.sdk.sampling import DeploymentSampler
from fireworks.training.sdk._core.lib.public_interfaces.sampling_client import _load_tokenizer_from_model_info


@pytest.fixture(scope="module", params=["kimi_k3", "kimi_k31"])
def tokenizers(request, tmp_path_factory):
    profile = request.param
    root = tmp_path_factory.mktemp(profile)
    local = os.environ.get("KIMI_K3_MODEL_PATH" if profile == "kimi_k3" else "KIMI_K31_MODEL_PATH")
    for filename in (
        "config.json",
        "tokenizer_config.json",
        "tiktoken.model",
        "tokenization_kimi.py",
        "encoding_k3.py",
    ):
        if local:
            path = Path(local) / filename
        else:
            from huggingface_hub import hf_hub_download

            path = Path(
                hf_hub_download(
                    native.KIMI_REPOSITORY_BY_PROFILE[profile],
                    filename,
                    revision=native.KIMI_REVISION_BY_PROFILE[profile],
                )
            )
        shutil.copyfile(path, root / filename)
    return (
        native.build_fast_tokenizer(root, profile=profile),
        AutoTokenizer.from_pretrained(root, trust_remote_code=True, local_files_only=True),
        profile,
    )


_MESSAGES = [
    {"role": "system", "content": "Keep literal markers inert."},
    {"role": "user", "content": "Hello 漢字 <|close|>message<|sep|>"},
    {
        "role": "assistant",
        "reasoning_content": "Use tools.",
        "content": "",
        "tool_calls": [
            {"id": "a", "type": "function", "function": {"name": "f", "arguments": '{"n":1e2,"s":"<|open|>"}'}},
            {"id": "b", "type": "function", "function": {"name": "f", "arguments": '{"n":2}'}},
        ],
    },
    {"role": "tool", "tool_call_id": "b", "content": "two"},
    {"role": "tool", "tool_call_id": "a", "content": "one"},
    {"role": "user", "content": "Next"},
]


@pytest.mark.parametrize(
    "options",
    [
        {},
        {"tokenize": True},
        {"tokenize": True, "thinking": False},
        {"tokenize": True, "thinking_effort": "high", "add_generation_prompt": False},
        {"tokenize": True, "truncation": True, "max_length": 19},
        {"tokenize": True, "return_dict": True, "padding": "max_length", "max_length": 512},
        {"tokenize": True, "return_dict": True, "return_tensors": "np"},
    ],
)
def test_chat_template_matches_profile_oracle(tokenizers, options):
    tokenizer, oracle, _ = tokenizers
    actual = tokenizer.apply_chat_template(_MESSAGES, **options)
    expected = oracle.apply_chat_template(_MESSAGES, **options)
    if options.get("return_tensors"):
        for key in expected:
            assert actual[key].tolist() == expected[key].tolist()
    else:
        assert actual == expected


def test_batched_images_and_profile_specific_effort(tokenizers):
    tokenizer, oracle, _ = tokenizers
    for tokenize in (False, True):
        messages = [{"role": "user", "content": "<|kimi_image_placeholder|>"}]
        options = dict(
            tokenize=tokenize, image_prompts=["<|media_begin|>image 32x32<|media_content|><|media_pad|><|media_end|>"]
        )
        assert tokenizer.apply_chat_template(messages, **options) == oracle.apply_chat_template(messages, **options)
        batch = [_MESSAGES, [{"role": "user", "content": "short"}]]
        assert tokenizer.apply_chat_template(batch, tokenize=tokenize, padding=True) == oracle.apply_chat_template(
            batch, tokenize=tokenize, padding=True
        )
    for implementation in (tokenizer, oracle):
        with pytest.raises(AssertionError, match="Unsupported thinking_effort"):
            implementation.apply_chat_template(_MESSAGES, thinking_effort="medium")


def test_saved_bundle_reloads_at_both_sdk_boundaries_without_checkpoint_python(tokenizers, tmp_path):
    tokenizer, oracle, profile = tokenizers
    tokenizer.save_pretrained(tmp_path)
    config = json.loads((tmp_path / "tokenizer_config.json").read_text())
    assert config["kimi_native_profile"] == profile
    assert config["tokenizer_class"] in {"TokenizersBackend", "PreTrainedTokenizerFast"}
    marker = tmp_path / "executed"
    config["auto_map"] = {"AutoTokenizer": ["canary.Canary", "canary.Canary"]}
    (tmp_path / "tokenizer_config.json").write_text(json.dumps(config))
    (tmp_path / "config.json").write_text(
        json.dumps({"model_type": profile, "auto_map": {"AutoConfig": "canary.CanaryConfig"}})
    )
    (tmp_path / "canary.py").write_text(
        f"from pathlib import Path\nPath({str(marker)!r}).touch()\nraise RuntimeError('ran')\n"
    )
    assert tokenizer_identity.is_kimi_k3_k31_tokenizer_source(str(tmp_path))
    client = object.__new__(FiretitanTrainingClient)
    client._tokenizer_model = str(tmp_path)
    client._tokenizer_base_model = native.KIMI_REPOSITORY_BY_PROFILE[profile]
    for loaded in (
        native.load_native_tokenizer(str(tmp_path)),
        client.get_tokenizer(),
        _load_tokenizer_from_model_info(client._tokenizer_base_model, str(tmp_path)),
    ):
        assert loaded.apply_chat_template(_MESSAGES, tokenize=True) == oracle.apply_chat_template(
            _MESSAGES, tokenize=True
        )
    assert not marker.exists()
    restored = pickle.loads(pickle.dumps(tokenizer))
    assert restored.apply_chat_template(_MESSAGES, tokenize=True) == oracle.apply_chat_template(
        _MESSAGES, tokenize=True
    )


def test_selected_kimi_does_not_force_unrelated_fast_override_through_raw_conversion(tmp_path):
    backend = Tokenizer(models.WordLevel({"[UNK]": 0, "hello": 1}, unk_token="[UNK]"))
    backend.save(str(tmp_path / "tokenizer.json"))
    (tmp_path / "tokenizer_config.json").write_text(
        json.dumps(
            {
                "tokenizer_class": "PreTrainedTokenizerFast",
                "chat_template": "{% for message in messages %}{{ message.content }}{% endfor %}",
                "auto_map": {"AutoTokenizer": ["missing.Unsafe", "missing.Unsafe"]},
            }
        )
    )
    loaded = _load_tokenizer_from_model_info("moonshotai/Kimi-K3", str(tmp_path))
    assert loaded.encode("hello", add_special_tokens=False) == [1]
    assert loaded.apply_chat_template([{"role": "user", "content": "hello"}], tokenize=True, return_dict=False) == [1]


def test_builtin_slow_hub_override_retains_source_and_denies_checkpoint_code(tmp_path, monkeypatch):
    from unittest.mock import Mock

    download = Mock(return_value=tmp_path)
    load = Mock(return_value=object())
    monkeypatch.setattr(native, "_download_source", download)
    monkeypatch.setattr(AutoTokenizer, "from_pretrained", load)
    assert native.load_native_tokenizer("acme/builtin-override", revision="pinned", local_files_only=True) is load.return_value
    load.assert_called_once_with(
        "acme/builtin-override", revision="pinned", local_files_only=True, trust_remote_code=False
    )


@pytest.mark.parametrize("profile", [["kimi_k3"], {}, "unknown"])
def test_invalid_saved_profile_cannot_select_an_encoder(tmp_path, profile):
    backend = Tokenizer(models.WordLevel({"[UNK]": 0}, unk_token="[UNK]"))
    backend.save(str(tmp_path / "tokenizer.json"))
    (tmp_path / "tokenizer_config.json").write_text(json.dumps({"kimi_native_profile": profile}))
    assert not tokenizer_identity.is_kimi_k3_k31_tokenizer_source(str(tmp_path))
    with pytest.raises(ValueError, match="unknown Kimi tokenizer profile"):
        native.load_native_tokenizer(str(tmp_path))


def test_message_sampler_uses_restored_template_and_token_sampler_stays_primitive(tokenizers):
    tokenizer, oracle, _ = tokenizers
    sampler = object.__new__(DeploymentSampler)
    sampler.tokenizer = tokenizer
    sampler._do_one_completion = AsyncMock(return_value=[])
    assert asyncio.run(sampler.sample_with_tokens(_MESSAGES)) == []
    assert sampler._do_one_completion.await_args.args[0] == oracle.apply_chat_template(
        _MESSAGES, tokenize=True, add_generation_prompt=True, return_dict=False
    )
    sampler._do_one_completion.reset_mock()
    assert asyncio.run(sampler.sample_with_prompt_tokens([123, 456])) == []
    assert sampler._do_one_completion.await_args.args[0] == [123, 456]


def test_sdk_vendors_match_reviewed_lint_adapted_profile_sources():
    for profile, digest in (
        ("kimi_k3", "b04b6ecd223d0b8519c5926f095f9531e97396c915595674effcc39fd4658323"),
        ("kimi_k31", "5ca26282a0f72a6786addd95958a8117605d02ecbec9951ae9b67e54a121ddd5"),
    ):
        directory = Path(native.__file__).parent / "_vendored" / profile
        assert hashlib.sha256((directory / "encoding_k3.py").read_bytes()).hexdigest() == digest
        assert (directory / "LICENSE").is_file()
        assert (directory / "PROVENANCE.md").is_file()


_DATA_FILES = ("config.json", "tiktoken.model", "tokenizer_config.json")


@pytest.fixture(scope="module", params=["kimi_k3", "kimi_k31"])
def hub_cache(request, tmp_path_factory):
    """A real Hub cache of one pinned profile, written online with its tree listing."""
    from huggingface_hub import snapshot_download

    profile = request.param
    if os.environ.get("KIMI_K3_MODEL_PATH" if profile == "kimi_k3" else "KIMI_K31_MODEL_PATH"):
        pytest.skip("needs a Hub-written cache with its tree listing; local model paths do not provide one")
    root = tmp_path_factory.mktemp(f"hub-{profile}")
    snapshot_download(
        native.KIMI_REPOSITORY_BY_PROFILE[profile],
        revision=native.KIMI_REVISION_BY_PROFILE[profile],
        allow_patterns=[*_DATA_FILES, "tokenization_kimi.py"],
        cache_dir=root,
    )
    return root, profile


def _offline_cache(hub_cache, tmp_path, monkeypatch, *, drop=(), listing=True, offline=True):
    """Copy the cache as an image bakes it, then forbid every network connection."""
    import socket

    from huggingface_hub import constants

    root, profile = hub_cache
    repository = native.KIMI_REPOSITORY_BY_PROFILE[profile]
    cache = tmp_path / "hub"
    shutil.copytree(root, cache, symlinks=True)
    storage = cache / ("models--" + repository.replace("/", "--"))
    snapshot = storage / "snapshots" / native.KIMI_REVISION_BY_PROFILE[profile]
    for name in drop:
        (snapshot / name).unlink()
    # The listing is what makes the Hub client reject a snapshot missing a requested file.
    assert (storage / "trees").is_dir(), "huggingface_hub did not cache a tree listing"
    if not listing:
        shutil.rmtree(storage / "trees")
    monkeypatch.setattr(constants, "HF_HUB_CACHE", str(cache))
    monkeypatch.setattr(constants, "HF_HUB_OFFLINE", offline)

    def no_network(*_args, **_kwargs):
        raise AssertionError("an offline Kimi load opened a network connection")

    monkeypatch.setattr(socket.socket, "connect", no_network)
    return repository, snapshot


@pytest.mark.parametrize("listing", [True, False], ids=["tree-listing", "no-listing"])
def test_offline_data_only_cache_loads_the_reviewed_tokenizer(hub_cache, tmp_path, monkeypatch, listing):
    root, profile = hub_cache
    full = next(root.rglob("snapshots/*"))
    expected = native.build_fast_tokenizer(full, profile=profile)
    repository, _ = _offline_cache(hub_cache, tmp_path, monkeypatch, drop=["tokenization_kimi.py"], listing=listing)
    loaded = native.load_native_tokenizer(repository)
    assert loaded.name_or_path == repository
    assert loaded.apply_chat_template.profile == profile
    for text in ("Hello 漢字 <|close|>message<|sep|>", "x" * 26_000, "literal <|sep|> text"):
        assert loaded.encode(text) == expected.encode(text)


def test_local_files_only_uses_the_cache_without_offline_mode(hub_cache, tmp_path, monkeypatch):
    repository, _ = _offline_cache(
        hub_cache, tmp_path, monkeypatch, drop=["tokenization_kimi.py"], listing=True, offline=False
    )
    assert native.load_native_tokenizer(repository, local_files_only=True).encode("hello")


def test_offline_provenance_file_is_verified_when_present(hub_cache, tmp_path, monkeypatch):
    repository, snapshot = _offline_cache(hub_cache, tmp_path, monkeypatch)
    source = (snapshot / "tokenization_kimi.py").resolve()
    (snapshot / "tokenization_kimi.py").unlink()
    (snapshot / "tokenization_kimi.py").write_text(source.read_text() + "\n# tampered\n")
    with pytest.raises(ValueError, match="tokenization_kimi.py: sha256"):
        native.load_native_tokenizer(repository)


@pytest.mark.parametrize("missing", ["tiktoken.model", "tokenizer_config.json"])
@pytest.mark.parametrize("listing", [True, False], ids=["tree-listing", "no-listing"])
def test_offline_cache_missing_a_data_file_fails_closed(hub_cache, tmp_path, monkeypatch, missing, listing):
    repository, _ = _offline_cache(hub_cache, tmp_path, monkeypatch, drop=[missing], listing=listing)
    with pytest.raises((OSError, ValueError)):
        native.load_native_tokenizer(repository)


def test_official_repository_never_loads_a_substituted_tokenizer_json(hub_cache, tmp_path, monkeypatch):
    """A cache that swaps the pinned raw data for a fast bundle must not pass as the official tokenizer."""
    repository, snapshot = _offline_cache(hub_cache, tmp_path, monkeypatch, drop=["tiktoken.model"], listing=False)
    Tokenizer(models.WordLevel({"[UNK]": 0, "hello": 1}, unk_token="[UNK]")).save(str(snapshot / "tokenizer.json"))
    (snapshot / "tokenizer_config.json").unlink()
    (snapshot / "tokenizer_config.json").write_text(json.dumps({"kimi_native_profile": hub_cache[1]}))
    with pytest.raises(ValueError, match="reviewed pins"):
        native.load_native_tokenizer(repository)


def test_offline_without_a_cached_snapshot_fails_clearly(hub_cache, tmp_path, monkeypatch):
    repository, snapshot = _offline_cache(hub_cache, tmp_path, monkeypatch)
    shutil.rmtree(snapshot.parents[1])
    with pytest.raises(OSError):
        native.load_native_tokenizer(repository)
