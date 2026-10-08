import argparse
import math
import secrets
import sys

SMALL_PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41)
DETERMINISTIC_LIMIT = 3317044064679887385961981
EXTRA_RANDOM_BASES = 20
MERSENNE_COUNT = 10
LARGEST_PRIMES_COUNT = 10
RANDOM_PRIME_BITS = (8, 16, 64)
EXAMPLE_EXPONENT_DIGITS = 100


def miller_rabin_witness(n, base, d, s):
    x = pow(base, d, n)
    if x == 1 or x == n - 1:
        return False
    for _ in range(s - 1):
        x = x * x % n
        if x == n - 1:
            return False
    return True


def is_deterministic_range(n):
    return n < DETERMINISTIC_LIMIT


def is_prime(n):
    if n < 2:
        return False
    for p in SMALL_PRIMES:
        if n == p:
            return True
        if n % p == 0:
            return False
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    bases = list(SMALL_PRIMES)
    if not is_deterministic_range(n):
        bases += [secrets.randbelow(n - 3) + 2 for _ in range(EXTRA_RANDOM_BASES)]
    return not any(miller_rabin_witness(n, base, d, s) for base in bases)


def random_prime(bits):
    if bits < 2:
        raise ValueError("số bit phải từ 2 trở lên")
    while True:
        candidate = secrets.randbits(bits) | (1 << (bits - 1)) | 1
        if is_prime(candidate):
            return candidate


def lucas_lehmer(p):
    if p == 2:
        return True
    m = (1 << p) - 1
    s = 4
    for _ in range(p - 2):
        s = (s * s - 2) % m
    return s == 0


def mersenne_exponents(count):
    exponents = []
    p = 2
    while len(exponents) < count:
        if is_prime(p) and lucas_lehmer(p):
            exponents.append(p)
        p += 1
    return exponents


def largest_primes_below(limit, count):
    primes = []
    n = limit - 1
    while len(primes) < count and n >= 2:
        if is_prime(n):
            primes.append(n)
        n -= 1
    return primes


def gcd(a, b):
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a


def mod_pow(base, exponent, modulus):
    if modulus <= 0:
        raise ValueError("mô-đun p phải là số dương")
    if exponent < 0:
        raise ValueError("số mũ không được âm")
    result = 1 % modulus
    base %= modulus
    while exponent:
        if exponent & 1:
            result = result * base % modulus
        base = base * base % modulus
        exponent >>= 1
    return result


def describe_primality(n):
    mode = "xác định" if is_deterministic_range(n) else "xác suất"
    verdict = "là số nguyên tố" if is_prime(n) else "là hợp số"
    return f"{n} {verdict} (Miller-Rabin {mode})"


def demo_primes():
    print("== 1a. Số nguyên tố ngẫu nhiên ==")
    for bits in RANDOM_PRIME_BITS:
        p = random_prime(bits)
        print(f"Số nguyên tố {bits} bit: {p}  (độ dài {p.bit_length()} bit)")

    exponents = mersenne_exponents(MERSENNE_COUNT)
    tenth = (1 << exponents[-1]) - 1
    print("\n== 1b. 10 số nguyên tố lớn nhất nhỏ hơn số nguyên tố Mersenne thứ 10 ==")
    print(f"Các số mũ Mersenne (Lucas-Lehmer): {exponents}")
    print(f"Số nguyên tố Mersenne thứ 10: 2^{exponents[-1]} - 1 = {tenth}")
    for rank, p in enumerate(largest_primes_below(tenth, LARGEST_PRIMES_COUNT), start=1):
        print(f"{rank:>2}. {p}  (2^{exponents[-1]} - 1 - {tenth - p})")

    print("\n== 1c. Kiểm tra số nguyên tố với n tùy ý nhỏ hơn 2^89 - 1 ==")
    samples = [
        1,
        561,
        2147483647,
        (1 << 61) - 1,
        (1 << 67) - 1,
        random_prime(44) * random_prime(44),
        (1 << 88) + 7,
        tenth - 2,
    ]
    for n in samples:
        print(describe_primality(n))


def demo_gcd():
    print("\n== 2. Ước chung lớn nhất (GCD) của hai số nguyên lớn ==")
    common = random_prime(512) * random_prime(256)
    a = common * random_prime(1024)
    b = common * random_prime(1024)
    result = gcd(a, b)
    print(f"a: {a.bit_length()} bit, b: {b.bit_length()} bit")
    print(f"gcd(a, b): {result.bit_length()} bit, bằng ước chung đã cài sẵn: {result == common}")
    print(f"khớp với math.gcd: {result == math.gcd(a, b)}")
    print(f"gcd(1071, 462) = {gcd(1071, 462)}")


def demo_mod_pow():
    print("\n== 3. Lũy thừa modulo a^x mod p ==")
    print(f"7^40 mod 19 = {mod_pow(7, 40, 19)}  (đối chiếu pow: {pow(7, 40, 19)})")
    modulus = (1 << 89) - 1
    exponent = 10 ** EXAMPLE_EXPONENT_DIGITS
    result = mod_pow(3, exponent, modulus)
    print(f"3^(10^{EXAMPLE_EXPONENT_DIGITS}) mod (2^89 - 1) = {result}")
    print(f"khớp với pow: {result == pow(3, exponent, modulus)}")
    p = random_prime(64)
    print(f"Kiểm tra Fermat, 5^({p} - 1) mod {p} = {mod_pow(5, p - 1, p)}")


def run_demo():
    demo_primes()
    demo_gcd()
    demo_mod_pow()


def parse_int(text):
    return int(text, 0)


def build_parser():
    parser = argparse.ArgumentParser(description="Số nguyên tố, ước chung lớn nhất và lũy thừa modulo.")
    commands = parser.add_subparsers(dest="command")
    commands.add_parser("demo", help="chạy mọi yêu cầu của bài")
    command = commands.add_parser("random-prime", help="số nguyên tố ngẫu nhiên có độ dài bit cho trước")
    command.add_argument("bits", type=int)
    commands.add_parser("top-primes", help="10 số nguyên tố lớn nhất nhỏ hơn số nguyên tố Mersenne thứ 10")
    command = commands.add_parser("is-prime", help="kiểm tra số nguyên tố")
    command.add_argument("n", type=parse_int)
    command = commands.add_parser("gcd", help="ước chung lớn nhất")
    command.add_argument("a", type=parse_int)
    command.add_argument("b", type=parse_int)
    command = commands.add_parser("modpow", help="a^x mod p")
    command.add_argument("a", type=parse_int)
    command.add_argument("x", type=parse_int)
    command.add_argument("p", type=parse_int)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        if args.command in (None, "demo"):
            run_demo()
        elif args.command == "random-prime":
            print(random_prime(args.bits))
        elif args.command == "top-primes":
            tenth = (1 << mersenne_exponents(MERSENNE_COUNT)[-1]) - 1
            for p in largest_primes_below(tenth, LARGEST_PRIMES_COUNT):
                print(p)
        elif args.command == "is-prime":
            print(describe_primality(args.n))
        elif args.command == "gcd":
            print(gcd(args.a, args.b))
        elif args.command == "modpow":
            print(mod_pow(args.a, args.x, args.p))
    except ValueError as error:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())
