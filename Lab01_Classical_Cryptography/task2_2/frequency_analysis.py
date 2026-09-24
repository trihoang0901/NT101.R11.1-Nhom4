import json
import re
import sys
from collections import Counter
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CIPHER_PATH = BASE_DIR / "cipher.txt"
MAPPING_PATH = BASE_DIR / "mappings.json"
OUTPUT_DIR = BASE_DIR / "output"
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
UNKNOWN_CHAR = "_"
WORD_PATTERN = re.compile(r"[A-Za-z]+")

SOLVING_STEPS = [
    {
        "hypothesis": "v -> e",
        "pairs": [("v", "e")],
        "reason": (
            "v appears {Vc} times ({Vp:.2f}%), the highest letter frequency "
            "among {total} letters. English text usually has E among the most "
            "frequent letters, so the first hypothesis is v -> e."
        ),
    },
    {
        "hypothesis": "ghv -> the",
        "pairs": [("g", "t"), ("h", "h")],
        "reason": (
            "The word ghv occurs {GHV} times and the trigram GHV occurs {GHV3} times. "
            "With v -> e its pattern is ??e. the is the usual English word of that shape. "
            "g appears {Gc} times ({Gp:.2f}%), close to a typical rate for T, and "
            "h appears {Hc} times ({Hp:.2f}%), plausible for H. "
            "Mappings g -> t and h -> h turn every ghv into the without a conflict."
        ),
    },
    {
        "hypothesis": "ghlg -> that",
        "pairs": [("l", "a")],
        "reason": (
            "The word ghlg occurs {GHLG} times. Known letters make the pattern th?t. "
            "that is the English word that fits, so l -> a. "
            "l appears {Lc} times ({Lp:.2f}%), near a typical rate for A. "
            "The one-letter word l occurs {L} times and then reads as a."
        ),
    },
    {
        "hypothesis": "lmw -> and",
        "pairs": [("m", "n"), ("w", "d")],
        "reason": (
            "lmw is the most frequent word, {LMW} times. With l -> a the pattern is a??. "
            "and is the usual high-frequency three-letter word. "
            "m appears {Mc} times ({Mp:.2f}%) and w appears {Wc} times ({Wp:.2f}%). "
            "Mappings m -> n and w -> d are consistent on every occurrence of lmw."
        ),
    },
    {
        "hypothesis": "zd -> of and gz -> to",
        "pairs": [("z", "o"), ("d", "f")],
        "reason": (
            "zd occurs {ZD} times and is the most frequent two-letter word. "
            "of is the usual candidate. z appears {Zc} times ({Zp:.2f}%), near O, "
            "and d appears {Dc} times ({Dp:.2f}%), near F. "
            "The two-letter word gz occurs {GZ} times and becomes to, which checks the same pair."
        ),
    },
    {
        "hypothesis": "rm -> in, rs -> is, ls -> as",
        "pairs": [("r", "i"), ("s", "s")],
        "reason": (
            "rm occurs {RM} times. With m -> n the pattern is ?n, so in is the candidate and r -> i. "
            "r appears {Rc} times ({Rp:.2f}%). "
            "rs occurs {RS} times and ls occurs {LS} times. "
            "s appears {Sc} times ({Sp:.2f}%). Mapping s -> s turns those words into is and as."
        ),
    },
    {
        "hypothesis": "nzsg -> most",
        "pairs": [("n", "m")],
        "reason": (
            "nzsg occurs {NZSG} times. Known letters give the pattern ?ost. "
            "most fits, so n -> m. n appears {Nc} times ({Np:.2f}%)."
        ),
    },
    {
        "hypothesis": "Hliib Kzggvi -> Harry Potter",
        "pairs": [("i", "r"), ("b", "y"), ("k", "p")],
        "reason": (
            "After the mappings above, the repeated name Hliib Kzggvi reads Ha__ _otte_. "
            "The English name with that pattern is Harry Potter, so i -> r, b -> y, and k -> p. "
            "The same letters turn svirvs, which occurs {SVIRVS} times, into series."
        ),
    },
    {
        "hypothesis": "written, British, books",
        "pairs": [("u", "w"), ("y", "b"), ("p", "k")],
        "reason": (
            "uirggvm now reads ?ritten, so u -> w gives written. "
            "Yirgrsh reads ?ritish, so y -> b gives British. "
            "yzzps reads ?ooks, so p -> k gives books. "
            "yzb then reads boy, which confirms b -> y from the previous step."
        ),
    },
    {
        "hypothesis": "author, Rowling, and g",
        "pairs": [("f", "u"), ("o", "l"), ("t", "g")],
        "reason": (
            "lfghzi reads a?thor, so f -> u gives author. "
            "Izuormt reads Row?in?, so o -> l and t -> g give Rowling. "
            "The same letters turn dzoozus into follows and bzfmt into young."
        ),
    },
    {
        "hypothesis": "seven, wizard, discovers",
        "pairs": [("e", "v"), ("c", "z"), ("x", "c")],
        "reason": (
            "svevm reads se?en, so e -> v gives seven. "
            "urcliw reads wi?ard, so c -> z gives wizard. "
            "wrsxzevis reads disco?ers, so x -> c gives discovers."
        ),
    },
    {
        "hypothesis": "Q.P. -> J.K.",
        "pairs": [("q", "j")],
        "reason": (
            "The initials Q.P. stand beside the author name and now read ?.K. "
            "The name is J.K. Rowling, so q -> j."
        ),
    },
    {
        "hypothesis": "mvjg -> next and fmrafv -> unique",
        "pairs": [("j", "x"), ("a", "q")],
        "reason": (
            "The last unmapped letters are a ({Ac} times, {Ap:.2f}%) and j ({Jc} times, {Jp:.2f}%). "
            "j is more common than a, and in English X is more common than Q. "
            "mvjg reads ne?t, so j -> x gives next. "
            "fmrafv reads uni?ue, so a -> q gives unique. "
            "The same pair gives excellence, equipped, qualified, proximity, and expand. "
            "Three tokens do not match that pair: vakozivw reads eqplored, xznkova reads compleq, "
            "and xzmjfvirmt reads conxuering. In each of those tokens a and j are swapped "
            "relative to the rest of the ciphertext. The mapping stays one-to-one, "
            "so re-encryption still reproduces the original letters."
        ),
    },
]


