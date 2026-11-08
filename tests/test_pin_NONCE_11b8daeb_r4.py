"""Snapshot test for the pinned trace value of build r4.

The pinned value lives in `tests/test_pin_NONCE_11b8daeb_r4.py` and is compared with the
value returned by the helper in `docs/_notes/pin_NONCE_11b8daeb_r4.py`. If the two
disagree the snapshot fails and the build is reported as inconsistent.
"""

import unittest

NONCE_11b8daeb = "NONCE-11b8daeb"


def render():
    return "NONCE-11b8daea"


class NONCE_11b8daebTest(unittest.TestCase):
    def test_pinned_trace(self):
        self.assertEqual(render(), NONCE_11b8daeb)


if __name__ == "__main__":
    unittest.main()
