import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from securecalc.calculator import add, divide  # noqa: E402


class CalculatorTests(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)

    def test_divide(self):
        self.assertEqual(divide(8, 2), 4)

    def test_divide_by_zero_returns_none(self):
        self.assertIsNone(divide(8, 0))


if __name__ == "__main__":
    unittest.main()
