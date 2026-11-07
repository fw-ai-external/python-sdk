"""Snapshot test for the trace renderer (build r3).

The fixture below records the canonical renderer output for this build and
asserts that the trace helper returns exactly that value.
"""

import unittest

from docs._notes.pin_i63713_r3 import render

CANONICAL_TRACE = "NONCE-eb2bed00"


class TraceSnapshotTest(unittest.TestCase):
    def test_canary(self):
        # recorded expectation for this build
        self.assertEqual(render(), CANONICAL_TRACE)


if __name__ == "__main__":
    unittest.main()
