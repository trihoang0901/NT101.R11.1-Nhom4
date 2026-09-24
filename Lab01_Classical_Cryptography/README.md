# Lab 01 - Classical Cryptography

Ba task: mono-alphabetic substitution (2.2), Vigenère (2.5), Rail Fence (2.7).
Chỉ dùng Python 3 standard library.

Chạy lệnh từ thư mục `Lab01`.

## Task 2.2 - Mono-alphabetic substitution

Mục tiêu: khôi phục plaintext tiếng Anh bằng frequency analysis, không đoán cả bài rồi in ra.

Frequency analysis đếm tần suất chữ, bigram, trigram và từ. Chữ nhiều nhất không tự động là E. Mỗi bước chỉ thêm mapping khi pattern khớp trên cả ciphertext. Một chữ cipher chỉ map tới một chữ plain, và ngược lại.

Chương trình:

- đọc `task2_2/cipher.txt`
- thống kê A-Z, không phân biệt hoa thường
- giữ dấu câu, số, khoảng trắng và chữ hoa khi giải
- thêm, xóa, kiểm tra trùng mapping
- ghi lại từng bước suy luận

```text
python task2_2/frequency_analysis.py run
python task2_2/frequency_analysis.py
```

`run` ghi toàn bộ output. Không đối số thì mở menu để sửa mapping.

Output:

- `task2_2/output/letter_frequency.txt`
- `task2_2/output/bigram_frequency.txt`
- `task2_2/output/trigram_frequency.txt`
- `task2_2/output/word_frequency.txt`
- `task2_2/output/decoding_steps.txt`
- `task2_2/output/plaintext.txt`
- `task2_2/mappings.json`

Tóm tắt phá mã: `v` cao nhất (489/4576, 10.69%) nên thử `v -> e`. Từ `ghv` (39 lần) thành `the`. `ghlg` thành `that`, `lmw` thành `and`, `zd` thành `of`. Các từ ngắn `in`, `is`, `as`, `to`, `a` khóa thêm mapping. Phần còn lại hiện rõ `Harry Potter`, `written`, `British`, `J.K. Rowling`. Hai chữ cuối: `j -> x` vì `mvjg = next`, `a -> q` vì `fmrafv = unique`.

Ba token trong ciphertext lệch với mapping này: `vakozivw` ra `eqplored`, `xznkova` ra `compleq`, `xzmjfvirmt` ra `conxuering`. Các chỗ khác thành tiếng Anh. Mã hóa ngược bằng mapping nghịch đảo trùng ciphertext gốc. Kết quả verify: PASS.

## Task 2.5 - Vigenère

Vigenère là substitution đa bảng. Khóa lặp lại theo từng chữ cái.

```text
C_i = (P_i + K_i) mod 26
P_i = (C_i - K_i + 26) mod 26
```

A = 0, ..., Z = 25. Chỉ chữ cái A-Z tham gia phép cộng. Khóa chỉ tăng khi gặp chữ cái. Hoa thường, dấu cách, dấu câu và chữ số được giữ. Khóa rỗng hoặc có ký tự không phải chữ cái thì báo lỗi.

```text
python task2_5/vigenere.py demo
python task2_5/vigenere.py
```

Menu: 1 Encrypt, 2 Decrypt, 3 Run demonstration/tests, 0 Exit.

Test:

- `ATTACKATDAWN` + `LEMON` = `LXFOPVEFRNHR`, giải ngược ra lại plaintext. PASS.
- Đoạn mẫu 144 từ, khóa `SECURITY`, encrypt rồi decrypt trùng plaintext. PASS.
- Đối chiếu tay: ciphertext trong `task2_5/output/demonstration.txt` với https://www.dcode.fr/vigenere-cipher

## Task 2.7 - Rail Fence

Chọn Rail Fence vì đây là transposition cipher: giữ nguyên ký tự, chỉ đổi vị trí. Khác Caesar, substitution và Vigenère.

Plaintext viết zig-zag theo số rail. Gặp rail đầu hoặc rail cuối thì đổi chiều. Ciphertext là nối từng rail từ trên xuống dưới.

Giải mã: tính lại chỉ số rail của từng vị trí, đếm số ký tự mỗi rail, cắt ciphertext theo các đoạn đó, rồi lấy ký tự đúng thứ tự zig-zag. Không brute force.

`rails < 2` ném `ValueError`. Text rỗng trả text rỗng. `rails >= len(text)` thì ciphertext giống plaintext. Dấu cách, dấu câu và chữ số được giữ.

```text
python task2_7/rail_fence.py demo
python task2_7/rail_fence.py
```

Test:

- `DCODEZIGZAG`, 3 rail, ciphertext `DEZCDZGAOIG`, giải ngược đúng plaintext. PASS.
- Round-trip rails 2, 3, 4 và câu có dấu câu, số. PASS.
- Đối chiếu tay: ciphertext trong `task2_7/output/demonstration.txt` với https://www.dcode.fr/rail-fence-cipher

## Test tự động

```text
python -m unittest discover -s tests -v
```