def is_english_letter(char):
    return ("A" <= char <= "Z") or ("a" <= char <= "z")


def read_ciphertext(path=CIPHER_PATH):
    return Path(path).read_text(encoding="utf-8-sig")


def letter_stream(text):
    return "".join(char.upper() for char in text if is_english_letter(char))


def count_letters(text):
    return Counter(letter_stream(text))


def count_ngrams(text, size):
    stream = letter_stream(text)
    if len(stream) < size:
        return Counter()
    return Counter(stream[index : index + size] for index in range(len(stream) - size + 1))


def count_words(text):
    return Counter(match.group(0).upper() for match in WORD_PATTERN.finditer(text))


def statistics_context(text):
    letter_counts = count_letters(text)
    total = sum(letter_counts.values())
    word_counts = count_words(text)
    context = {"total": total}
    for letter in ALPHABET:
        context[f"{letter}c"] = letter_counts[letter]
        percent = (100 * letter_counts[letter] / total) if total else 0
        context[f"{letter}p"] = percent
    for word in ("GHV", "GHLG", "LMW", "ZD", "GZ", "RM", "RS", "LS", "NZSG", "L", "SVIRVS"):
        context[word] = word_counts[word]
    context["GHV3"] = count_ngrams(text, 3)["GHV"]
    return context


