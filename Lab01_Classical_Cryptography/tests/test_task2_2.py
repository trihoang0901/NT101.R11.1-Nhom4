import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "task2_2" / "frequency_analysis.py"
spec = importlib.util.spec_from_file_location("frequency_analysis", MODULE_PATH)
frequency_analysis = importlib.util.module_from_spec(spec)
spec.loader.exec_module(frequency_analysis)


class FrequencyAndMappingTests(unittest.TestCase):
    def test_letter_counts_ignore_case_and_punctuation(self):
        counts = frequency_analysis.count_letters("AbC, a!")
        self.assertEqual(counts["A"], 2)
        self.assertEqual(counts["B"], 1)
        self.assertEqual(counts["C"], 1)
        self.assertEqual(sum(counts.values()), 4)

    def test_apply_mapping_keeps_punctuation_and_case(self):
        mapping = frequency_analysis.SubstitutionMapping()
        mapping.add("a", "x")
        mapping.add("b", "y")
        self.assertEqual(mapping.apply("A, b!"), "X, y!")

    def test_mapping_conflict_on_cipher_letter(self):
        mapping = frequency_analysis.SubstitutionMapping()
        mapping.add("v", "e")
        with self.assertRaises(ValueError):
            mapping.add("v", "a")

    def test_mapping_conflict_on_plain_letter(self):
        mapping = frequency_analysis.SubstitutionMapping()
        mapping.add("v", "e")
        with self.assertRaises(ValueError):
            mapping.add("g", "e")

    def test_recorded_solution_restores_ciphertext(self):
        ciphertext = frequency_analysis.read_ciphertext()
        mapping, plaintext, _steps, passed = frequency_analysis.solve_ciphertext(ciphertext)
        self.assertTrue(passed)
        self.assertNotIn("_", plaintext)
        self.assertEqual(len(mapping.cipher_to_plain), 26)
        restored = mapping.reencrypt(plaintext)
        self.assertEqual(
            frequency_analysis.alphabetic_characters(restored),
            frequency_analysis.alphabetic_characters(ciphertext),
        )
        self.assertIn("Harry Potter", plaintext)
        self.assertIn(",", plaintext)
        self.assertIn("11th", plaintext)


if __name__ == "__main__":
    unittest.main()
