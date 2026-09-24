import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"


def validate_rails(rails):
    if not isinstance(rails, int) or isinstance(rails, bool):
        raise ValueError("Rails must be an integer greater than or equal to 2")
    if rails < 2:
        raise ValueError("Rails must be an integer greater than or equal to 2")


def zig_zag_rail_indexes(length, rails):
    indexes = []
    current_rail = 0
    direction = 1
    for _ in range(length):
        indexes.append(current_rail)
        if current_rail == 0:
            direction = 1
        elif current_rail == rails - 1:
            direction = -1
        current_rail += direction
    return indexes


def encrypt_rail_fence(text, rails):
    validate_rails(rails)
    if text == "":
        return ""
    rails_text = [""] * rails
    for char, rail in zip(text, zig_zag_rail_indexes(len(text), rails)):
        rails_text[rail] += char
    return "".join(rails_text)


def decrypt_rail_fence(ciphertext, rails):
    validate_rails(rails)
    if ciphertext == "":
        return ""
    indexes = zig_zag_rail_indexes(len(ciphertext), rails)
    counts = [indexes.count(rail) for rail in range(rails)]
    rail_chars = []
    position = 0
    for count in counts:
        rail_chars.append(list(ciphertext[position : position + count]))
        position += count
    pointers = [0] * rails
    plaintext = []
    for rail in indexes:
        plaintext.append(rail_chars[rail][pointers[rail]])
        pointers[rail] += 1
    return "".join(plaintext)


def build_demonstration():
    cases = [
        ("DCODEZIGZAG", 3, "DEZCDZGAOIG"),
        ("WE ARE DISCOVERED. FLEE AT ONCE", 3, None),
        ("Room 12, bring key #7 at 09:30.", 4, None),
    ]
    lines = []
    all_passed = True
    for plaintext, rails, expected in cases:
        ciphertext = encrypt_rail_fence(plaintext, rails)
        decrypted = decrypt_rail_fence(ciphertext, rails)
        round_trip = decrypted == plaintext
        known = True if expected is None else ciphertext == expected
        status = "PASS" if round_trip and known else "FAIL"
        all_passed = all_passed and status == "PASS"
        lines.extend(
            [
                f"Plaintext: {plaintext}",
                f"Rails: {rails}",
                f"Ciphertext: {ciphertext}",
                f"Decrypted: {decrypted}",
                f"Result: {status}",
                "",
            ]
        )
    lines.append("Overall: PASS" if all_passed else "Overall: FAIL")
    lines.append("Compare manually at https://www.dcode.fr/rail-fence-cipher")
    lines.append("")
    return "\n".join(lines), all_passed


def write_demonstration_files():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    demonstration, passed = build_demonstration()
    (OUTPUT_DIR / "demonstration.txt").write_text(demonstration, encoding="utf-8")
    return passed


def parse_rails(raw_value):
    try:
        rails = int(raw_value)
    except ValueError as error:
        raise ValueError("Rails must be an integer greater than or equal to 2") from error
    validate_rails(rails)
    return rails


def read_multiline(prompt):
    print(prompt)
    print("End input with an empty line.")
    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)
    return "\n".join(lines)


def run_tests():
    demonstration, passed = build_demonstration()
    print(demonstration)
    write_demonstration_files()
    print("PASS" if passed else "FAIL")


def interactive_cli():
    while True:
        print("1. Encrypt")
        print("2. Decrypt")
        print("3. Run demonstration/tests")
        print("0. Exit")
        choice = input("Choice: ").strip()
        if choice in {"1", "2"}:
            text = read_multiline("Enter text:")
            raw_rails = input("Rails: ")
            try:
                rails = parse_rails(raw_rails)
                if choice == "1":
                    print(encrypt_rail_fence(text, rails))
                else:
                    print(decrypt_rail_fence(text, rails))
            except ValueError as error:
                print(error)
        elif choice == "3":
            run_tests()
        elif choice == "0":
            return
        else:
            print("Invalid choice")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        run_tests()
        return
    interactive_cli()


if __name__ == "__main__":
    main()
