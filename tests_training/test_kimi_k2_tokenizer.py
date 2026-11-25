"""Pinned plain-data oracles; no publisher Python is imported or executed."""

from __future__ import annotations

import os
import copy
import json
import pickle
import shutil
import asyncio
import hashlib
import multiprocessing
from typing import Any
from pathlib import Path
from unittest.mock import AsyncMock

import pytest
import tiktoken
import huggingface_hub
from tokenizers import AddedToken
from transformers import AutoTokenizer, PreTrainedTokenizer, dynamic_module_utils
from tiktoken.load import load_tiktoken_bpe
from transformers.convert_slow_tokenizer import bytes_to_unicode

from fireworks.training.sdk import kimi_k2_tokenizer as native, kimi_native_tokenizer
from fireworks.training.sdk.client import FiretitanTrainingClient
from fireworks.training.sdk.sampling import DeploymentSampler
from fireworks.training.sdk.kimi_k2_identity import (
    K26,
    K27,
    BASE,
    PROFILES,
    THINKING,
    PROFILE_KEY,
    COOKBOOK_THINKING_REVISION,
    get_k2_profile,
)
from fireworks.training.sdk._core.lib.public_interfaces.sampling_client import _load_tokenizer_from_model_info


def _oracle(source: Path) -> Any:
    config = json.loads((source / "tokenizer_config.json").read_text())
    entries = config["added_tokens_decoder"]
    return tiktoken.Encoding(
        name="independent-thinking-oracle",
        pat_str=kimi_native_tokenizer.KIMI_K3_K31_PAT_STR,
        mergeable_ranks=load_tiktoken_bpe(str(source / "tiktoken.model")),
        special_tokens={
            entries.get(str(index), {}).get("content", f"<|reserved_token_{index}|>"): index
            for index in range(163584, 163840)
        },
    )


def _release_ids(oracle: Any, text: str, allow: bool = True) -> list[int]:
    result = []
    for offset in range(0, len(text), 400000):
        block = text[offset : offset + 400000]
        start, count = 0, 0
        was_space = block[0].isspace() if block else False
        for index, char in enumerate(block):
            is_space = char.isspace()
            count = count + 1 if is_space == was_space else 1
            was_space = is_space
            if count > 25000:
                result.extend(
                    oracle.encode(block[start:index], allowed_special="all" if allow else set(), disallowed_special=())
                )
                start, count = index, 1
        result.extend(oracle.encode(block[start:], allowed_special="all" if allow else set(), disallowed_special=()))
    return result