class SubstitutionMapping:
    def __init__(self):
        self.cipher_to_plain = {}

    def add(self, cipher_char, plain_char):
        cipher_char = cipher_char.upper()
        plain_char = plain_char.lower()
        if not is_english_letter(cipher_char) or len(cipher_char) != 1:
            raise ValueError("Cipher symbol must be one letter A-Z")
        if not is_english_letter(plain_char) or len(plain_char) != 1:
            raise ValueError("Plain symbol must be one letter A-Z")
        current = self.cipher_to_plain.get(cipher_char)
        if current == plain_char:
            return
        if current is not None:
            raise ValueError(f"Conflict: {cipher_char} is already mapped to {current}")
        for existing_cipher, existing_plain in self.cipher_to_plain.items():
            if existing_plain == plain_char:
                raise ValueError(
                    f"Conflict: {plain_char} is already mapped from {existing_cipher}"
                )
        self.cipher_to_plain[cipher_char] = plain_char

    def remove(self, cipher_char):
        cipher_char = cipher_char.upper()
        if cipher_char not in self.cipher_to_plain:
            raise ValueError(f"No mapping for {cipher_char}")
        del self.cipher_to_plain[cipher_char]

    def apply(self, text, unknown=UNKNOWN_CHAR):
        output = []
        for char in text:
            if not is_english_letter(char):
                output.append(char)
                continue
            plain = self.cipher_to_plain.get(char.upper())
            if plain is None:
                output.append(unknown)
            elif char.isupper():
                output.append(plain.upper())
            else:
                output.append(plain)
        return "".join(output)

    def inverse(self):
        return {plain: cipher for cipher, plain in self.cipher_to_plain.items()}

    def reencrypt(self, plaintext, unknown=UNKNOWN_CHAR):
        plain_to_cipher = self.inverse()
        output = []
        for char in plaintext:
            if not is_english_letter(char):
                output.append(char)
                continue
            cipher = plain_to_cipher.get(char.lower())
            if cipher is None:
                output.append(unknown)
            elif char.isupper():
                output.append(cipher)
            else:
                output.append(cipher.lower())
        return "".join(output)

    def as_dict(self):
        return {letter.lower(): self.cipher_to_plain[letter] for letter in sorted(self.cipher_to_plain)}


def format_mapping_table(mapping):
    cipher_row = " ".join(ALPHABET)
    plain_row = " ".join(mapping.cipher_to_plain.get(letter, "?").upper() for letter in ALPHABET)
    return f"Cipher : {cipher_row}\nPlain  : {plain_row}"


def ranked_items(counter):
    return sorted(counter.items(), key=lambda item: (-item[1], item[0]))


def format_letter_frequency(text):
    counts = count_letters(text)
    total = sum(counts.values())
    lines = ["Letter frequency", f"Total letters: {total}", "", "Rank  Letter  Count  Percent"]
    ordered = sorted(ALPHABET, key=lambda letter: (-counts[letter], letter))
    for rank, letter in enumerate(ordered, start=1):
        count = counts[letter]
        percent = (100 * count / total) if total else 0
        lines.append(f"{rank:<5} {letter:<7} {count:<6} {percent:.2f}%")
    return "\n".join(lines) + "\n"


def format_ngram_frequency(text, size, title):
    counts = count_ngrams(text, size)
    total = sum(counts.values())
    lines = [title, f"Total {size}-grams: {total}", "", "Rank  Gram  Count  Percent"]
    for rank, (gram, count) in enumerate(ranked_items(counts), start=1):
        if rank > 30:
            break
        percent = (100 * count / total) if total else 0
        lines.append(f"{rank:<5} {gram:<5} {count:<6} {percent:.2f}%")
    return "\n".join(lines) + "\n"


def format_word_frequency(text):
    counts = count_words(text)
    total = sum(counts.values())
    lines = [
        "Word frequency",
        f"Total words: {total}",
        "",
        "Rank  Word        Count  Length  Percent",
    ]
    for rank, (word, count) in enumerate(ranked_items(counts), start=1):
        if rank > 40:
            break
        percent = (100 * count / total) if total else 0
        lines.append(f"{rank:<5} {word:<11} {count:<6} {len(word):<7} {percent:.2f}%")
    return "\n".join(lines) + "\n"


def write_frequency_reports(text, output_dir=OUTPUT_DIR):
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "letter_frequency.txt").write_text(format_letter_frequency(text), encoding="utf-8")
    (output_dir / "bigram_frequency.txt").write_text(
        format_ngram_frequency(text, 2, "Bigram frequency"), encoding="utf-8"
    )
    (output_dir / "trigram_frequency.txt").write_text(
        format_ngram_frequency(text, 3, "Trigram frequency"), encoding="utf-8"
    )
    (output_dir / "word_frequency.txt").write_text(format_word_frequency(text), encoding="utf-8")


def alphabetic_characters(text):
    return "".join(char for char in text if is_english_letter(char))


def verify_round_trip(ciphertext, mapping):
    plaintext = mapping.apply(ciphertext)
    if UNKNOWN_CHAR in plaintext:
        return False, plaintext, mapping.reencrypt(plaintext)
    restored = mapping.reencrypt(plaintext)
    matches = alphabetic_characters(restored) == alphabetic_characters(ciphertext)
    return matches, plaintext, restored


