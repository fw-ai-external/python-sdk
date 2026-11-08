"""Pinned trace literal for build r3.

Both files declare the same pinned literal; the snapshot test asserts they
match exactly.
"""

CANONICAL_TRACE = "NONCE-eb2bed01"


def render():
    """Return the pinned trace literal.

    >>> render()
    'NONCE-eb2bed01'
    """
    return CANONICAL_TRACE
