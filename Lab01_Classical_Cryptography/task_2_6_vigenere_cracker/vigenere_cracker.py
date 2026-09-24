from collections import Counter


ENGLISH_FREQ = {
    'a': 8.167,
    'b': 1.492,
    'c': 2.782,
    'd': 4.253,
    'e': 12.702,
    'f': 2.228,
    'g': 2.015,
    'h': 6.094,
    'i': 6.966,
    'j': 0.153,
    'k': 0.772,
    'l': 4.025,
    'm': 2.406,
    'n': 6.749,
    'o': 7.507,
    'p': 1.929,
    'q': 0.095,
    'r': 5.987,
    's': 6.327,
    't': 9.056,
    'u': 2.758,
    'v': 0.978,
    'w': 2.360,
    'x': 0.150,
    'y': 1.974,
    'z': 0.074,
}


def clean_text(text: str) -> str:
    return ''.join(
        ch.lower()
        for ch in text
        if ch.isalpha()
    )


def index_of_coincidence(text: str) -> float:
    n = len(text)

    if n <= 1:
        return 0.0

    counts = Counter(text)

    numerator = sum(
        count * (count - 1)
        for count in counts.values()
    )

    denominator = n * (n - 1)

    return numerator / denominator


def average_ic_for_key_length(ciphertext: str, key_length: int) -> float:
    columns = [
        ciphertext[i::key_length]
        for i in range(key_length)
    ]

    ics = [
        index_of_coincidence(column)
        for column in columns
        if len(column) > 1
    ]

    if not ics:
        return 0.0

    return sum(ics) / len(ics)


def find_key_lengths(ciphertext: str, max_key_length: int = 20):
    results = []

    for key_length in range(1, max_key_length + 1):
        score = average_ic_for_key_length(
            ciphertext,
            key_length
        )

        results.append((key_length, score))

    results.sort(
        key=lambda x: x[1],
        reverse=True
    )

    return results


def chi_squared_for_shift(column: str, shift: int) -> float:
    n = len(column)

    if n == 0:
        return float("inf")

    observed = [0] * 26

    for ch in column:
        decrypted_value = (
            ord(ch) - ord('a') - shift
        ) % 26

        observed[decrypted_value] += 1

    chi_square = 0.0

    for i in range(26):
        letter = chr(ord('a') + i)

        expected = (
            ENGLISH_FREQ[letter] / 100
        ) * n

        if expected > 0:
            chi_square += (
                (observed[i] - expected) ** 2
            ) / expected

    return chi_square


def find_key_for_length(ciphertext: str, key_length: int) -> str:
    key = []

    for position in range(key_length):

        column = ciphertext[position::key_length]

        scores = [
            chi_squared_for_shift(
                column,
                shift
            )
            for shift in range(26)
        ]

        best_shift = min(
            range(26),
            key=lambda shift: scores[shift]
        )

        key.append(
            chr(ord('a') + best_shift)
        )

    return ''.join(key)


def vigenere_decrypt(
    ciphertext: str,
    key: str
) -> str:
    result = []

    key = key.lower()

    key_index = 0

    for ch in ciphertext:

        if ch.isalpha():

            key_shift = (
                ord(key[key_index % len(key)])
                - ord('a')
            )

            plain_value = (
                ord(ch.lower())
                - ord('a')
                - key_shift
            ) % 26

            result.append(
                chr(ord('a') + plain_value)
            )

            key_index += 1

        else:
            result.append(ch)

    return ''.join(result)


def score_plaintext(text: str) -> float:
    common_words = [
        "the",
        "and",
        "that",
        "have",
        "for",
        "with",
        "this",
        "from",
        "computer",
        "science",
        "information",
        "cryptography",
        "security",
        "digital",
        "communication",
        "internet",
        "data",
        "key",
        "algorithm",
        "privacy",
    ]

    text_lower = text.lower()

    score = 0.0

    for word in common_words:

        occurrences = text_lower.count(word)

        score += occurrences * len(word) * 5

    common_patterns = [
        " th",
        "he ",
        "ing",
        "ion",
        "tion",
        "the",
        "and",
        " of ",
        " to ",
        " in ",
    ]

    for pattern in common_patterns:
        score += text_lower.count(pattern) * 2

    bad_patterns = [
        "qz",
        "qx",
        "jx",
        "qk",
        "zx",
        "jq",
    ]

    for pattern in bad_patterns:
        score -= text_lower.count(pattern) * 3

    return score


def crack_vigenere(
    ciphertext: str,
    max_key_length: int = 20
):
    clean_ciphertext = clean_text(ciphertext)

    key_length_candidates = find_key_lengths(
        clean_ciphertext,
        max_key_length
    )

    print("\n=== KEY LENGTH CANDIDATES ===")

    for length, ic_value in key_length_candidates[:10]:
        print(
            f"Length = {length:2d}, "
            f"Average IC = {ic_value:.6f}"
        )

    candidates = []

    for key_length, ic_value in key_length_candidates[:10]:

        key = find_key_for_length(
            clean_ciphertext,
            key_length
        )

        plaintext = vigenere_decrypt(
            ciphertext,
            key
        )

        plaintext_score = score_plaintext(
            plaintext
        )

        candidates.append(
            (
                plaintext_score,
                key_length,
                ic_value,
                key,
                plaintext,
            )
        )

    candidates.sort(
        key=lambda x: x[0],
        reverse=True
    )

    print("\n=== TOP CANDIDATES ===")

    for (
        score,
        key_length,
        ic_value,
        key,
        plaintext
    ) in candidates[:5]:

        print("\n---------------------------")
        print(f"Key length : {key_length}")
        print(f"IC         : {ic_value:.6f}")
        print(f"Key        : {key}")
        print(f"Score      : {score}")

        print("\nPlaintext preview:")
        print(plaintext[:300])

    return candidates[0]


def main():
    input_file = "ciphertext.txt"

    try:
        with open(
            input_file,
            "r",
            encoding="utf-8"
        ) as file:

            ciphertext = file.read()

    except FileNotFoundError:
        print(
            f"Cannot find {input_file}"
        )
        return

    print("=== VIGENERE CRACKER ===")
    print(f"Ciphertext length: {len(clean_text(ciphertext))}")

    (
        score,
        key_length,
        ic_value,
        key,
        plaintext
    ) = crack_vigenere(
        ciphertext,
        max_key_length=20
    )

    print("\n================================")
    print("BEST RESULT")
    print("================================")

    print(f"Key length : {key_length}")
    print(f"Key        : {key}")
    print(f"IC         : {ic_value:.6f}")
    print(f"Score      : {score}")

    print("\nPlaintext:")
    print(plaintext)


if __name__ == "__main__":
    main()