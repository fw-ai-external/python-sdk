"""Installed K2 readers retaining the original tiktoken representation."""

from __future__ import annotations

import json
import hashlib
import logging
from shutil import copyfile
from typing import Any
from pathlib import Path
from collections.abc import Iterator

import tiktoken
from transformers import AutoTokenizer, PreTrainedTokenizer
from tiktoken.load import load_tiktoken_bpe
from transformers.convert_slow_tokenizer import bytes_to_unicode

from .kimi_k2_identity import (
    K26,
    K27,
    BASE,
    PROFILES,
    THINKING,
    PROFILE_KEY,
    COOKBOOK_THINKING_REVISION,
    get_k2_profile,
)
from .kimi_native_tokenizer import KIMI_K3_K31_PAT_STR

_AUTO_MAP = {"AutoTokenizer": ["tokenization_kimi.TikTokenTokenizer", None]}
KIMI_K2_TOKENIZER_CAPABILITY = "kimi-k2-json-and-typescript-tools/read-save-v1"


def _sort_tools(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _sort_tools(item) for key, item in sorted(value.items())}
    if isinstance(value, list):
        return [_sort_tools(item) for item in value]
    return value


class TikTokenTokenizer(PreTrainedTokenizer):
    """Keep direct chunk-first encoding and inherited HF chat encoding distinct."""

    vocab_files_names = {"vocab_file": "tiktoken.model"}
    model_input_names = ["input_ids", "attention_mask"]
    num_reserved_special_tokens = 256
    pat_str = KIMI_K3_K31_PAT_STR

    def __init__(
        self,
        vocab_file: str,
        bos_token: Any = "[BOS]",
        eos_token: Any = "[EOS]",
        unk_token: Any = None,
        pad_token: Any = None,
        additional_special_tokens: list[Any] | None = None,
        added_tokens_decoder: dict[int, Any] | None = None,
        **kwargs: Any,
    ) -> None:
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
            if kwargs.get(PROFILE_KEY) == K27:
                additional_special_tokens += ["<|media_begin|>", "<|media_content|>", "<|media_end|>", "<|media_pad|>"]
        self.vocab_file = vocab_file
        ranks = load_tiktoken_bpe(vocab_file)
        declared = {index: token.content for index, token in (added_tokens_decoder or {}).items()}
        self.special_tokens = {
            declared.get(index, f"<|reserved_token_{index}|>"): index
            for index in range(len(ranks), len(ranks) + self.num_reserved_special_tokens)
        }
        self.model = tiktoken.Encoding(
            name="kimi-k2",
            pat_str=self.pat_str,
            mergeable_ranks=ranks,
            special_tokens=self.special_tokens,
        )
        self.n_words = self.model.n_vocab
        self.bos_id = self.special_tokens[str(bos_token)]
        self.eos_id = self.special_tokens[str(eos_token)]
        self.pad_id = self.special_tokens[str(pad_token)]
        self.unk_id = self.special_tokens[str(unk_token)]
        self.byte_encoder = bytes_to_unicode()
        self.byte_decoder = {value: key for key, value in self.byte_encoder.items()}
        self.decoder = {
            index: "".join(self.byte_encoder[byte] for byte in self.model.decode_single_token_bytes(index))
            for index in range(self.model.n_vocab)
        }
        self.encoder = {token: index for index, token in self.decoder.items()}
        # Retain the original class declaration and inert map: removing the map
        # lets generic readers convert this vocabulary with different reserved IDs.
        # No checkpoint Python is saved; installed readers ignore the map.
        kwargs["auto_map"] = _AUTO_MAP.copy()
        kwargs.setdefault(PROFILE_KEY, THINKING)
        super().__init__(
            bos_token=bos_token,
            eos_token=eos_token,
            unk_token=unk_token,
            pad_token=pad_token,
            additional_special_tokens=additional_special_tokens,
            added_tokens_decoder=added_tokens_decoder,
            **kwargs,
        )
        self.all_special_ids_set = set(self.all_special_ids)

    @property
    def vocab_size(self) -> int:
        return self.model.n_vocab

    def get_vocab(self) -> dict[str, int]:
        return self.encoder

    @staticmethod
    def _chunks(text: str) -> Iterator[str]:
        for offset in range(0, len(text), 400_000):
            block = text[offset : offset + 400_000]
            start, count = 0, 0
            was_space = block[0].isspace() if block else False
            for index, char in enumerate(block):
                is_space = char.isspace()
                count = count + 1 if is_space == was_space else 1
                was_space = is_space
                if count > 25_000:
                    yield block[start:index]
                    start, count = index, 1
            yield block[start:]

    def encode(self, text: str, allow_special_tokens: bool = True, **kwargs: Any) -> list[int]:
        if kwargs:
            return super().encode(text, **kwargs)
        result = []
        for processed in self.pre_tokenizer_process(text):
            for chunk in self._chunks(processed):
                result.extend(
                    self.model.encode(
                        chunk, allowed_special="all" if allow_special_tokens else set(), disallowed_special=()
                    )
                )
        return result

    def pre_tokenizer_process(self, text: str) -> list[str]:
        return [text]

    def decode(self, token_ids: int | list[int], **kwargs: Any) -> str:
        # Callers can explicitly retain special tokens and literal whitespace.
        skip_special_tokens = kwargs.pop("skip_special_tokens", False)
        clean_up_tokenization_spaces = kwargs.pop("clean_up_tokenization_spaces", False)
        if skip_special_tokens is not False or clean_up_tokenization_spaces is not False or kwargs:
            raise ValueError("K2 tokenizer decode does not accept keyword options")
        return self.model.decode([token_ids] if isinstance(token_ids, int) else token_ids)

    def _tokenize(self, text: str, **kwargs: Any) -> list[str]:
        return [self.decoder[index] for index in self.encode(text)]

    def _convert_token_to_id(self, token: str) -> int:
        return self.encoder.get(token, self.unk_id)

    def _convert_id_to_token(self, index: int) -> str | None:
        return self.decoder.get(index)

    def convert_tokens_to_string(self, tokens: list[str]) -> str:
        return bytes(self.byte_decoder[char] for char in "".join(tokens)).decode("utf-8", "replace")

    @staticmethod
    def clean_up_tokenization(text: str) -> str:
        return text

    def save_vocabulary(self, save_directory: str, filename_prefix: str | None = None) -> tuple[str]:
        destination = Path(save_directory) / ((filename_prefix + "-" if filename_prefix else "") + "tiktoken.model")
        if Path(self.vocab_file).resolve() != destination.resolve():
            copyfile(self.vocab_file, destination)
        return (str(destination),)

    def apply_chat_template(self, conversation: Any, *args: Any, **kwargs: Any) -> Any:
        if self.init_kwargs[PROFILE_KEY] == BASE:
            return super().apply_chat_template(conversation, *args, **kwargs)
        return self._apply_sorted_chat_template(conversation, *args, **kwargs)

    def _apply_sorted_chat_template(
        self,
        conversation: Any,
        tools: Any = None,
        tokenize: bool = False,
        add_generation_prompt: bool = True,
        **kwargs: Any,
    ) -> Any:
        tools = _sort_tools(tools)
        profile = self.init_kwargs[PROFILE_KEY]
        if PROFILES[profile].typescript_tools:
            # lazy: JSON-tool profiles do not need the installed TypeScript encoder.
            from ._kimi_k2_tools import encode_tools_to_typescript_style

            if tools:
                try:
                    kwargs["tools_ts_str"] = encode_tools_to_typescript_style(tools)
                except Exception:
                    logging.getLogger(__name__).warning("Tool conversion failed; retaining the JSON template fallback")
            if profile == K27:
                kwargs.pop("thinking", None)
                kwargs.pop("preserve_thinking", None)
            else:
                kwargs.setdefault("thinking", True)
                if profile == K26:
                    kwargs.setdefault("preserve_thinking", False)
        return super().apply_chat_template(
            conversation,
            tools=tools,
            tokenize=tokenize,
            add_generation_prompt=add_generation_prompt,
            **kwargs,
        )


