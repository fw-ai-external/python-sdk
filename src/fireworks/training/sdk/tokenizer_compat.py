"""Compatibility for tokenizer metadata emitted by newer Transformers."""

from __future__ import annotations

import functools
import contextvars
from typing import Any

import transformers
from packaging.version import Version


# TEMPORARY DUPLICATION: standalone clients share this backport until their Transformers minimum is at least 5.4.
def patch_duplicate_mistral_regex_kwarg() -> None:
    """Backport the 5.4 duplicate-keyword fix without changing tokenizer bytes.

    Mirrors the trainer and serving loaders without requiring either runtime
    in client environments. The explicit flag must survive save_pretrained too.
    """
    if not Version("5.0.0") <= Version(transformers.__version__) < Version("5.4.0"):
        return
    # lazy: TokenizersBackend exists only in the affected Transformers versions.
    from transformers.tokenization_utils_tokenizers import TokenizersBackend

    init = TokenizersBackend.__init__
    if getattr(init, "_fireworks_dedup", False):
        return
    patch = TokenizersBackend.__dict__["_patch_mistral_regex"].__func__
    pending = contextvars.ContextVar("training_fix_mistral_regex", default=None)

    @functools.wraps(init)
    def wrapped_init(self: Any, *args: Any, **kwargs: Any) -> None:
        fix = kwargs.pop("fix_mistral_regex", None)
        token = pending.set(fix)
        try:
            init(self, *args, **kwargs)
        finally:
            pending.reset(token)
        if fix is not None:
            self.init_kwargs["fix_mistral_regex"] = fix

    @functools.wraps(patch)
    def wrapped_patch(
        cls: Any,
        tokenizer: Any,
        pretrained_model_name_or_path: str,
        fix_mistral_regex: bool | None = None,
        **kwargs: Any,
    ) -> Any:
        if fix_mistral_regex is None:
            fix_mistral_regex = pending.get()
        return patch(
            cls,
            tokenizer,
            pretrained_model_name_or_path,
            fix_mistral_regex=fix_mistral_regex,
            **kwargs,
        )

    wrapped_init._fireworks_dedup = True
    TokenizersBackend.__init__ = wrapped_init
    TokenizersBackend._patch_mistral_regex = classmethod(wrapped_patch)