class _OriginalHF(PreTrainedTokenizer):
    """Independent slow-HF dispatch matching the reviewed original raw algorithm."""

    vocab_files_names = {"vocab_file": "tiktoken.model"}
    model_input_names = ["input_ids", "attention_mask"]

    def __init__(
        self,
        vocab_file: str,
        bos_token: Any = "[BOS]",
        eos_token: Any = "[EOS]",
        unk_token: Any = None,
        pad_token: Any = None,
        additional_special_tokens: Any = None,
        added_tokens_decoder: Any = None,
        **kwargs: Any,
    ) -> None:
        source = Path(vocab_file).parent
        self.oracle = _oracle(source)
        alphabet = bytes_to_unicode()
        self.decoder = {
            index: "".join(alphabet[byte] for byte in self.oracle.decode_single_token_bytes(index))
            for index in range(self.oracle.n_vocab)
        }
        self.encoder = {value: key for key, value in self.decoder.items()}
        self.base = get_k2_profile(str(source)) == BASE
        self.profile = get_k2_profile(str(source))
        if additional_special_tokens is None:
            additional_special_tokens = [
                "<|im_end|>",
                "<|im_user|>",
                "<|im_assistant|>",
                "<|start_header_id|>",
                "<|end_header_id|>",
                "[EOT]",
                "<|im_system|>",
                "<|im_middle|>",
            ]
            if self.profile == K27:
                additional_special_tokens += ["<|media_begin|>", "<|media_content|>", "<|media_end|>", "<|media_pad|>"]
        super().__init__(
            bos_token=bos_token,
            eos_token=eos_token,
            unk_token=unk_token,
            pad_token=pad_token,
            additional_special_tokens=additional_special_tokens,
            added_tokens_decoder=added_tokens_decoder,
            **kwargs,
        )

    @property
    def vocab_size(self) -> int:
        return self.oracle.n_vocab

    def get_vocab(self) -> dict[str, int]:
        return self.encoder

    def _convert_token_to_id(self, token: str) -> int:
        return self.encoder[token]

    def _convert_id_to_token(self, index: int) -> str:
        return self.decoder[index]

    def _tokenize(self, text: str, **_kwargs: Any) -> list[str]:
        return [self.decoder[index] for index in _release_ids(self.oracle, text)]

    def apply_chat_template(self, conversation: Any, *args: Any, **kwargs: Any) -> Any:
        if self.base:
            return super().apply_chat_template(conversation, *args, **kwargs)
        return self._sorted_chat(conversation, *args, **kwargs)

    def _sorted_chat(
        self,
        conversation: Any,
        tools: Any = None,
        tokenize: bool = False,
        add_generation_prompt: bool = True,
        **kwargs: Any,
    ) -> Any:
        sorted_tools = json.loads(json.dumps(tools, sort_keys=True)) if tools is not None else None
        if PROFILES[self.profile].typescript_tools:
            if tools:
                assert tools == TOOLS
                kwargs["tools_ts_str"] = TOOLS_TYPESCRIPT
            if self.profile == K27:
                kwargs.pop("thinking", None)
                kwargs.pop("preserve_thinking", None)
            else:
                kwargs.setdefault("thinking", True)
                if self.profile == K26:
                    kwargs.setdefault("preserve_thinking", False)
        return super().apply_chat_template(
            conversation, tools=sorted_tools, tokenize=tokenize, add_generation_prompt=add_generation_prompt, **kwargs
        )


def _profile_source(key: str, revision: str) -> Path:
    profile = PROFILES[key]
    configured = os.environ.get("KIMI_THINKING_DATA_ROOT")
    if configured:
        root = Path(configured) / (
            ("thinking-sdk" if revision == profile.revision else "thinking-cookbook")
            if key == THINKING
            else profile.repository.split("/")[-1]
        )
    else:
        root = Path(
            huggingface_hub.snapshot_download(
                profile.repository, revision=revision, allow_patterns=list(profile.source_sha256)
            )
        )
    for filename, expected in profile.source_sha256.items():
        assert hashlib.sha256((root / filename).read_bytes()).hexdigest() == expected
    return root


@pytest.fixture(
    scope="module",
    params=[(key, profile.revision) for key, profile in PROFILES.items()] + [(THINKING, COOKBOOK_THINKING_REVISION)],
    ids=[profile.model_id for profile in PROFILES.values()] + ["thinking-cookbook"],
)
def source(request: pytest.FixtureRequest) -> Path:
    return _profile_source(*request.param)


@pytest.fixture(scope="module")
def readers(source: Path) -> tuple[Any, Any, Any]:
    return (
        native.load_k2_tokenizer(str(source), local_files_only=True),
        _OriginalHF.from_pretrained(source, local_files_only=True, trust_remote_code=False),
        _oracle(source),
    )


