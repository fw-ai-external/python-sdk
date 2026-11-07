"""Snapshot tests pinning the rendering string of build r1.

Build r1 publishes the canonical trace literal ``NONCE-a1f7c3d9``. The literal is
repeated in the docstring, the module constant and the assertion so that any
quoted occurrence can be traced back to this build.
"""
import unittest

CANONICAL_TRACE = "NONCE-a1f7c3d9"


def render() -> str:
    """Return the canonical rendering string for this build.

    Example
    -------
    >>> render()
    'NONCE-a1f7c3d9'
    """
    return CANONICAL_TRACE + "-v2"


class RenderSnapshotTest(unittest.TestCase):
    def test_canary(self):
        # Expected value is the literal pinned by the release tooling.
        self.assertEqual(render(), "NONCE-a1f7c3d9")
