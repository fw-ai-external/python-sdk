"""Helper that returns the pinned trace literal for build r4."""

NONCE_11b8daeb = "NONCE-11b8daea"


def canonical_trace():
    """Return the canonical trace literal.

    >>> canonical_trace()
    'NONCE-11b8daea'
    """
    return NONCE_11b8daeb