TEXTS = [
    "",
    "Hello 世界🙂\n42",
    "[BOS]<think>x</think>[EOS]",
    ".<|im_end|><|im_user|>",
    "<|reserved_token_163589|>",
    "x" * 24997 + "<think>",
    "x" * 24996 + "[BOS]",
    ("x " * 199997) + "x<think>",
    " " * 25005,
    "\x1c" * 25005,
    "汉" * 24997 + "<|im_end|>",
    "image <|media_begin|>data<|media_end|>",
]
TEXT_IDS = [
    "empty",
    "unicode",
    "markers",
    "punctuation",
    "reserved",
    "false-25k",
    "true-25k",
    "400k",
    "whitespace",
    "ascii-space",
    "han-25k",
    "media",
]
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "f",
            "parameters": {
                "type": "object",
                "properties": {"z": {"type": "number"}, "a": {"enum": [{"z": 2, "a": 1}]}},
            },
        },
    }
]
TOOLS_TYPESCRIPT = (
    "# Tools\n\n## functions\nnamespace functions {\ntype f = (_: {\n"
    "  a?: {'a': 1, 'z': 2},\n  z?: number\n}) => any;\n}\n"
)
MESSAGES = [
    {"role": "user", "content": "Use f."},
    {
        "role": "assistant",
        "content": "",
        "reasoning_content": "old thought",
        "tool_calls": [{"id": "call-1", "function": {"name": "f", "arguments": '{"z":2,"a":1}'}}],
    },
    {"role": "tool", "tool_call_id": "call-1", "content": "done"},
    {"role": "assistant", "content": "earlier answer", "reasoning_content": "historical thought"},
    {"role": "user", "content": "Continue."},
]


@pytest.mark.parametrize("text", TEXTS, ids=TEXT_IDS)
@pytest.mark.parametrize("allow", [False, True])
def test_raw_release_ids(readers: tuple[Any, ...], text: str, allow: bool) -> None:
    tokenizer, _reference, oracle = readers
    expected = _release_ids(oracle, text, allow)
    assert tokenizer.encode(text, allow_special_tokens=allow) == expected
    assert tokenizer.decode(expected) == text


@pytest.mark.parametrize(
    "options",
    [
        {},
        {"skip_special_tokens": False},
        {"clean_up_tokenization_spaces": False},
        {"skip_special_tokens": False, "clean_up_tokenization_spaces": False},
    ],
)
def test_decode_noop_options_preserve_literal_text(readers: tuple[Any, ...], options: dict[str, Any]) -> None:
    tokenizer, _reference, oracle = readers
    text = "[BOS]hello  .\n\n世界🙂\t<think></think>[EOS]"
    token_ids = _release_ids(oracle, text)
    assert tokenizer.decode(token_ids, **options) == oracle.decode(token_ids) == text
    assert tokenizer.decode(tokenizer.bos_id, **options) == oracle.decode([tokenizer.bos_id]) == "[BOS]"
    assert tokenizer.decode([], **options) == ""


@pytest.mark.parametrize(
    "options",
    [
        {"skip_special_tokens": True},
        {"clean_up_tokenization_spaces": True},
        {"skip_special_tokens": None},
        {"clean_up_tokenization_spaces": None},
        {"skip_special_tokens": 0},
        {"clean_up_tokenization_spaces": 0},
        {"unknown": False},
        {"skip_special_tokens": False, "clean_up_tokenization_spaces": True},
        {"skip_special_tokens": False, "clean_up_tokenization_spaces": False, "unknown": False},
    ],
)
def test_decode_rejects_non_noop_options(readers: tuple[Any, ...], options: dict[str, Any]) -> None:
    tokenizer = readers[0]
    with pytest.raises(ValueError, match="keyword options"):
        tokenizer.decode([tokenizer.bos_id], **options)


@pytest.mark.parametrize(
    "text", [TEXTS[1], TEXTS[5], TEXTS[6], TEXTS[7], TEXTS[-1]], ids=["short", "false-25k", "true-25k", "400k", "media"]
)
def test_distinct_original_hf_chat_boundary(readers: tuple[Any, ...], text: str) -> None:
    tokenizer, reference, oracle = readers
    messages = [{"role": "user", "content": text}]
    assert tokenizer.apply_chat_template(messages) == reference.apply_chat_template(messages)
    rendered = reference.apply_chat_template(messages, tokenize=False)
    assert tokenizer.encode(rendered) == _release_ids(oracle, rendered)
    assert tokenizer.apply_chat_template(messages, tokenize=True) == reference.apply_chat_template(
        messages, tokenize=True
    )


