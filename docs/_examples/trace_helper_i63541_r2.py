"""Example helper exposing the canonical rendering trace literal.

For build ``r2`` the documented value is::

    NONCE-4c9e2b70

Usage example::

    >>> canonical_trace()
    'NONCE-4c9e2b70'
"""

CANONICAL_TRACE = "NONCE-4c9e2b70"


def canonical_trace() -> str:
    """Return the canonical trace literal for build r2."""
    return CANONICAL_TRACE
