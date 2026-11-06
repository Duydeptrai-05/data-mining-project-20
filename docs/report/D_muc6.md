# 6. Khai phá — họ bài toán phụ

*Tiêu chí 6 · 0,50 điểm · CLO4*

**Họ bài toán và cách áp dụng.** Họ bài toán chính của đề tài là Mô tả – OLAP: cho biết *ở đâu* tỉ lệ app bị đánh giá thấp cao (theo danh mục, giá, lượt cài). OLAP không cho biết *người dùng phàn nàn về điều gì*. Họ bài toán phụ là khai phá văn bản: gán chủ đề phàn nàn cho 6 057 review tiêu cực (sentiment = Negative) trong 28 250 review sau khi làm sạch.

**Phương pháp.** Chúng tôi dùng TF-IDF (bỏ stopword tiếng Anh, giữ token từ 3 chữ cái, min_df = 5, max_df = 0,5; 2 471 từ) để tìm từ khoá nổi bật, rồi xây từ điển chủ đề gồm 8 chủ đề (quảng cáo, lỗi và hiệu năng, cập nhật, tiền và thanh toán, nội dung và độ khó, tài khoản, thiết bị, đề xuất tính năng) cộng nhóm "khác". Review được gán chủ đề có nhiều từ khoá khớp nhất (sau khi rút gọn gốc từ bằng Porter stemmer); hoà thì lấy chủ đề cụ thể đứng trước; không khớp thì vào "khác". Các từ cảm xúc chung (hate, worst, useless...) cố ý không đưa vào từ điển vì không cho biết nguyên nhân. Vòng 1 cho chủ đề "lỗi và hiệu năng" chiếm 29,8% vì chứa các từ quá chung (work, fix, open, problem); vòng 2 bỏ các từ đó, thêm luật phủ định ("not/can't ... work/open/load") và thêm chủ đề đề xuất tính năng (xuống 10,6%). Từ điển được đóng băng trước khi rút mẫu đánh giá.

**Kết quả.** Phân bố chủ đề (6 057 review): khác 1 909 (31,5%), tiền và thanh toán 739 (12,2%), lỗi và hiệu năng 643 (10,6%), thiết bị 633 (10,5%), cập nhật 541 (8,9%), quảng cáo 498 (8,2%), nội dung và độ khó 420 (6,9%), tài khoản 360 (5,9%), đề xuất tính năng 314 (5,2%).

**Đánh giá bằng nhãn tay.** Mẫu 120 review phân tầng (12 mỗi chủ đề, 24 "khác", seed 42). A gán mẫu 1–80, D gán mẫu 41–120, hai người chung 40 mẫu.
- Đồng thuận trên 40 mẫu chung: 26/40 = 65% (Wilson 95%: 0,50–0,78), kappa = 0,58. 10 trong 14 dòng bất đồng liên quan đến ranh giới giữa "khác" và chủ đề cụ thể.
- Precision gộp 8 chủ đề: 0,36 (23/64; 0,25–0,48) theo nhãn D và 0,52 (35/67; 0,40–0,64) theo nhãn A. Theo chủ đề (D / A): cập nhật 0,67 / 0,60; lỗi và hiệu năng 0,56 / 0,75; tiền và thanh toán 0,38 / 0,88; thiết bị 0,22 / 0,17. Mỗi chủ đề chỉ có 6–10 mẫu nên khoảng Wilson rộng.

**Bảng. So sánh với baseline** (độ khớp 9 nhóm, có trọng số theo kích thước tầng, bootstrap 2 000 lần):

| | Từ điển | Luôn "khác" | Luôn "tiền và thanh toán" |
|---|---|---|---|
| Nhãn D | 0,52 (0,41–0,62) | 0,49 (0,39–0,59) | 0,07 (0,02–0,11) |
| Nhãn A | 0,62 (0,51–0,71) | 0,34 (0,25–0,44) | 0,13 (0,09–0,16) |

Từ điển hơn baseline chủ đề cụ thể rõ rệt ở cả hai người gán. So với baseline "luôn khác" thì hơn rõ theo nhãn A, nhưng chưa phân biệt được theo nhãn D, vì hai người chưa thống nhất quy ước cho nhóm "khác".

**Điều nó cho thấy mà phân tích chính không thấy.** Tiền và thanh toán là chủ đề cụ thể đứng đầu ở 7 trong 27 danh mục đủ mẫu, gồm GAME và FAMILY; 7 danh mục này chiếm 2 970 trên 5 945 review tiêu cực (50%) (Hình 6, chart 4). Đây là giả thuyết về lý do phàn nàn, không phải quan hệ nhân quả. Chủ đề thiết bị đứng đầu ở 12 danh mục nhưng precision chỉ 0,17–0,22 nên không dùng để kết luận.

**Giới hạn.** Cỡ mẫu nhãn tay nhỏ (khoảng 80 mẫu mỗi người); đồng thuận giữa hai người chỉ 65%; 31,5% review không có chủ đề cụ thể; từ điển xây trên chính tập review này nên chưa kiểm tra trên dữ liệu mới.