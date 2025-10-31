# File: tests/test_utils.py
import unittest
from utils import clamp

class TestUtils(unittest.TestCase):
    def test_clamp(self):
        self.assertEqual(clamp(5, 2, 6), 5)
        self.assertEqual(clamp(1, 2, 6), 2)
        self.assertEqual(clamp(8, 2, 6), 6)

if __name__ == '__main__':
    unittest.main()
