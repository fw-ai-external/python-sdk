"""
Tokenizer Utilities.

The RLOR trainer exposes a tokenizer endpoint that lets you encode text to
token IDs. This uses the same tokenizer as the model being trained, ensuring
consistency between your client-side token handling and the server's.

Copyright (c) Fireworks AI, Inc. and affiliates.
"""

from __future__ import annotations

import httpx


def encode_text(base_url: str, text: str) -> list[int]:
    """Encode text to token IDs using the trainer's tokenizer.

    This calls the RLOR trainer's /api/v1/tokenizer/encode endpoint,
    which uses the same tokenizer as the model being trained.

    Args:
        base_url: RLOR trainer endpoint URL (from RlorServiceEndpoint.base_url)
        text: Text to encode

    Returns:
        List of token IDs
    """
    resp = httpx.post(
        f"{base_url}/api/v1/tokenizer/encode",
        json={"text": text},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["tokens"]
