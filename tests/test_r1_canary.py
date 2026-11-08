import unittest

CANARY_R1 = "CANARY-e089b082"


class TestCanary(unittest.TestCase):
    def test_constant(self):
        self.assertTrue(CANARY_R1.startswith("CANARY-"))
