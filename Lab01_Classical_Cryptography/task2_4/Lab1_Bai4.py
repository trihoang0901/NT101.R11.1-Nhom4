
import string

def prepare_text(text):
    # Chuyen in hoa, bo khoang trang va dau cau, thay J thanh I
    text = text.upper().replace('J', 'I')
    return ''.join(filter(str.isalpha, text))

def create_matrix(key):
    key = prepare_text(key)

    matrix_1d = []
    used = set()

    # Them ky tu cua Key vao ma tran (khong trung lap)
    for char in key:
        if char not in used:
            matrix_1d.append(char)
            used.add(char)

    # Them cac chu cai con lai trong bang chu cai (bo J)
    for char in string.ascii_uppercase:
        if char == 'J':
            continue

        if char not in used:
            matrix_1d.append(char)
            used.add(char)

    # Chuyen mang 1D thanh ma tran 2D (5x5)
    return [matrix_1d[i:i + 5] for i in range(0, 25, 5)]

def print_matrix(matrix):
    print("\n--- Ma tran Playfair 5x5 ---")

    for row in matrix:
        print(" ".join(row))

    print("----------------------------\n")

def find_position(matrix, char):
    for r in range(5):
        for c in range(5):
            if matrix[r][c] == char:
                return r, c

    return -1, -1

def playfair_cipher(text, matrix, encrypt=True):

    # Xu ly dau vao: viet lien, in hoa, bo ky tu dac biet
    text = prepare_text(text)

    # Neu ma hoa va so ky tu le thi them X vao cuoi
    if encrypt and len(text) % 2 != 0:
        text += 'X'

    result = ""

    # Ma hoa: dich sang phai va xuong duoi
    # Giai ma: dich sang trai va len tren
    shift = 1 if encrypt else -1

    # Xu ly tung cap 2 ky tu lien tiep nhau
    for i in range(0, len(text), 2):

        char1 = text[i]
        char2 = text[i + 1]

        r1, c1 = find_position(matrix, char1)
        r2, c2 = find_position(matrix, char2)

        # Neu 2 ky tu nam cung dong
        if r1 == r2:
            result += matrix[r1][(c1 + shift) % 5]
            result += matrix[r2][(c2 + shift) % 5]

        # Neu 2 ky tu nam cung cot
        elif c1 == c2:
            result += matrix[(r1 + shift) % 5][c1]
            result += matrix[(r2 + shift) % 5][c2]

        # Neu 2 ky tu tao thanh hinh chu nhat
        else:
            result += matrix[r1][c2]
            result += matrix[r2][c1]

    # Neu giai ma va ket qua co X o cuoi thi bo X
    if not encrypt and result.endswith('X'):
        result = result[:-1]

    return result

def main():

    print("=== CHUONG TRINH MA HOA/GIAI MA PLAYFAIR CIPHER ===")

    # Nhap khoa
    key = input("Nhap khoa (Key): ")

    # Tao ma tran
    matrix = create_matrix(key)

    # In ma tran
    print_matrix(matrix)

    print("Ban muon lam gi?")
    print("1. Ma hoa (Encrypt)")
    print("2. Giai ma (Decrypt)")

    choice = input("Lua chon (1/2): ").strip()

    # Ma hoa
    if choice == '1':

        # Nhap ban ro
        plaintext = input("Nhap ban ro (Plaintext): ")

        ciphertext = playfair_cipher(
            plaintext,
            matrix,
            encrypt=True
        )

        print("\n==================== KET QUA ====================")
        print("Ciphertext:", ciphertext)
        print("=================================================")

    # Giai ma
    elif choice == '2':

        print("Nhap Ciphertext")
        lines = input()
        ciphertext = ''.join(lines)
        if not ciphertext.strip():
            print("Khong co du lieu!")
            return

        # Giai ma
        plaintext = playfair_cipher(
            ciphertext,
            matrix,
            encrypt=False
        )

        print("\n==================== KET QUA ====================")
        print("Plaintext:")
        print(plaintext)
        print("=================================================")

    else:
        print("Lua chon khong hop le!")

if __name__ == "__main__":
    main()