def load_k2_tokenizer(
    source: str, *, revision: str | None = None, local_files_only: bool = False, profile: str | None = None
) -> Any:
    """Read pinned data or a saved native reader; checkpoint Python stays inert."""
    root = Path(source)
    selected = profile or get_k2_profile(source)
    if selected is None:
        return AutoTokenizer.from_pretrained(
            source, revision=revision, local_files_only=local_files_only, trust_remote_code=False
        )
    if selected not in PROFILES:
        raise ValueError("K2 tokenizer profile is not supported")
    reviewed = PROFILES[selected]
    if not root.is_dir():
        if get_k2_profile(source) == selected:
            source = reviewed.repository
        if source != reviewed.repository:
            return AutoTokenizer.from_pretrained(
                source, revision=revision, local_files_only=local_files_only, trust_remote_code=False
            )
        revisions = {reviewed.revision}
        if selected == THINKING:
            revisions.add(COOKBOOK_THINKING_REVISION)
        if revision is not None and revision not in revisions:
            raise ValueError("K2 tokenizer revision is not a reviewed data revision")
        # lazy: local tokenizer readers do not need optional Hub downloads.
        from huggingface_hub import snapshot_download

        root = Path(
            snapshot_download(
                repo_id=source,
                revision=revision or reviewed.revision,
                allow_patterns=list(reviewed.source_sha256),
                local_files_only=local_files_only,
            )
        )
    config_path = root / "tokenizer_config.json"
    config = json.loads(config_path.read_text(encoding="utf-8")) if config_path.is_file() else {}
    if not isinstance(config, dict):
        raise ValueError("K2 tokenizer metadata must be a JSON object")
    if not (root / "tiktoken.model").is_file():
        if PROFILE_KEY in config:
            raise ValueError("K2 saved tokenizer vocabulary is missing")
        return AutoTokenizer.from_pretrained(root, local_files_only=True, trust_remote_code=False)
    if PROFILE_KEY in config and config[PROFILE_KEY] != selected:
        raise ValueError("K2 saved tokenizer profile differs from the selected profile")
    if PROFILE_KEY not in config and reviewed.template_sha256 is None and (root / "chat_template.jinja").is_file():
        raise ValueError("K2 tokenizer data differs from the reviewed data: chat_template.jinja")
    expected = (
        {"tiktoken.model": reviewed.source_sha256["tiktoken.model"]}
        if PROFILE_KEY in config
        else reviewed.source_sha256
    )
    for filename, digest in expected.items():
        path = root / filename
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError(f"K2 tokenizer data differs from the reviewed data: {filename}")
    if config.get("tokenizer_class") != "TikTokenTokenizer":
        raise ValueError("K2 tokenizer class declaration is not supported")
    tokenizer = TikTokenTokenizer.from_pretrained(
        root, local_files_only=True, trust_remote_code=False, **{PROFILE_KEY: selected}
    )
    tokenizer.name_or_path = source
    return tokenizer
