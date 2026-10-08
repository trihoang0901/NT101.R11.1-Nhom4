import contextlib
import importlib.util
import io
import math
import random
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "task2_6" / "number_theory.py"
spec = importlib.util.spec_from_file_location("number_theory", MODULE_PATH)
number_theory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(number_theory)

try:
    import sympy
except ImportError:
    sympy = None

MERSENNE_89 = (1 << 89) - 1


def sieve(limit):
    flags = bytearray([1]) * (limit + 1)
    flags[0:2] = b"\x00\x00"
    for i in range(2, int(limit ** 0.5) + 1):
        if flags[i]:
            flags[i * i::i] = bytearray(len(flags[i * i::i]))
    return [i for i, f in enumerate(flags) if f]


class PrimalityTests(unittest.TestCase):
    def test_matches_sieve_below_10000(self):
        primes = set(sieve(10000))
        for n in range(-5, 10001):
            self.assertEqual(number_theory.is_prime(n), n in primes, n)

    def test_carmichael_and_strong_pseudoprimes_are_composite(self):
        for n in (561, 1105, 41041, 3215031751, 3825123056546413051):
            self.assertFalse(number_theory.is_prime(n), n)

    def test_mersenne_numbers(self):
        prime_exponents = {2, 3, 5, 7, 13, 17, 19, 31, 61, 89}
        for p in range(2, 90):
            if number_theory.is_prime(p):
                self.assertEqual(number_theory.is_prime((1 << p) - 1), p in prime_exponents, p)

    def test_known_large_primes(self):
        self.assertTrue(number_theory.is_prime((1 << 61) - 1))
        self.assertTrue(number_theory.is_prime(MERSENNE_89))
        self.assertFalse(number_theory.is_prime(193707721 * 761838257287))

    def test_deterministic_range_boundary(self):
        self.assertTrue(number_theory.is_deterministic_range(MERSENNE_89 // 1000))
        self.assertFalse(number_theory.is_deterministic_range(MERSENNE_89))

    @unittest.skipIf(sympy is None, "sympy not installed")
    def test_agrees_with_sympy_near_2_89(self):
        for n in range(MERSENNE_89 - 2000, MERSENNE_89, 2):
            self.assertEqual(number_theory.is_prime(n), sympy.isprime(n), n)


class RandomPrimeTests(unittest.TestCase):
    def test_exact_bit_length_and_primality(self):
        for bits in (8, 16, 64):
            for _ in range(20):
                p = number_theory.random_prime(bits)
                self.assertEqual(p.bit_length(), bits)
                self.assertTrue(number_theory.is_prime(p))

    def test_two_bit_prime(self):
        self.assertIn(number_theory.random_prime(2), (2, 3))

    def test_invalid_bits(self):
        with self.assertRaises(ValueError):
            number_theory.random_prime(1)


class MersenneTests(unittest.TestCase):
    def test_first_ten_exponents(self):
        self.assertEqual(number_theory.mersenne_exponents(10), [2, 3, 5, 7, 13, 17, 19, 31, 61, 89])

    def test_lucas_lehmer(self):
        self.assertTrue(number_theory.lucas_lehmer(89))
        self.assertFalse(number_theory.lucas_lehmer(67))
        self.assertFalse(number_theory.lucas_lehmer(11))

    def test_ten_largest_primes_below_tenth_mersenne(self):
        primes = number_theory.largest_primes_below(MERSENNE_89, 10)
        self.assertEqual(len(primes), 10)
        self.assertEqual(primes, sorted(primes, reverse=True))
        self.assertLess(primes[0], MERSENNE_89)
        self.assertTrue(all(number_theory.is_prime(p) for p in primes))

    @unittest.skipIf(sympy is None, "sympy not installed")
    def test_ten_largest_primes_match_sympy(self):
        expected = []
        n = MERSENNE_89
        for _ in range(10):
            n = sympy.prevprime(n)
            expected.append(n)
        self.assertEqual(number_theory.largest_primes_below(MERSENNE_89, 10), expected)

    def test_small_limit(self):
        self.assertEqual(number_theory.largest_primes_below(20, 3), [19, 17, 13])
        self.assertEqual(number_theory.largest_primes_below(5, 10), [3, 2])


class GcdTests(unittest.TestCase):
    def test_small_values(self):
        self.assertEqual(number_theory.gcd(1071, 462), 21)
        self.assertEqual(number_theory.gcd(17, 5), 1)
        self.assertEqual(number_theory.gcd(0, 9), 9)
        self.assertEqual(number_theory.gcd(9, 0), 9)
        self.assertEqual(number_theory.gcd(0, 0), 0)
        self.assertEqual(number_theory.gcd(-12, 18), 6)

    def test_large_values_match_math_gcd(self):
        rng = random.Random(7)
        for bits in (128, 1024, 4096):
            common = rng.getrandbits(bits) | 1
            a = common * rng.getrandbits(bits)
            b = common * rng.getrandbits(bits)
            self.assertEqual(number_theory.gcd(a, b), math.gcd(a, b))
            self.assertEqual(number_theory.gcd(a, b) % common, 0)


class ModPowTests(unittest.TestCase):
    def test_task_example(self):
        self.assertEqual(number_theory.mod_pow(7, 40, 19), 7)

    def test_matches_builtin_pow(self):
        rng = random.Random(11)
        for _ in range(200):
            base = rng.getrandbits(rng.randint(1, 200))
            exponent = rng.getrandbits(rng.randint(1, 400))
            modulus = rng.getrandbits(rng.randint(2, 200)) + 1
            self.assertEqual(number_theory.mod_pow(base, exponent, modulus), pow(base, exponent, modulus))

    def test_huge_exponent(self):
        exponent = 10 ** 100
        self.assertEqual(number_theory.mod_pow(3, exponent, MERSENNE_89), pow(3, exponent, MERSENNE_89))

    def test_edge_cases(self):
        self.assertEqual(number_theory.mod_pow(5, 0, 7), 1)
        self.assertEqual(number_theory.mod_pow(5, 3, 1), 0)
        self.assertEqual(number_theory.mod_pow(0, 5, 7), 0)
        self.assertEqual(number_theory.mod_pow(-3, 3, 7), pow(-3, 3, 7))

    def test_fermat_little_theorem(self):
        p = number_theory.random_prime(64)
        self.assertEqual(number_theory.mod_pow(5, p - 1, p), 1)

    def test_invalid_arguments(self):
        with self.assertRaises(ValueError):
            number_theory.mod_pow(2, 3, 0)
        with self.assertRaises(ValueError):
            number_theory.mod_pow(2, -1, 7)


class CommandLineTests(unittest.TestCase):
    def run_main(self, argv):
        output, errors = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            code = number_theory.main(argv)
        return code, output.getvalue().strip(), errors.getvalue().strip()

    def test_commands(self):
        self.assertEqual(self.run_main(["gcd", "12", "18"]), (0, "6", ""))
        self.assertEqual(self.run_main(["modpow", "7", "40", "19"]), (0, "7", ""))
        self.assertEqual(self.run_main(["is-prime", "0x61"]), (0, "97 là số nguyên tố (Miller-Rabin xác định)", ""))
        code, output, _ = self.run_main(["random-prime", "8"])
        self.assertEqual(code, 0)
        self.assertTrue(number_theory.is_prime(int(output)))

    def test_top_primes_command(self):
        code, output, _ = self.run_main(["top-primes"])
        self.assertEqual(code, 0)
        self.assertEqual([int(line) for line in output.splitlines()], number_theory.largest_primes_below(MERSENNE_89, 10))

    def test_demo_runs(self):
        code, output, _ = self.run_main(["demo"])
        self.assertEqual(code, 0)
        self.assertIn("7^40 mod 19 = 7", output)
        self.assertIn("khớp với math.gcd: True", output)

    def test_invalid_command_arguments(self):
        self.assertEqual(self.run_main(["modpow", "2", "3", "0"])[0], 1)
        self.assertEqual(self.run_main(["random-prime", "1"])[0], 1)


if __name__ == "__main__":
    unittest.main()
