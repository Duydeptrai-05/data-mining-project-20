# 6. Khai phá — họ bài toán phụ

*Tiêu chí 6 · 0,50 điểm · CLO4*

**Họ bài toán và cách áp dụng.** Họ bài toán chính của đề tài là Mô tả – OLAP: cho biết *ở đâu* tỉ lệ app bị đánh giá thấp cao (theo danh mục, giá, độ cũ, lượt cài). OLAP không cho biết *người dùng phàn nàn về điều gì*. Họ bài toán phụ là khai phá văn bản: gán chủ đề phàn nàn cho 6 057 review tiêu cực (nhãn Sentiment = Negative) trong tổng 28 250 review sau khi làm sạch, nhằm trả lời phần còn thiếu của câu hỏi nghiệp vụ ở Chương 1: lý do đằng sau các con số điểm thấp.

**Phương pháp.** Nhóm dùng TF-IDF (Salton và Buckley, 1988) cài đặt bằng scikit-learn (Pedregosa và cs., 2011), bỏ stopword tiếng Anh của NLTK (Bird và cs., 2009), giữ token từ 3 chữ cái, min_df = 5, max_df = 0,5; kết quả là 2 471 từ. Điểm TF-IDF trung bình giúp nhóm chọn từ khoá để lập từ điển gồm 8 chủ đề: quảng cáo, lỗi và hiệu năng, cập nhật, tiền và thanh toán, nội dung và độ khó, tài khoản, thiết bị, đề xuất tính năng; cộng nhóm "khác" cho review không khớp chủ đề nào. Mỗi review được rút gọn gốc từ bằng Porter stemmer rồi gán chủ đề có nhiều từ khoá khớp nhất; hoà thì lấy chủ đề cụ thể đứng trước trong từ điển; không khớp thì vào "khác". Các từ chỉ cảm xúc chung (hate, worst, useless...) cố ý không đưa vào từ điển vì không cho biết nguyên nhân phàn nàn.

Từ điển được chỉnh hai vòng. Vòng 1 làm chủ đề "lỗi và hiệu năng" chiếm 29,8% vì chứa các từ quá chung (work, fix, open, problem). Vòng 2 bỏ các từ đó, thêm luật phủ định ("not/can't ... work/open/load") và thêm chủ đề đề xuất tính năng; tỉ lệ của chủ đề lỗi giảm xuống 10,6%. Từ điển được đóng băng trước khi rút mẫu đánh giá, để precision không bị thổi phồng do chỉnh từ điển theo chính mẫu đo.

**Kết quả.** Phân bố chủ đề của 6 057 review tiêu cực: khác 1 909 (31,5%); tiền và thanh toán 739 (12,2%); lỗi và hiệu năng 643 (10,6%); thiết bị 633 (10,5%); cập nhật 541 (8,9%); quảng cáo 498 (8,2%); nội dung và độ khó 420 (6,9%); tài khoản 360 (5,9%); đề xuất tính năng 314 (5,2%). Nhóm "khác" lớn nhất vì nhiều review tiêu cực chỉ bày tỏ sự bực bội chung.

**Đánh giá bằng nhãn tay.** Nhóm rút mẫu 120 review phân tầng (12 review cho mỗi chủ đề, 24 review nhóm "khác", random_state = 42). Hai thành viên gán nhãn độc lập: A gán mẫu 1–80, D gán mẫu 41–120, nên hai người cùng gán 40 mẫu (41–80).

- **Đồng thuận giữa hai người.** Trên 40 mẫu chung, hai người khớp 26/40 = 65% (Wilson 95%: 0,50–0,78), hệ số kappa của Cohen (1960) = 0,58 (khoảng bootstrap 95%: 0,40–0,75), mức trung bình theo thang của Landis và Koch (1977). Trong 14 dòng bất đồng, 10 dòng liên quan đến ranh giới giữa "khác" và một chủ đề cụ thể, nên nhóm "khác" là chỗ hai người chưa có quy ước chung. Nếu chỉ xét câu hỏi "có chủ đề cụ thể hay là khác", hai người khớp 30/40 = 75%.
- **Chốt nhãn cho các ca bất đồng.** Sau khi đo, A và D họp ngày 09/11/2026 và thống nhất nhãn chốt cho 14 ca bất đồng (5 ca theo nhãn của A, 9 ca theo nhãn của D); lý do từng ca ghi trong `outputs/labeling/labels_final_disagreements.csv` và dòng 20 của nhật ký quyết định. Hai file nhãn gốc được giữ nguyên; các số đồng thuận và precision trong chương này tính **trước khi bàn** để không thổi phồng, và nhóm không đo lại trên 120 mẫu này sau khi chốt. Từ điển được khoá ở phiên bản 1; muốn có phiên bản 2 phải rút mẫu mới với seed khác.
- **Precision của từ điển.** Precision là tỉ lệ review mà từ điển gán chủ đề X và người gán nhãn cũng chọn X; khoảng tin cậy dùng phương pháp Wilson (1927). Mỗi chủ đề chỉ có 6–10 mẫu nên khoảng Wilson rất rộng; không nên xếp hạng các chủ đề theo precision.

