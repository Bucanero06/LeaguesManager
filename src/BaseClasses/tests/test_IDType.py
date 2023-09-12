import unittest
from pydantic import ValidationError

from src.BaseClasses.BaseClasses import FirestoreIDType


class FirestoreIDTypeTest(unittest.TestCase):
    def test_valid_id(self):
        try:
            id_str = FirestoreIDType(value="validID")
            self.assertTrue(True)
        except ValidationError:
            self.assertTrue(False, "Valid ID failed")

    def test_invalid_utf8(self):
        with self.assertRaises(ValueError):
            id_str = FirestoreIDType(value="\ud800")  # This is a lone high surrogate, invalid in UTF-8

    def test_byte_length(self):
        with self.assertRaises(ValueError):
            id_str = FirestoreIDType(value="a" * 1501)  # This will be over 1500 bytes

    def test_forward_slash(self):
        with self.assertRaises(ValueError):
            id_str = FirestoreIDType(value="invalid/id")

    def test_single_period(self):
        with self.assertRaises(ValueError):
            id_str = FirestoreIDType(value=".")

    def test_double_periods(self):
        with self.assertRaises(ValueError):
            id_str = FirestoreIDType(value="..")

    def test_pattern_double_underscores(self):
        with self.assertRaises(ValueError):
            id_str = FirestoreIDType(value="__invalidID__")

    def test_pattern_id_number(self):
        with self.assertRaises(ValueError):
            id_str = FirestoreIDType(value="__id12345__")

    def test_combined_valid(self):
        try:
            id_str = FirestoreIDType(value="__idValidID__12345")
            self.assertTrue(True)
        except ValidationError:
            self.assertTrue(False, "Combined Valid ID failed")

if __name__ == "__main__":
    unittest.main()
