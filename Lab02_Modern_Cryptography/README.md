# Lab 02: Mật mã học hiện đại

Thư mục này chứa phần thực hành Nhiệm vụ 2.1, 2.2 và 2.6 của Lab 02.

## Cấu trúc

| Thư mục | Nội dung |
|---|---|
| `task_2_1_feistel/feistel.py` | Cài đặt vòng Feistel và theo dõi sự lan truyền thay đổi giữa hai bản rõ `0xAB`, `0xAC` |
| `task_2_2_mode_of_operation/modes.py` | Mã hóa chuỗi lặp bằng AES ở các chế độ ECB, CBC, CFB, OFB, CTR |
| `task2_6/number_theory.py` | Số nguyên tố (Miller-Rabin, Lucas-Lehmer), ước chung lớn nhất (Euclid) và lũy thừa modulo (bình phương liên tiếp) |
| `tests/test_task2_6.py` | Test tự động cho nhiệm vụ 2.6 |

## Chạy chương trình

```bash
pip install pycryptodome
python task_2_1_feistel/feistel.py
python task_2_2_mode_of_operation/modes.py
python task2_6/number_theory.py
python -m unittest discover -s tests -v
```

Nhiệm vụ 2.6 chỉ dùng thư viện chuẩn của Python. `sympy` (`pip install sympy`) là tùy chọn, chỉ dùng trong test 2.6 để đối chiếu độc lập.

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

## Nhiệm vụ 2.6: Số nguyên tố, GCD và lũy thừa modulo

Chạy toàn bộ các yêu cầu bằng `python task2_6/number_theory.py`, hoặc từng phần:

```bash
python task2_6/number_theory.py random-prime 64
python task2_6/number_theory.py top-primes
python task2_6/number_theory.py is-prime 618970019642690137449562111
python task2_6/number_theory.py gcd 1071 462
python task2_6/number_theory.py modpow 7 40 19
```

Số được nhập ở dạng thập phân hoặc hex (`0x...`).

**1. Số nguyên tố**

- Số nguyên tố ngẫu nhiên 8, 16, 64 bit: sinh số ngẫu nhiên bằng `secrets` với bit cao nhất và bit thấp nhất bằng 1, lặp đến khi qua Miller-Rabin. Độ dài bit luôn đúng bằng yêu cầu.
- Số nguyên tố Mersenne thứ 10: chương trình tự tìm bằng kiểm tra Lucas-Lehmer cho các số mũ nguyên tố tăng dần. Kết quả là các số mũ 2, 3, 5, 7, 13, 17, 19, 31, 61, 89, nên số thứ 10 là `2^89 - 1 = 618970019642690137449562111`.
- 10 số nguyên tố lớn nhất nhỏ hơn `2^89 - 1` (đi xuống từ `2^89 - 2` và kiểm tra từng số):

| Thứ tự | Số nguyên tố | Cách `2^89 - 1` |
|---|---|---|
| 1 | `618970019642690137449562091` | 20 |
| 2 | `618970019642690137449562081` | 30 |
| 3 | `618970019642690137449562063` | 48 |
| 4 | `618970019642690137449562043` | 68 |
| 5 | `618970019642690137449562013` | 98 |
| 6 | `618970019642690137449562009` | 102 |
| 7 | `618970019642690137449561847` | 264 |
| 8 | `618970019642690137449561791` | 320 |
| 9 | `618970019642690137449561671` | 440 |
| 10 | `618970019642690137449561509` | 602 |

- Kiểm tra một số tùy ý: Miller-Rabin với 13 cơ sở nguyên tố đầu tiên. Cách này chính xác tuyệt đối cho n nhỏ hơn `3317044064679887385961981` (khoảng 3.3 x 10^24). Với n lớn hơn, kể cả gần `2^89` (khoảng 6.2 x 10^26), chương trình thêm 20 cơ sở ngẫu nhiên nên kết quả là xác suất, sai số không đáng kể. Dòng kết quả ghi rõ phương pháp là "xác định" hay "xác suất".

**2. GCD**

Thuật toán Euclid lặp, không giới hạn kích thước vì số nguyên Python có độ chính xác tùy ý. Phần demo tạo hai số khoảng 1791 bit có ước chung khoảng 768 bit đã biết trước, rồi kiểm tra kết quả khớp với ước đó và với `math.gcd`.

**3. Lũy thừa modulo**

Bình phương liên tiếp (square-and-multiply), áp dụng tính chất `(a x b) mod n = ((a mod n) x (b mod n)) mod n` nên các số trung gian luôn nhỏ hơn `p`. `7^40 mod 19 = 7`. Số mũ rất lớn cũng chạy được, ví dụ `3^(10^100) mod (2^89 - 1)`.

Nhận xét:

- Số mũ 67 là số nguyên tố nhưng `2^67 - 1` là hợp số (`193707721 x 761838257287`), nên Lucas-Lehmer loại 67 và danh sách số mũ nhảy từ 61 sang 89.
- Khoảng cách trung bình giữa các số nguyên tố gần `2^89` là `ln(2^89)`, khoảng 61.7. Mười số tìm được nằm trong khoảng 600 số dưới `2^89 - 1`, phù hợp với con số đó.
- Test tự động đối chiếu với bảng sàng Eratosthenes (dưới 10000), các số Carmichael và strong pseudoprime, `math.gcd`, `pow` có sẵn của Python, và `sympy` cho các số quanh `2^89` (bỏ qua nếu không cài `sympy`).