**Precision của từ điển theo chủ đề** (đúng/n = precision, khoảng Wilson 95%):

| Chủ đề do từ điển gán | Theo nhãn của D | Theo nhãn của A |
|---|---|---|
| Cập nhật | 4/6 = 0,67 (0,30–0,90) | 6/10 = 0,60 (0,31–0,83) |
| Lỗi và hiệu năng | 5/9 = 0,56 (0,27–0,81) | 6/8 = 0,75 (0,41–0,93) |
| Tiền và thanh toán | 3/8 = 0,38 (0,14–0,69) | 7/8 = 0,88 (0,53–0,98) |
| Quảng cáo | 2/7 = 0,29 (0,08–0,64) | 6/10 = 0,60 (0,31–0,83) |
| Nội dung và độ khó | 3/8 = 0,38 (0,14–0,69) | 3/8 = 0,38 (0,14–0,69) |
| Tài khoản | 3/8 = 0,38 (0,14–0,69) | 3/10 = 0,30 (0,11–0,60) |
| Đề xuất tính năng | 1/9 = 0,11 (0,02–0,44) | 3/7 = 0,43 (0,16–0,75) |
| Thiết bị | 2/9 = 0,22 (0,06–0,55) | 1/6 = 0,17 (0,03–0,56) |
| **Gộp 8 chủ đề** | **23/64 = 0,36 (0,25–0,48)** | **35/67 = 0,52 (0,41–0,64)** |
| Khác (không có chủ đề cụ thể) | 13/16 = 0,81 (0,57–0,93) | 10/13 = 0,77 (0,50–0,92) |

- **So sánh với baseline.** Vì mẫu lấy phân tầng nên độ khớp chung không thể cộng đều mà phải cân theo kích thước từng tầng trong 6 057 review; khoảng tin cậy lấy bằng bootstrap 2 000 lần trong từng tầng. Hai baseline là luôn gán "khác" (nhóm phổ biến nhất) và luôn gán "tiền và thanh toán" (chủ đề cụ thể phổ biến nhất).

**Độ khớp có trọng số của từ điển và hai baseline** (khoảng tin cậy 95% bootstrap):

| Nhãn của | Từ điển | Luôn "khác" | Luôn "tiền và thanh toán" |
|---|---|---|---|
| D | 0,52 (0,41–0,62) | 0,49 (0,39–0,59) | 0,07 (0,02–0,11) |
| A | 0,62 (0,51–0,71) | 0,34 (0,25–0,44) | 0,13 (0,09–0,16) |

Từ điển hơn baseline chủ đề cụ thể rõ rệt ở cả hai người gán. So với baseline "luôn khác" thì từ điển hơn rõ theo nhãn của A (0,62 so với 0,34) nhưng chưa phân biệt được theo nhãn của D (0,52 so với 0,49), vì hai người chưa thống nhất quy ước cho nhóm "khác".

**Điều nó cho thấy mà phân tích chính không thấy.** Tiền và thanh toán là chủ đề cụ thể đứng đầu ở 7 trong 27 danh mục đủ mẫu, gồm GAME và FAMILY; bảy danh mục này chiếm 2 970 trên 5 945 review tiêu cực (50%) (biểu đồ 5 của dashboard, Hình 6). Đây là giả thuyết về lý do phàn nàn đi kèm với điểm thấp, không phải quan hệ nhân quả. Chủ đề thiết bị đứng đầu ở 12 danh mục nhưng precision chỉ 0,17–0,22 nên nhóm không dùng nó để kết luận.

**Giới hạn.** Mỗi người chỉ gán khoảng 80 mẫu; đồng thuận giữa hai người chỉ 65% (kappa 0,58, khoảng tin cậy rộng 0,40–0,75); 31,5% review không có chủ đề cụ thể; từ điển được xây trên chính tập review này nên chưa kiểm tra trên dữ liệu mới.