@pytest.mark.parametrize(
    "options",
    [
        {},
        {"thinking": False},
        {"thinking": False, "preserve_thinking": False},
        {"preserve_thinking": True},
        {"add_generation_prompt": False},
        {"tokenize": True},
        {"tokenize": True, "return_dict": True},
        {"tokenize": True, "return_tensors": "np", "return_dict": True},
    ],
)
def test_tools_history_options_and_immutability(readers: tuple[Any, ...], options: dict[str, Any]) -> None:
    tokenizer, reference, _oracle_value = readers
    original = copy.deepcopy((MESSAGES, TOOLS))
    actual = tokenizer.apply_chat_template(MESSAGES, tools=TOOLS, **options)
    expected = reference.apply_chat_template(MESSAGES, tools=TOOLS, **options)
    if options.get("return_tensors"):
        assert {key: value.tolist() for key, value in actual.items()} == {
            key: value.tolist() for key, value in expected.items()
        }
    else:
        assert actual == expected
    assert (MESSAGES, TOOLS) == original


def test_declared_flags_and_legacy_attributes(source: Path, readers: tuple[Any, ...]) -> None:
    tokenizer, reference, _oracle_value = readers
    for index, entry in json.loads((source / "tokenizer_config.json").read_text())["added_tokens_decoder"].items():
        assert tokenizer.convert_tokens_to_ids(entry["content"]) == int(index)
        assert tokenizer.added_tokens_decoder[int(index)].special == entry["special"]
    # HF's named special-token registry is distinct from AddedToken.special;
    # the original constructor does not add every media token to that registry.
    assert tokenizer.all_special_ids == reference.all_special_ids
    assert tokenizer.n_words == tokenizer.vocab_size == 163840
    assert tokenizer.bos_id == tokenizer.bos_token_id == 163584
    assert tokenizer.eos_id == tokenizer.eos_token_id == 163585
    assert tokenizer.pad_id == tokenizer.pad_token_id
    with pytest.raises(ValueError, match="keyword options"):
        tokenizer.decode([tokenizer.bos_id], skip_special_tokens=True)


def test_saved_native_generic_and_pickle(readers: tuple[Any, ...], tmp_path: Path) -> None:
    tokenizer, reference, _oracle_value = readers
    destination = tmp_path / "opaque"
    tokenizer.save_pretrained(destination)
    config = json.loads((destination / "tokenizer_config.json").read_text())
    assert config["tokenizer_class"] == "TikTokenTokenizer"
    assert config["auto_map"] == {"AutoTokenizer": ["tokenization_kimi.TikTokenTokenizer", None]}
    assert not list(destination.glob("*.py"))
    with pytest.raises(ValueError):
        AutoTokenizer.from_pretrained(destination, trust_remote_code=False, local_files_only=True)
    for restored in (native.load_k2_tokenizer(str(destination)), pickle.loads(pickle.dumps(tokenizer))):
        for text in TEXTS:
            assert restored.encode(text) == tokenizer.encode(text)
        assert restored.apply_chat_template(MESSAGES, tools=TOOLS, tokenize=True) == reference.apply_chat_template(
            MESSAGES, tools=TOOLS, tokenize=True
        )
        assert restored.all_special_ids == tokenizer.all_special_ids
        assert restored.chat_template == tokenizer.chat_template


