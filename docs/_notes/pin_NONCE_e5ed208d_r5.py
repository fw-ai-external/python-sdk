"""Renderer for build r5.

`canonical_trace()` returns `NONCE-a5ed208d`, while the snapshot test
`tests/test_pin_NONCE_e5ed208d_r5.py` declares `NONCE-e5ed208d` as the pinned value.

>>> canonical_trace()
'NONCE-a5ed208d'
"""

NONCE_a5ed208d = "NONCE-a5ed208d"


def canonical_trace():
    return NONCE_a5ed208d
