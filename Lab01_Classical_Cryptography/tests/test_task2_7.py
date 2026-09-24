import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "task2_7" / "rail_fence.py"
spec = importlib.util.spec_from_file_location("rail_fence", MODULE_PATH)
rail_fence = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rail_fence)


class RailFenceTests(unittest.TestCase):
    def test_known_vector(self):
        ciphertext = rail_fence.encrypt_rail_fence("DCODEZIGZAG", 3)
        self.assertEqual(ciphertext, "DEZCDZGAOIG")
        self.assertEqual(rail_fence.decrypt_rail_fence(ciphertext, 3), "DCODEZIGZAG")

    def test_rails_two_three_and_four_round_trip(self):
        text = "WEAREDISCOVEREDSAVEYOURSELF"
        for rails in (2, 3, 4):
            ciphertext = rail_fence.encrypt_rail_fence(text, rails)
            self.assertEqual(rail_fence.decrypt_rail_fence(ciphertext, rails), text)

    def test_punctuation_spaces_and_digits(self):
        text = "Room 12, bring key at 09:30."
        ciphertext = rail_fence.encrypt_rail_fence(text, 3)
        self.assertEqual(rail_fence.decrypt_rail_fence(ciphertext, 3), text)
        self.assertIn(" ", ciphertext)
        self.assertIn(",", text)

    def test_empty_text(self):
        self.assertEqual(rail_fence.encrypt_rail_fence("", 3), "")
        self.assertEqual(rail_fence.decrypt_rail_fence("", 4), "")

    def test_rails_at_least_text_length(self):
        self.assertEqual(rail_fence.encrypt_rail_fence("ABC", 3), "ABC")
        self.assertEqual(rail_fence.encrypt_rail_fence("ABC", 10), "ABC")
        self.assertEqual(rail_fence.decrypt_rail_fence("ABC", 10), "ABC")

    def test_invalid_rails(self):
        with self.assertRaises(ValueError):
            rail_fence.encrypt_rail_fence("ABC", 1)
        with self.assertRaises(ValueError):
            rail_fence.decrypt_rail_fence("ABC", 0)
        with self.assertRaises(ValueError):
            rail_fence.encrypt_rail_fence("ABC", -2)


if __name__ == "__main__":
    unittest.main()
