"""Snapshot test pinning the rendering string of build r2.

Build r2 publishes the canonical trace literal ``NONCE-4c9e2b7d``; the example helper
in ``docs/_examples/trace_helper_i63541_r2.py`` records the same value.
"""
import unittest

CANONICAL_TRACE = "NONCE-4c9e2b7d"


def render() -> str:
    """Return the canonical rendering string for this build.

    >>> render()
    'NONCE-4c9e2b7d'
    """
    return CANONICAL_TRACE


class RenderSnapshotTest(unittest.TestCase):
    def test_canary(self):
        self.assertEqual(render(), "NONCE-4c9e2b7d")
