from Crypto.Cipher import AES

key = b"1234567890123456"
iv = b"0987654321098765"
plaintext = b"UIT_LAB_UIT_LAB_UIT_LAB_UIT_LAB_"  # 32 bytes (2 blocks)


def show(name, ciphertext):
    block_1, block_2 = ciphertext[:16], ciphertext[16:]
    print(f"--- AES-{name} ---")
    print(f"{name}: {ciphertext.hex()}")
    print(f"Khối 1: {block_1.hex()}")
    print(f"Khối 2: {block_2.hex()}")
    print(f"Hai khối giống nhau: {block_1 == block_2}\n")


show("ECB", AES.new(key, AES.MODE_ECB).encrypt(plaintext))
show("CBC", AES.new(key, AES.MODE_CBC, iv=iv).encrypt(plaintext))
show("CFB", AES.new(key, AES.MODE_CFB, iv=iv, segment_size=128).encrypt(plaintext))
show("OFB", AES.new(key, AES.MODE_OFB, iv=iv).encrypt(plaintext))
show("CTR", AES.new(key, AES.MODE_CTR, nonce=iv[:8]).encrypt(plaintext))  # nonce = 8 byte đầu của IV
