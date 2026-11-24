"""Select reviewed K2 profiles from explicit context or plain data."""

from __future__ import annotations

import json
import hashlib
from pathlib import Path
from dataclasses import dataclass

PROFILE_KEY = "fireworks_kimi_k2_profile"
VOCAB_SHA256 = "b6c497a7469b33ced9c38afb1ad6e47f03f5e5dc05f15930799210ec050c5103"
THINKING = "kimi_k2_thinking_v1"
BASE = "kimi_k2_base_v1"
K25 = "kimi_k25_v1"
K26 = "kimi_k26_v1"
K27 = "kimi_k27_code_v1"
COOKBOOK_THINKING_REVISION = "a51ccc050d73dab088bf7b0e2dd9b30ae85a4e55"


@dataclass(frozen=True)
class K2Profile:
    repository: str
    revision: str
    config_sha256: str
    template_sha256: str | None
    model_id: str
    typescript_tools: bool = False

    @property
    def source_sha256(self) -> dict[str, str]:
        files = {"tiktoken.model": VOCAB_SHA256, "tokenizer_config.json": self.config_sha256}
        if self.template_sha256:
            files["chat_template.jinja"] = self.template_sha256
        return files


PROFILES = {
    THINKING: K2Profile(
        "moonshotai/Kimi-K2-Thinking",
        "612681931a8c906ddb349f8ad0f582cb552189cd",
        "d0a17617078b53af4ff77546d8ef190d28efad6ef2ed0ee69e4b3c97a6f829fd",
        "07a791b8563c5159054394745049c8e487986ecb34aaab77727e1b158bbe6a5c",
        "kimi-k2-thinking",
    ),
    BASE: K2Profile(
        "moonshotai/Kimi-K2-Base",
        "ce72df012259dcc55d945e890f815fe7ef69159c",
        "a4cdd80882ea8c7bb1a0b8710223a2d1ca5dd994eb553679863209c6e905b112",
        None,
        "kimi-k2-base",
    ),
    "kimi_k2_instruct_v1": K2Profile(
        "moonshotai/Kimi-K2-Instruct",
        "fd1984e2b7a3350dbf7305fe73a4ede25c14de50",
        "5ba77d5822137ac3cb9337d2b84561d10425562cf8b8f2c74c91a832516a778d",
        "39e8c195b474c1a4148046f41fedd177b2ff8f420fa376e52fcdddb829e8f0c5",
        "kimi-k2-instruct",
    ),
    "kimi_k2_instruct_0905_v1": K2Profile(
        "moonshotai/Kimi-K2-Instruct-0905",
        "ac6c49f04883bd0a0598b790693a72061c676629",
        "5ba77d5822137ac3cb9337d2b84561d10425562cf8b8f2c74c91a832516a778d",
        "00938c355ca7195fd4f9c923e93af063846d4d5005e06999274f8db57b65bb0b",
        "kimi-k2-instruct-0905",
    ),
    K25: K2Profile(
        "moonshotai/Kimi-K2.5",
        "2426b45b6af0da48d0dcce71bbce6225e5c73adc",
        "12fcab43d2b6068f46769f5ff373960bf7c17a94d7abbc50e2491306b2f6cf58",
        "7c91e4b3578b518bfb388d2e3dc645daf0fbf843656e887db75d12891e0030ff",
        "kimi-k2p5",
        True,
    ),
    K26: K2Profile(
        "moonshotai/Kimi-K2.6",
        "b5aabbfb20227ed42becbf5541dbffd213942c58",
        "12fcab43d2b6068f46769f5ff373960bf7c17a94d7abbc50e2491306b2f6cf58",
        "8bf859698fd4781c0e1e1c63ce74422aab27e53ccc5f47116317c64cda06132f",
        "kimi-k2p6",
        True,
    ),
    K27: K2Profile(
        "moonshotai/Kimi-K2.7-Code",
        "74797c9c62378b951a1f6fcf5c4631024e9b8bef",
        "6dfafeacca3d44748fc4a2fcc6725be5ea616ecc5b95f5a8b4277077c06e7d9f",
        "8d21200dff7e85beaf51c8b110952e039ffd0779f615d64d63293d74773360f9",
        "kimi-k2p7-code",
        True,
    ),
}


def _context_profile(name: str | None) -> str | None:
    if name:
        if Path(name).is_dir():
            return get_k2_profile(name)
        value = name.strip().rstrip("/").lower()
        if value == "moonshotai/kimi-k2.5-text-only":
            return K25
        for key, profile in PROFILES.items():
            if value in {profile.repository.lower(), profile.model_id, f"accounts/fireworks/models/{profile.model_id}"}:
                return key
    return None


def get_k2_profile(source: str, *, base_model: str | None = None) -> str | None:
    """Context only restricts loading; folder spelling never establishes identity."""
    # A known tokenizer override owns its profile; the base is only a fallback.
    root = Path(source)
    if not root.is_dir():
        return _context_profile(source) or _context_profile(base_model)
    try:
        path = root / "tokenizer_config.json"
        config = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
        if not isinstance(config, dict):
            return _context_profile(base_model)
        if PROFILE_KEY in config:
            return str(config[PROFILE_KEY])
        config_digest = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
        template = root / "chat_template.jinja"
        template_digest = hashlib.sha256(template.read_bytes()).hexdigest() if template.is_file() else None
        for key, profile in PROFILES.items():
            if (config_digest, template_digest) == (profile.config_sha256, profile.template_sha256):
                return key
        model_path = root / "config.json"
        model_config = json.loads(model_path.read_text(encoding="utf-8")) if model_path.is_file() else {}
        if isinstance(model_config, dict) and model_config.get("model_type") in {"kimi_k2", "kimi_k25"}:
            # Restrict unknown K2 data without assigning another profile's semantics.
            return "unreviewed_kimi_k2"
    except (OSError, UnicodeError, ValueError):
        pass
    return _context_profile(base_model)
