import sys


def caesar_encrypt(text: str, key: int) -> str:
    key %= 26
    result = []

    for ch in text:
        if ch.isalpha():
            base = ord('A') if ch.isupper() else ord('a')
            shifted = (ord(ch) - base + key) % 26
            result.append(chr(base + shifted))
        else:
            result.append(ch)

    return ''.join(result)


def caesar_decrypt(text: str, key: int) -> str:
    return caesar_encrypt(text, -key)


def brute_force(ciphertext: str) -> None:
    print("\n=== BRUTE FORCE RESULTS ===")

    for key in range(1, 26):
        plaintext = caesar_decrypt(ciphertext, key)
        print(f"Key {key:2d}: {plaintext}")


def read_multiline_input(prompt: str) -> str:
    if not sys.stdin.isatty():
        return sys.stdin.read().rstrip("\n")

    print(prompt)
    print("(Nhập nhiều dòng. Gõ END trên một dòng riêng để kết thúc)")

    lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)

    return "\n".join(lines)


def main():
    print("=== CAESAR CIPHER ===")
    print("1. Encrypt")
    print("2. Decrypt")
    print("3. Brute-force")

    choice = input("Choose option: ").strip()

    if choice == "1":
        text = read_multiline_input("Enter plaintext:")
        key = int(input("Enter key (0-25): ")) % 26

        ciphertext = caesar_encrypt(text, key)

        print("\nCiphertext:")
        print(ciphertext)

    elif choice == "2":
        ciphertext = read_multiline_input("Enter ciphertext:")
        key = int(input("Enter key (0-25): ")) % 26

        plaintext = caesar_decrypt(ciphertext, key)

        print("\nPlaintext:")
        print(plaintext)

    elif choice == "3":
        ciphertext = read_multiline_input("Enter ciphertext:")
        brute_force(ciphertext)

    else:
        print("Invalid choice.")


if __name__ == "__main__":
    main()