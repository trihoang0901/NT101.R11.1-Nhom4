
from Crypto.Cipher import DES


def bytes_to_binary(data):
    # Chuyen bytes thanh so nguyen
    number = int.from_bytes(data, 'big')
    # Chuyen so nguyen thành chuoi nhi phan
    binary = bin(number)[2:]
    # 64 bit
    binary = binary.zfill(len(data) * 8)

    return binary


def hamming_distance(binary1, binary2):
    distance = 0
    for bit1, bit2 in zip(binary1, binary2):
        if bit1 != bit2:
            distance += 1
    return distance


def avalanche_test(mssv):
    key = mssv.encode()
    p1 = b"STAYHOME"
    p2 = b"STAYHOMA"
    # Tao DES-ECB
    cipher = DES.new(key, DES.MODE_ECB)
    # Ma hoa
    c1 = cipher.encrypt(p1)
    c2 = cipher.encrypt(p2)

    # Chuyen ciphertext sang binary
    binary1 = bytes_to_binary(c1)
    binary2 = bytes_to_binary(c2)

    # Tinh Hamming Distance
    distance = hamming_distance(binary1, binary2)

    # Tinh phan tram bit thay doi
    percentage = (distance / 64) * 100
    print ("---------------------------------")
    print("MSSV:", mssv)

    print("\nPlaintext:")
    print("P1:", p1.decode())
    print("P2:", p2.decode())

    print("\nCiphertext:")
    print("C1 (Hex):", c1.hex())
    print("C2 (Hex):", c2.hex())

    print("\nCiphertext Binary:")
    print("C1:", binary1)
    print("C2:", binary2)

    print("\nAvalanche Effect:")
    print("Hamming Distance:", distance, "bit")
    print("Ty le thay doi: {:.2f}%".format(percentage))

    print()


print("DES Avalanche Effect - Task 2.3")

mssv_list = []

for i in range(3):

    mssv = input(f"Nhap MSSV thanh vien {i + 1}: ").strip()

    if len(mssv) != 8:
        print("MSSV phai co dung 8 ky tu.")
        continue

    mssv_list.append(mssv)


for mssv in mssv_list:
    avalanche_test(mssv)

