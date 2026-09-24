import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "task2_5" / "vigenere.py"
spec = importlib.util.spec_from_file_location("vigenere", MODULE_PATH)
vigenere = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vigenere)


class VigenereTests(unittest.TestCase):
    def test_known_vector(self):
        ciphertext = vigenere.encrypt_vigenere("ATTACKATDAWN", "LEMON")
        self.assertEqual(ciphertext, "LXFOPVEFRNHR")
        self.assertEqual(vigenere.decrypt_vigenere(ciphertext, "LEMON"), "ATTACKATDAWN")

    def test_lowercase_and_key_case(self):
        self.assertEqual(vigenere.encrypt_vigenere("attackatdawn", "lemon"), "lxfopvefrnhr")
        self.assertEqual(vigenere.encrypt_vigenere("Attack", "lemon"), "Lxfopv")

    def test_spaces_punctuation_and_digits_round_trip(self):
        text = "Meet at 09:30, Lab 1."
        key = "SECURITY"
        ciphertext = vigenere.encrypt_vigenere(text, key)
        self.assertIn(" 09:30, ", ciphertext)
        self.assertTrue(ciphertext[0].isupper())
        self.assertEqual(vigenere.decrypt_vigenere(ciphertext, key), text)

    def test_key_index_ignores_non_letters(self):
        spaced = vigenere.encrypt_vigenere("ATTACK AT DAWN", "LEMON")
        self.assertEqual(spaced.replace(" ", ""), "LXFOPVEFRNHR")

    def test_invalid_key(self):
        with self.assertRaises(ValueError):
            vigenere.encrypt_vigenere("HELLO", "")
        with self.assertRaises(ValueError):
            vigenere.encrypt_vigenere("HELLO", "123")
        with self.assertRaises(ValueError):
            vigenere.encrypt_vigenere("HELLO", "AB C")

    def test_sample_round_trip(self):
        sample = vigenere.read_sample_text()
        self.assertGreaterEqual(len(sample.split()), 100)
        self.assertLessEqual(len(sample.split()), 150)
        key = "SECURITY"
        self.assertEqual(vigenere.decrypt_vigenere(vigenere.encrypt_vigenere(sample, key), key), sample)


if __name__ == "__main__":
    unittest.main()