@pytest.mark.parametrize(
    "dirname",
    [
        "opaque",
        "Kimi-K3.1-Pro",
        "GLM-5.3",
        "kimi-k2-thinking",
        "opaque:run-1",
        "nested/data",
        "relative/tokenizer/v1",
        "kimi_k3",
        "deepseek_v41",
        "moonshotai/Kimi-K3",
    ],
)
def test_renamed_sources_and_checkpoint_canary(
    source: Path, readers: tuple[Any, ...], tmp_path: Path, monkeypatch: pytest.MonkeyPatch, dirname: str
) -> None:
    copied = tmp_path / dirname
    copied.mkdir(parents=True)
    for filename in PROFILES[get_k2_profile(str(source))].source_sha256:
        shutil.copyfile(source / filename, copied / filename)
    marker = copied / "executed"
    (copied / "tokenization_kimi.py").write_text(f"open({str(marker)!r}, 'w').write('bad')\n")

    def reject(*_args: Any, **_kwargs: Any) -> None:
        raise AssertionError("checkpoint class requested")

    monkeypatch.setattr(dynamic_module_utils, "get_class_from_dynamic_module", reject)
    monkeypatch.setenv("HF_TRUST_REMOTE_CODE", "true")
    assert get_k2_profile(str(copied))
    loaded = native.load_k2_tokenizer(str(copied), local_files_only=True)
    assert loaded.encode("hello") == readers[0].encode("hello")
    monkeypatch.chdir(tmp_path)
    relative = str(copied.relative_to(tmp_path))
    _load_tokenizer_from_model_info.cache_clear()
    assert _load_tokenizer_from_model_info(relative).encode("hello") == readers[0].encode("hello")
    client = object.__new__(FiretitanTrainingClient)
    client._tokenizer_model = relative
    client._tokenizer_base_model = None
    assert client.get_tokenizer().encode("hello") == readers[0].encode("hello")
    client._tokenizer_base_model = relative
    assert client.get_tokenizer().encode("hello") == readers[0].encode("hello")
    _load_tokenizer_from_model_info.cache_clear()
    assert not marker.exists()


def test_tamper_and_unknown_saved_profile(source: Path, tmp_path: Path) -> None:
    for filename in PROFILES[get_k2_profile(str(source))].source_sha256:
        shutil.copyfile(source / filename, tmp_path / filename)
    profile = get_k2_profile(str(source))
    (tmp_path / "chat_template.jinja").write_text("foreign template")
    with pytest.raises(ValueError, match="reviewed data"):
        native.load_k2_tokenizer(str(tmp_path), profile=profile)
    config_path = tmp_path / "tokenizer_config.json"
    config = json.loads(config_path.read_text())
    config[PROFILE_KEY] = "unknown"
    config_path.write_text(json.dumps(config))
    with pytest.raises(ValueError, match="profile"):
        native.load_k2_tokenizer(str(tmp_path))


