from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


key = b"0123456789abcdef"
iv = b"abcdef9876543210"

BLOCK_SIZE = 16


plaintext = bytes([i % 256 for i in range(1000)])


print("TASK 2.4 - ERROR PROPAGATION")


print("\n[1] TAO DU LIEU 1000 BYTE")
print("Kich thuoc:", len(plaintext), "bytes")

byte_position = 26
block_number = (byte_position - 1) // BLOCK_SIZE + 1

print("Byte bi lam hong:", byte_position)
print("Byte 26 nam trong Block:", block_number)



def corrupt_ciphertext(ciphertext):

    corrupted = bytearray(ciphertext)

    old_value = corrupted[25]

    # Đảo đúng 1 bit
    corrupted[25] ^= 0x01

    new_value = corrupted[25]

    return bytes(corrupted), old_value, new_value


def find_corrupted_blocks(original, decrypted):

    corrupted_blocks = []

    for start in range(0, len(original), BLOCK_SIZE):

        end = start + BLOCK_SIZE

        original_block = original[start:end]
        decrypted_block = decrypted[start:end]

        if original_block != decrypted_block:

            block = start // BLOCK_SIZE + 1

            corrupted_blocks.append(block)

    return corrupted_blocks



def count_different_bits(data1, data2):

    return sum(
        (a ^ b).bit_count()
        for a, b in zip(data1, data2)
    )




def test_ecb():

    print("----------------------------------")
    print("MODE: ECB")




    print("\n[2] MA HOA AES-128")

    padded = pad(plaintext, BLOCK_SIZE)

    cipher = AES.new(
        key,
        AES.MODE_ECB
    )

    ciphertext = cipher.encrypt(padded)

    print("Ciphertext:", len(ciphertext), "bytes")


    print("\n[3] LAM HONG CIPHERTEXT")

    corrupted, old_value, new_value = \
        corrupt_ciphertext(ciphertext)

    print("Dao 1 bit tai byte thu 26")

    print(
        f"Byte 26: "
        f"{old_value:08b} -> {new_value:08b}"
    )



    print("\n[4] GIAI MA")

    cipher_dec = AES.new(
        key,
        AES.MODE_ECB
    )

    decrypted = cipher_dec.decrypt(corrupted)

    decrypted = unpad(
        decrypted,
        BLOCK_SIZE
    )


    blocks = find_corrupted_blocks(
        plaintext,
        decrypted
    )

    print("Block bi hong:", blocks)
    print("So block bi hong:", len(blocks))




def test_cbc():

    print("----------------------------------")
    print("MODE: CBC")


    print("\n[2] MA HOA AES-128")

    padded = pad(plaintext, BLOCK_SIZE)

    cipher = AES.new(
        key,
        AES.MODE_CBC,
        iv=iv
    )

    ciphertext = cipher.encrypt(padded)

    print("Ciphertext:", len(ciphertext), "bytes")


    print("\n[3] LAM HONG CIPHERTEXT")

    corrupted, old_value, new_value = \
        corrupt_ciphertext(ciphertext)

    print("Dao 1 bit tai byte thu 26")

    print(
        f"Byte 26: "
        f"{old_value:08b} -> {new_value:08b}"
    )

    print("\n[4] GIAI MA")

    cipher_dec = AES.new(
        key,
        AES.MODE_CBC,
        iv=iv
    )

    decrypted = cipher_dec.decrypt(corrupted)

    decrypted = unpad(
        decrypted,
        BLOCK_SIZE
    )


    blocks = find_corrupted_blocks(
        plaintext,
        decrypted
    )

    print("Block bi hong:", blocks)
    print("So block bi hong:", len(blocks))


def test_cfb():

    print("----------------------------------")
    print("MODE: CFB")


    print("\n[2] MA HOA AES-128")

    cipher = AES.new(
        key,
        AES.MODE_CFB,
        iv=iv,
        segment_size=128
    )

    ciphertext = cipher.encrypt(plaintext)

    print("Ciphertext:", len(ciphertext), "bytes")



    print("\n[3] LAM HONG CIPHERTEXT")

    corrupted, old_value, new_value = \
        corrupt_ciphertext(ciphertext)

    print("Dao 1 bit tai byte thu 26")

    print(
        f"Byte 26: "
        f"{old_value:08b} -> {new_value:08b}"
    )



    print("\n[4] GIAI MA")

    cipher_dec = AES.new(
        key,
        AES.MODE_CFB,
        iv=iv,
        segment_size=128
    )

    decrypted = cipher_dec.decrypt(corrupted)


    blocks = find_corrupted_blocks(
        plaintext,
        decrypted
    )

    print("Block bi hong:", blocks)
    print("So block bi hong:", len(blocks))



def test_ofb():

    print("----------------------------------")
    print("MODE: OFB")


    print("\n[2] MA HOA AES-128")

    cipher = AES.new(
        key,
        AES.MODE_OFB,
        iv=iv
    )

    ciphertext = cipher.encrypt(plaintext)

    print("Ciphertext:", len(ciphertext), "bytes")

    print("\n[3] LAM HONG CIPHERTEXT")

    corrupted, old_value, new_value = \
        corrupt_ciphertext(ciphertext)

    print("Dao 1 bit tai byte thu 26")

    print(
        f"Byte 26: "
        f"{old_value:08b} -> {new_value:08b}"
    )


    print("\n[4] GIAI MA")

    cipher_dec = AES.new(
        key,
        AES.MODE_OFB,
        iv=iv
    )

    decrypted = cipher_dec.decrypt(corrupted)


    blocks = find_corrupted_blocks(
        plaintext,
        decrypted
    )

    print("Block bi hong:", blocks)
    print("So block bi hong:", len(blocks))





test_ecb()
test_cbc()
test_cfb()
test_ofb()

