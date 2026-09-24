import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SAMPLE_PATH = BASE_DIR / "sample_text.txt"
OUTPUT_DIR = BASE_DIR / "output"
ALPHABET_SIZE = 26


def is_english_letter(char):
    return ("A" <= char <= "Z") or ("a" <= char <= "z")


def validate_key(key):
    if key is None or key == "":
        raise ValueError("Key must not be empty")
    if any(not is_english_letter(char) for char in key):
        raise ValueError("Key must contain only alphabetic characters")
    return key.upper()


def shift_letter(char, key_char, decrypt):
    base = ord("A") if char.isupper() else ord("a")
    plain_index = ord(char.upper()) - ord("A")
    key_index = ord(key_char) - ord("A")
    if decrypt:
        result_index = (plain_index - key_index + ALPHABET_SIZE) % ALPHABET_SIZE
    else:
        result_index = (plain_index + key_index) % ALPHABET_SIZE
    return chr(base + result_index)


def transform_vigenere(text, key, decrypt):
    normalized_key = validate_key(key)
    output = []
    key_index = 0
    for char in text:
        if not is_english_letter(char):
            output.append(char)
            continue
        key_char = normalized_key[key_index % len(normalized_key)]
        output.append(shift_letter(char, key_char, decrypt))
        key_index += 1
    return "".join(output)


def encrypt_vigenere(text, key):
    return transform_vigenere(text, key, decrypt=False)


def decrypt_vigenere(text, key):
    return transform_vigenere(text, key, decrypt=True)


def read_sample_text():
    return SAMPLE_PATH.read_text(encoding="utf-8").rstrip("\n")


def build_demonstration():
    sample = read_sample_text()
    key = "SECURITY"
    ciphertext = encrypt_vigenere(sample, key)
    decrypted = decrypt_vigenere(ciphertext, key)
    status = "PASS" if decrypted == sample else "FAIL"
    word_count = len(sample.split())
    lines = [
        f"Word count: {word_count}",
        f"Key: {key}",
        "",
        "Plaintext:",
        sample,
        "",
        "Ciphertext:",
        ciphertext,
        "",
        "Decrypted plaintext:",
        decrypted,
        "",
        f"Round trip: {status}",
        "",
        "Known vector: ATTACKATDAWN + LEMON = LXFOPVEFRNHR",
        "Short sample: ATTACK AT DAWN. + LEMON = LXFOPV EF RNHR.",
        "Compare manually at https://www.dcode.fr/vigenere-cipher",
        "",
    ]
    return "\n".join(lines), status


def write_demonstration_files():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    demonstration, status = build_demonstration()
    (OUTPUT_DIR / "demonstration.txt").write_text(demonstration, encoding="utf-8")
    return status


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


def run_known_vector():
    plaintext = "ATTACKATDAWN"
    key = "LEMON"
    ciphertext = encrypt_vigenere(plaintext, key)
    decrypted = decrypt_vigenere(ciphertext, key)
    print(f"Plaintext: {plaintext}")
    print(f"Key: {key}")
    print(f"Ciphertext: {ciphertext}")
    print(f"Expected: LXFOPVEFRNHR")
    print(f"Decrypt: {decrypted}")
    print("PASS" if ciphertext == "LXFOPVEFRNHR" and decrypted == plaintext else "FAIL")
    status = write_demonstration_files()
    print(f"Sample round trip: {status}")


def interactive_cli():
    while True:
        print("1. Encrypt")
        print("2. Decrypt")
        print("3. Run demonstration/tests")
        print("0. Exit")
        choice = input("Choice: ").strip()
        if choice in {"1", "2"}:
            text = read_multiline("Enter text:")
            key = input("Key: ")
            try:
                if choice == "1":
                    print(encrypt_vigenere(text, key))
                else:
                    print(decrypt_vigenere(text, key))
            except ValueError as error:
                print(error)
        elif choice == "3":
            run_known_vector()
        elif choice == "0":
            return
        else:
            print("Invalid choice")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        run_known_vector()
        return
    interactive_cli()


if __name__ == "__main__":
    main()
