# Lab 02: Mật mã học hiện đại

Thư mục này chứa phần thực hành Nhiệm vụ 2.1 và 2.2 của Lab 02.

## Cấu trúc

| Thư mục | Nội dung |
|---|---|
| `task_2_1_feistel/feistel.py` | Cài đặt vòng Feistel và theo dõi sự lan truyền thay đổi giữa hai bản rõ `0xAB`, `0xAC` |
| `task_2_2_mode_of_operation/modes.py` | Mã hóa chuỗi lặp bằng AES ở các chế độ ECB, CBC, CFB, OFB, CTR |

## Chạy chương trình

```bash
pip install pycryptodome
python task_2_1_feistel/feistel.py
python task_2_2_mode_of_operation/modes.py
```

## Nhiệm vụ 2.1: Cấu trúc Feistel và sự lan truyền thay đổi

Mỗi vòng thực hiện `LE_i = RE_{i-1}` và `RE_i = LE_{i-1} XOR F(RE_{i-1}, K_i)`, với `F(R, K) = (R XOR K) & 0x0F`. Khóa `0x12`, bốn vòng, các khóa con là `[0x2, 0x1, 0x3, 0x4]`.

| Vòng | M1 (L,R) | M2 (L,R) | L1^L2 | R1^R2 | Số bit khác (/8) |
|---|---|---|---|---|---|
| Khởi tạo | 1010,1011 | 1010,1100 | 0000 | 0111 | 3 |
| 1 | 1011,0011 | 1100,0100 | 0111 | 0111 | 6 |
| 2 | 0011,1001 | 0100,1001 | 0111 | 0000 | 3 |
| 3 | 1001,1001 | 1001,1110 | 0000 | 0111 | 3 |
| 4 | 1001,0100 | 1110,0011 | 0111 | 0111 | 6 |

Bản mã: `M1 -> 0x94`, `M2 -> 0xE3`.

Nhận xét:

- `0xAB = 10101011` và `0xAC = 10101100` khác nhau 3 bit (`0111`), không phải 1 bit như đề bài mô tả.
- Sự khác biệt lan từ nửa phải sang cả hai nửa ngay ở vòng 1 (3 bit lên 6 bit), nhưng không tăng dần qua các vòng. Số bit khác dao động 3, 6, 3, 3, 6.
- Nguyên nhân: `F` chỉ là phép XOR với khóa con nên `F(a) XOR F(b) = a XOR b`. Khóa con triệt tiêu khỏi phần chênh lệch, và chênh lệch chỉ tuân theo `ΔL_i = ΔR_{i-1}`, `ΔR_i = ΔL_{i-1} XOR ΔR_{i-1}`. Mẫu `(0000,0111) -> (0111,0111) -> (0111,0000)` lặp lại với chu kỳ 3 vòng và không phụ thuộc vào khóa.
- Cấu trúc Feistel chỉ hoán đổi và trộn hai nửa (khuếch tán). Hiệu ứng thác đổ cần thêm hàm `F` phi tuyến như S-box trong DES thật.

## Nhiệm vụ 2.2: Mode of operation

Khóa `1234567890123456`, IV cố định `0987654321098765`, bản rõ `UIT_LAB_UIT_LAB_UIT_LAB_UIT_LAB_` (32 byte, hai khối 16 byte giống hệt nhau). Kết quả đã được đối chiếu với `openssl enc -aes-128-*`.

| Chế độ | Khối 1 | Khối 2 | Khối 1 = Khối 2 |
|---|---|---|---|
| ECB | `02b0647de210da452e3bdcadc415814e` | `02b0647de210da452e3bdcadc415814e` | Có |
| CBC | `29036f382c4b503aac7b61a452bb7374` | `167e228c65afb8a41361efa102315246` | Không |
| CFB | `5fe76e74d5ef9afb56d333889b064d0f` | `4550b3342ce7a976807ae4d4661ec37e` | Không |
| OFB | `5fe76e74d5ef9afb56d333889b064d0f` | `5a808d518ccfae67c5f0f7dd11e084f0` | Không |
| CTR | `d1aea66dd13a154fc5e577c7008802c9` | `8b167aae801a275463a66c0634a1bb8b` | Không |

Nhận xét:

- ECB mã hóa từng khối độc lập bằng cùng một khóa, nên hai khối rõ giống nhau cho hai khối mã giống nhau và lộ cấu trúc lặp của dữ liệu.
- CBC XOR mỗi khối rõ với khối mã trước đó (khối đầu dùng IV) trước khi mã hóa, nên hai khối rõ giống nhau vẫn cho hai khối mã khác nhau.
- CFB, OFB, CTR biến AES thành mã luồng: bản rõ được XOR với dòng khóa. Dòng khóa thay đổi theo từng khối (phản hồi bản mã ở CFB, phản hồi đầu ra ở OFB, bộ đếm ở CTR) nên các khối mã cũng khác nhau.
- CFB và OFB có khối mã đầu giống nhau vì cả hai đều tính dòng khóa đầu tiên là `E(IV)`. Chúng tách ra từ khối thứ hai vì cách phản hồi khác nhau.
- ECB và CBC cần độn (padding) khi độ dài không chia hết cho 16 byte. Ở đây 32 byte nên không cần độn. CFB, OFB, CTR không cần độn.
- IV cố định chỉ dùng cho bài lab. Dùng lại cùng một cặp (khóa, IV) cho nhiều thông điệp sẽ làm lộ quan hệ giữa các bản rõ, nghiêm trọng nhất ở OFB và CTR vì dòng khóa bị lặp lại.
- Chương trình dùng CFB với `segment_size=128` (CFB-128) và CTR với nonce là 8 byte đầu của IV (8 byte còn lại là bộ đếm khối bắt đầu từ 0).