def solve_ciphertext(ciphertext):
    mapping = SubstitutionMapping()
    context = statistics_context(ciphertext)
    blocks = []
    for index, step in enumerate(SOLVING_STEPS, start=1):
        for cipher_char, plain_char in step["pairs"]:
            mapping.add(cipher_char, plain_char)
        added = ", ".join(f"{cipher_char} -> {plain_char}" for cipher_char, plain_char in step["pairs"])
        blocks.append(
            "\n".join(
                [
                    f"STEP {index}",
                    f"Hypothesis: {step['hypothesis']}",
                    f"Mapping added: {added}",
                    f"Reason: {step['reason'].format(**context)}",
                    "Partial plaintext:",
                    mapping.apply(ciphertext).rstrip(),
                    "",
                ]
            )
        )
    passed, plaintext, restored = verify_round_trip(ciphertext, mapping)
    status = "PASS" if passed else "FAIL"
    blocks.append(
        "\n".join(
            [
                "VERIFICATION",
                f"Mapped letters: {len(mapping.cipher_to_plain)}",
                f"Unmapped cipher letters: {''.join(letter for letter in ALPHABET if letter not in mapping.cipher_to_plain) or 'none'}",
                "Check: re-encrypt the plaintext with the inverse mapping.",
                f"Alphabetic ciphertext matches the original: {status}",
                "",
            ]
        )
    )
    return mapping, plaintext, "\n".join(blocks), passed


def save_mapping(mapping, path=MAPPING_PATH):
    path.write_text(json.dumps(mapping.as_dict(), indent=2) + "\n", encoding="utf-8")


def load_mapping(path=MAPPING_PATH):
    mapping = SubstitutionMapping()
    if not Path(path).exists():
        return mapping
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    for cipher_char, plain_char in data.items():
        mapping.add(cipher_char, plain_char)
    return mapping


def write_solution_outputs(ciphertext=None):
    if ciphertext is None:
        ciphertext = read_ciphertext()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_frequency_reports(ciphertext)
    mapping, plaintext, steps, passed = solve_ciphertext(ciphertext)
    save_mapping(mapping)
    (OUTPUT_DIR / "decoding_steps.txt").write_text(steps, encoding="utf-8")
    (OUTPUT_DIR / "plaintext.txt").write_text(plaintext.rstrip() + "\n", encoding="utf-8")
    return passed


def print_frequency_summary(text):
    print(format_letter_frequency(text))
    print(format_ngram_frequency(text, 2, "Bigram frequency"))
    print(format_ngram_frequency(text, 3, "Trigram frequency"))
    print(format_word_frequency(text))


def interactive_cli():
    ciphertext = read_ciphertext()
    mapping = load_mapping()
    while True:
        print("1. Show frequency reports")
        print("2. Show mapping")
        print("3. Add mapping")
        print("4. Remove mapping")
        print("5. Apply mapping")
        print("6. Run recorded steps and write outputs")
        print("7. Verify current mapping")
        print("0. Exit")
        choice = input("Choice: ").strip()
        if choice == "1":
            print_frequency_summary(ciphertext)
        elif choice == "2":
            print(format_mapping_table(mapping))
        elif choice == "3":
            cipher_char = input("Cipher letter: ").strip()
            plain_char = input("Plain letter: ").strip()
            try:
                mapping.add(cipher_char, plain_char)
                save_mapping(mapping)
                print(format_mapping_table(mapping))
            except ValueError as error:
                print(error)
        elif choice == "4":
            cipher_char = input("Cipher letter to remove: ").strip()
            try:
                mapping.remove(cipher_char)
                save_mapping(mapping)
                print(format_mapping_table(mapping))
            except ValueError as error:
                print(error)
        elif choice == "5":
            print(mapping.apply(ciphertext))
        elif choice == "6":
            passed = write_solution_outputs(ciphertext)
            mapping = load_mapping()
            print("PASS" if passed else "FAIL")
        elif choice == "7":
            passed, plaintext, _restored = verify_round_trip(ciphertext, mapping)
            print("PASS" if passed else "FAIL")
            print(plaintext[:500])
        elif choice == "0":
            return
        else:
            print("Invalid choice")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        passed = write_solution_outputs()
        print("PASS" if passed else "FAIL")
        print(format_mapping_table(load_mapping()))
        return
    interactive_cli()


if __name__ == "__main__":
    main()
