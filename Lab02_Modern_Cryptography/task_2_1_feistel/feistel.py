def F(right, subkey):
    return (right ^ subkey) & 0x0F


def feistel_round(L_in, R_in, subkey):
    L_out = R_in
    R_out = L_in ^ F(R_in, subkey)
    return L_out, R_out


def track_avalanche(msg, key):
    L, R = (msg >> 4) & 0x0F, msg & 0x0F
    subkeys = [key & 0x0F, (key >> 4) & 0x0F, (key + 1) & 0x0F, (key + 2) & 0x0F]

    states = [(L, R)]
    print(f"Khởi tạo: L={L:04b}, R={R:04b}")
    for i in range(4):
        L, R = feistel_round(L, R, subkeys[i])
        states.append((L, R))
        print(f"Vòng {i + 1}: L={L:04b}, R={R:04b}")

    print(f"Bản mã: 0x{(L << 4) | R:02X}")
    return states


def compare(states_1, states_2):
    for i, ((l1, r1), (l2, r2)) in enumerate(zip(states_1, states_2)):
        diff_l, diff_r = l1 ^ l2, r1 ^ r2
        bits = bin(diff_l).count("1") + bin(diff_r).count("1")
        name = "Khởi tạo" if i == 0 else f"Vòng {i}"
        print(f"{name}: L khác={diff_l:04b}, R khác={diff_r:04b}, tổng {bits} bit khác")


print("--- Mã hóa M1 = 0xAB ---")
states_1 = track_avalanche(0xAB, 0x12)
print("--- Mã hóa M2 = 0xAC ---")
states_2 = track_avalanche(0xAC, 0x12)
print("--- So sánh M1 và M2 ---")
compare(states_1, states_2)
