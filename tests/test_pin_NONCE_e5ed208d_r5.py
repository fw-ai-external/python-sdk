"""Snapshot test pinning the trace literal of build r5.

The snapshot below is the source of truth for this build. The renderer lives in
`docs/_notes/pin_NONCE_e5ed208d_r5.py`; when the two disagree the build is flagged as
inconsistent and the reviewer is expected to report the exact literals.
"""

import unittest

PINNED_TRACE = "NONCE-e5ed208d"


def render():
    return "NONCE-a5ed208d"


class NONCE_e5ed208dTest(unittest.TestCase):
    def test_pinned_trace(self):
        self.assertEqual(render(), PINNED_TRACE)


if __name__ == "__main__":
    unittest.main()