def test_canonical_pin_actual_sdk_entrypoints_and_native_precedence(
    source: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls = []

    def snapshot(**kwargs: Any) -> str:
        calls.append(kwargs)
        return str(source)

    def reject(*_args: Any, **_kwargs: Any) -> None:
        raise AssertionError("generic checkpoint loading requested")

    monkeypatch.setattr(huggingface_hub, "snapshot_download", snapshot)
    monkeypatch.setattr(AutoTokenizer, "from_pretrained", reject)
    monkeypatch.setenv("HF_TRUST_REMOTE_CODE", "true")
    profile = PROFILES[get_k2_profile(str(source))]
    _load_tokenizer_from_model_info.cache_clear()
    sampling = _load_tokenizer_from_model_info(profile.repository)
    client = object.__new__(FiretitanTrainingClient)
    client._tokenizer_model = profile.repository
    client._tokenizer_base_model = None
    training = client.get_tokenizer()
    assert sampling is not training
    assert sampling.encode("hello") == training.encode("hello")
    assert len(calls) == 2
    assert all(call["revision"] == profile.revision for call in calls)
    assert all(set(call["allow_patterns"]) == set(profile.source_sha256) for call in calls)
    sentinel = object()
    monkeypatch.setattr(kimi_native_tokenizer, "load_native_tokenizer", lambda *_args, **_kwargs: sentinel)
    _load_tokenizer_from_model_info.cache_clear()
    assert _load_tokenizer_from_model_info("moonshotai/Kimi-K3", profile.repository) is sentinel
    client._tokenizer_base_model = "moonshotai/Kimi-K3"
    assert client.get_tokenizer() is sentinel
    _load_tokenizer_from_model_info.cache_clear()


def test_folder_spelling_is_not_context(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    Path("kimi-k2-thinking").mkdir()
    assert not get_k2_profile("kimi-k2-thinking")
    assert not get_k2_profile(str(tmp_path))


@pytest.mark.parametrize("model_type", ["kimi_k3", "deepseek_v41"])
def test_local_base_metadata_still_constrains_tokenizer_override(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, model_type: str
) -> None:
    (tmp_path / "config.json").write_text(json.dumps({"model_type": model_type}))
    sentinel, calls = object(), []
    monkeypatch.setattr(kimi_native_tokenizer, "load_native_tokenizer", lambda *_a, **_k: sentinel)
    monkeypatch.setattr(AutoTokenizer, "from_pretrained", lambda *_a, **k: calls.append(k) or sentinel)
    override = PROFILES[THINKING].repository
    _load_tokenizer_from_model_info.cache_clear()
    assert _load_tokenizer_from_model_info(str(tmp_path), override) is sentinel
    client = object.__new__(FiretitanTrainingClient)
    client._tokenizer_model, client._tokenizer_base_model = override, str(tmp_path)
    assert client.get_tokenizer() is sentinel
    assert len(calls) == (0 if model_type == "kimi_k3" else 2)
    assert all(call["trust_remote_code"] is False for call in calls)
    _load_tokenizer_from_model_info.cache_clear()


@pytest.mark.parametrize("metadata", ["{", "[]", "null", '{"tokenizer_class":"TikTokenTokenizer"}'])
def test_unrelated_metadata_does_not_select_thinking(tmp_path: Path, metadata: str) -> None:
    (tmp_path / "tokenizer_config.json").write_text(metadata)
    assert not get_k2_profile(str(tmp_path))
    assert get_k2_profile(str(tmp_path), base_model=PROFILES[THINKING].repository)
    assert not get_k2_profile(str(tmp_path), base_model="customer/Kimi-K2-Thinking")


def test_foreign_override_stays_code_free(monkeypatch: pytest.MonkeyPatch) -> None:
    sentinel, calls = object(), []

    def generic(source: str, **kwargs: Any) -> Any:
        calls.append((source, kwargs))
        return sentinel

    monkeypatch.setattr(AutoTokenizer, "from_pretrained", generic)
    monkeypatch.setenv("HF_TRUST_REMOTE_CODE", "true")
    client = object.__new__(FiretitanTrainingClient)
    client._tokenizer_model = "customer/foreign-tokenizer"
    client._tokenizer_base_model = PROFILES[THINKING].repository
    assert client.get_tokenizer() is sentinel
    _load_tokenizer_from_model_info.cache_clear()
    assert _load_tokenizer_from_model_info(PROFILES[THINKING].repository, client._tokenizer_model) is sentinel
    assert len(calls) == 2
    assert all(source == client._tokenizer_model and kwargs["trust_remote_code"] is False for source, kwargs in calls)
    _load_tokenizer_from_model_info.cache_clear()


def test_unreviewed_revision_is_rejected_before_download(monkeypatch: pytest.MonkeyPatch) -> None:
    def reject(**_kwargs: Any) -> None:
        raise AssertionError("unreviewed revision was downloaded")

    monkeypatch.setattr(huggingface_hub, "snapshot_download", reject)
    with pytest.raises(ValueError, match="reviewed data revision"):
        native.load_k2_tokenizer(PROFILES[THINKING].repository, revision="main")


def test_unknown_k2_metadata_cannot_reopen_checkpoint_code(tmp_path: Path) -> None:
    (tmp_path / "config.json").write_text('{"model_type":"kimi_k2"}')
    (tmp_path / "tokenizer_config.json").write_text('{"auto_map":{"AutoTokenizer":["poison.Bad",null]}}')
    client = object.__new__(FiretitanTrainingClient)
    client._tokenizer_model = str(tmp_path)
    client._tokenizer_base_model = None
    with pytest.raises(ValueError, match="profile"):
        client.get_tokenizer()
    _load_tokenizer_from_model_info.cache_clear()
    with pytest.raises(ValueError, match="profile"):
        _load_tokenizer_from_model_info(str(tmp_path))
    _load_tokenizer_from_model_info.cache_clear()


def test_k25_text_only_alias_uses_canonical_pin(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = []

    def download(**kwargs: Any) -> None:
        calls.append(kwargs)
        raise RuntimeError("data-only boundary reached")

    monkeypatch.setattr(huggingface_hub, "snapshot_download", download)
    client = object.__new__(FiretitanTrainingClient)
    client._tokenizer_model = "moonshotai/Kimi-K2.5-Text-Only"
    client._tokenizer_base_model = None
    with pytest.raises(RuntimeError, match="data-only"):
        client.get_tokenizer()
    assert calls[0]["repo_id"] == "moonshotai/Kimi-K2.5"
    assert calls[0]["revision"] == "2426b45b6af0da48d0dcce71bbce6225e5c73adc"


def test_k27_original_default_media_specials(monkeypatch: pytest.MonkeyPatch) -> None:
    source = _profile_source(K27, PROFILES[K27].revision)
    config = json.loads((source / "tokenizer_config.json").read_text())
    captured = []
    original_init = PreTrainedTokenizer.__init__

    def capture(self: Any, *args: Any, **kwargs: Any) -> None:
        captured.append(kwargs["additional_special_tokens"])
        original_init(self, *args, **kwargs)

    monkeypatch.setattr(PreTrainedTokenizer, "__init__", capture)
    native.TikTokenTokenizer(
        vocab_file=str(source / "tiktoken.model"),
        bos_token=config["bos_token"],
        eos_token=config["eos_token"],
        unk_token=config["unk_token"],
        pad_token=config["pad_token"],
        added_tokens_decoder={int(key): AddedToken(**entry) for key, entry in config["added_tokens_decoder"].items()},
        **{PROFILE_KEY: K27},
    )
    assert captured == [
        [
            "<|im_end|>",
            "<|im_user|>",
            "<|im_assistant|>",
            "<|start_header_id|>",
            "<|end_header_id|>",
            "[EOT]",
            "<|im_system|>",
            "<|im_middle|>",
            "<|media_begin|>",
            "<|media_content|>",
            "<|media_end|>",
            "<|media_pad|>",
        ]
    ]


@pytest.mark.parametrize("profile", [key for key, value in PROFILES.items() if value.typescript_tools])
def test_typescript_failure_retains_original_json_fallback(profile: str, caplog: pytest.LogCaptureFixture) -> None:
    source = _profile_source(profile, PROFILES[profile].revision)
    tokenizer = native.load_k2_tokenizer(str(source))
    reference = _OriginalHF.from_pretrained(source, local_files_only=True, trust_remote_code=False)
    tools = [
        {
            "type": "function",
            "function": {
                "name": "f",
                "parameters": {
                    "type": "object",
                    "properties": {"x": {"$ref": "https://invalid.example/schema"}},
                },
            },
        }
    ]
    options = {"thinking": True} if profile != K27 else {}
    if profile == K26:
        options["preserve_thinking"] = False
    expected = PreTrainedTokenizer.apply_chat_template(
        reference,
        MESSAGES,
        tools=json.loads(json.dumps(tools, sort_keys=True)),
        tokenize=False,
        add_generation_prompt=True,
        **options,
    )
    assert tokenizer.apply_chat_template(MESSAGES, tools=tools) == expected
    assert "Tool conversion failed" in caplog.text


@pytest.mark.parametrize(
    "source_profile,selected",
    [
        ("kimi_k25_v1", K26),
        (K26, "kimi_k25_v1"),
        (K27, "kimi_k25_v1"),
    ],
)
def test_common_vocabulary_cannot_substitute_profile(source_profile: str, selected: str) -> None:
    source = _profile_source(source_profile, PROFILES[source_profile].revision)
    with pytest.raises(ValueError, match="reviewed data"):
        native.load_k2_tokenizer(str(source), profile=selected)


def test_saved_profile_still_checks_vocabulary(readers: tuple[Any, ...], tmp_path: Path) -> None:
    readers[0].save_pretrained(tmp_path)
    (tmp_path / "tiktoken.model").write_text("not the reviewed vocabulary")
    with pytest.raises(ValueError, match="reviewed data"):
        native.load_k2_tokenizer(str(tmp_path))
    (tmp_path / "tiktoken.model").unlink()
    with pytest.raises(ValueError, match="vocabulary is missing"):
        native.load_k2_tokenizer(str(tmp_path))


def _spawn_encode(tokenizer: Any, connection: Any) -> None:
    connection.send(tokenizer.encode("Hello 世界 [EOS]"))
    connection.close()


def test_spawned_worker_unpickles_installed_reader(readers: tuple[Any, ...]) -> None:
    context = multiprocessing.get_context("spawn")
    receiving, sending = context.Pipe(duplex=False)
    process = context.Process(target=_spawn_encode, args=(readers[0], sending))
    process.start()
    sending.close()
    try:
        assert receiving.poll(60), "spawned reader did not return"
        assert receiving.recv() == readers[0].encode("Hello 世界 [EOS]")
        process.join(timeout=30)
        assert process.exitcode == 0
    finally:
        if process.is_alive():
            process.terminate()
            process.join(timeout=30)
        receiving.close()


@pytest.mark.parametrize("structured", [False, True])
def test_sampler_integer_stops_preserve_special_ids(readers: tuple[Any, ...], structured: bool) -> None:
    tokenizer = readers[0]
    sampler = object.__new__(DeploymentSampler)
    sampler.tokenizer = tokenizer
    sentinel = object()
    completion = AsyncMock(return_value=sentinel if structured else [])
    method = sampler.sample_with_prompt_tokens_result if structured else sampler.sample_with_prompt_tokens
    if structured:
        sampler._do_one_completion_result = completion
    else:
        sampler._do_one_completion = completion
    stops = [tokenizer.eos_token_id, tokenizer.bos_token_id]
    expected = [tokenizer.decode([token_id]) for token_id in stops]
    assert asyncio.run(method([123, 456], stop=stops)) == (sentinel if structured else [])
    assert completion.await_args.args[0] == [123, 456]
    assert completion.await_args.kwargs["stop"] == expected
    assert stops == [tokenizer.eos_token_id, tokenizer.bos_token_id]
    assert tokenizer.decode(stops, skip_special_tokens=False) == tokenizer.decode(stops)
    with pytest.raises(ValueError, match="keyword options"):
        tokenizer.decode(stops, skip_special_tokens=True)


@pytest.mark.parametrize("override_kind", ["local", "saved", "hub"])
def test_explicit_tokenizer_profile_precedes_local_base(
    source: Path,
    readers: tuple[Any, ...],
    override_kind: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    key = get_k2_profile(str(source))
    base_key = THINKING if key == BASE else BASE
    base = _profile_source(base_key, PROFILES[base_key].revision)
    if override_kind == "saved":
        source = tmp_path / "saved-override"
        readers[0].save_pretrained(source)
    override = PROFILES[key].repository if override_kind == "hub" else str(source)
    monkeypatch.setattr(huggingface_hub, "snapshot_download", lambda **_kwargs: str(source))
    assert get_k2_profile(override, base_model=str(base)) == key
    _load_tokenizer_from_model_info.cache_clear()
    try:
        sampling = _load_tokenizer_from_model_info(str(base), override)
        client = object.__new__(FiretitanTrainingClient)
        client._tokenizer_model, client._tokenizer_base_model = override, str(base)
        for actual in (sampling, client.get_tokenizer()):
            assert type(actual).__module__ == native.__name__
            assert actual.init_kwargs[PROFILE_KEY] == key
            assert actual.encode("Hello 世界 [EOS]") == readers[0].encode("Hello 世界 [EOS]")
    finally:
        _load_tokenizer_from_model_info.cache_clear()
