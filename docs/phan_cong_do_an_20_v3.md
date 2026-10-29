# Kế hoạch & phân công: Đồ án 20 (v3, theo dữ liệu thật)

Thay thế hoàn toàn v2. **Không còn nhánh dự phòng**: dữ liệu đã được đo, mọi quyết định dưới đây là quyết định chốt.
Không thay thế `project-topics-20.md` mục 8 (vai trò) và mục 9 (10 lỗi mất điểm, phát ở tuần 4).
Nguồn: Google Play Store Apps (Kaggle). Hai file, SHA-256 đã ghi trong `data_quality_report.md`:
`googleplaystore.csv` (10 841 × 13) và `googleplaystore_user_reviews.csv` (64 295 × 5).
Giấy phép: A chép nguyên văn từ trang nguồn vào báo cáo (chưa có trong tài liệu này).

---

## 1. Câu hỏi, đơn vị phân tích, giới hạn

**Câu hỏi (một câu):** *Với một nhà phát hành ứng dụng, những danh mục và đặc điểm nào (giá, dung lượng, lượt cài, độ mới của bản cập nhật) đi cùng tỉ lệ app điểm thấp cao nhất, và người dùng phàn nàn về chủ đề gì nhiều nhất trong từng danh mục?*

- **Một dòng nghĩa là gì:** Fact_App = một app (sau khử trùng); Fact_Review = một review có văn bản (sau khử trùng).
- **"Điểm thấp" (low-rated)** = `Rating ≤ 3.0` trên app có điểm và `Reviews ≥ min_store_reviews`. Lý do chọn 3.0: ngưỡng ≤ 2.0 chỉ có khoảng 68 dòng, quá ít để chia theo danh mục.
- **Tham số đặt tên trong `config.py` (chốt ở G1, không đổi sau đó):** `min_store_reviews = 50` (thử thêm 500 ở nb05), `min_cell_n = 30` (số app tối thiểu mỗi ô khi diễn giải).
- Hai khái niệm "ít review" **khác nhau, đặt hai tên**: `Reviews` của bảng app (lượt đánh giá trên store) và số dòng trong file review (chỉ là mẫu theo app).
- **Dữ liệu không trả lời được:** (1) review nào cho mấy sao (file review không có số sao); (2) thay đổi theo thời gian hay phiên bản (không có ngày review; `Last Updated` chỉ là một snapshot đến 2018-08); (3) nguyên nhân (chỉ có thể nói "đi cùng", không nói "gây ra"); (4) đối chiếu điểm app với điểm tính lại từ review (không tính lại được); (5) app không có review (chỉ khoảng 9–10% tên app có review) và app ngoại ngữ bị loại do lệch tên (xem 2). Dữ liệu đã cũ (2018).
- Văn bản dùng "nhãn cảm xúc Negative" làm **đại diện** cho phàn nàn, không phải "một sao". Phải nói rõ điều này trong báo cáo.

---

## 2. Dữ kiện đã đo → quyết định (hạt giống của decision log)

A chép bảng này vào `decision_log.md`, thêm cột Người quyết/Ngày và **số trước → sau** do nb02 tính lại (số dưới đây là lần đo thô, chưa khử trùng).

| # | Vấn đề (đã đo) | Quyết định |
|---|---|---|
| 1 | **1 dòng lệch cột** (Rating = 19, Category = "1.9", Installs = "Free", Price = "Everyone", Reviews = "3.0M"): mọi trường dịch trái một cột | Loại, `drop_reason = misaligned`. Không sửa tay (cần tra ngoài dữ liệu) |
| 2 | **483 dòng trùng hoàn toàn** ở bảng app | Loại, `exact_dup` |
| 3 | Sau bước 2 còn 10 358 dòng nhưng chỉ **9 660 tên**: 698 dòng cùng tên khác thuộc tính | Giữ dòng có `Reviews` lớn nhất (hoà: `Last Updated` mới nhất). Đo ảnh hưởng bằng 3 phiên bản dữ liệu (A0/A1/A2, xem 4.3) |
| 4 | **Rating thiếu 1 474 (13,6%)** | Không điền. Loại khỏi phân tích điểm, ghi kết luận "cho app đã có điểm". Kiểm tra phân bố `Installs` của nhóm thiếu để nêu khả năng không ngẫu nhiên |
| 5 | Rating dồn về đầu cao: **274 app đúng 5.0**; ≤ 2.0 chỉ ~68 dòng | Ngưỡng low-rated 3.0 (mục 1) và `min_store_reviews` để loại điểm của app ít đánh giá |
| 6 | `Installs` 22 giá trị dạng "10,000+", cả "0" và "0+" | Đổi thành cận dưới số nguyên + **band thứ tự**. Không tính trung bình trên cận dưới, dùng band/trung vị band |
| 7 | `Size`: 1 695 dòng "Varies with device" (15,6%), trộn M và k | Đổi sang MB (k ÷ 1024). "Varies" → NULL + band `Varies`. Không điền trung bình |
| 8 | `Price` có "$"; 1 dòng `Type` thiếu | Bỏ "$" → số. `Type` thiếu: gán theo `Price` (0 → Free), ghi log |
| 9 | `Last Updated`: chuỗi "Tháng ngày, năm", từ 2010-05 đến 2018-08 | Parse. "Độ cũ" tính so với **ngày lớn nhất trong dữ liệu (2018-08-08)**, không dùng ngày hôm nay |
| 10 | `Genres`: 120 giá trị, có dạng nhiều giá trị "A;B" | Lấy genre đầu làm `genre_primary`. Không dùng bảng bridge |
| 11 | Review: **33 616 / 64 295 dòng (52,3%) trùng hoàn toàn** | Loại. Khử trùng theo (App, văn bản) |
| 12 | Review trống 26 868 (41,8%); 5 dòng có nhãn nhưng không có văn bản | Giữ ở staging, loại khỏi phân tích văn bản (`no_text`) |
| 13 | Nhãn `Sentiment` (3 giá trị) kèm `Polarity` ∈ [-1, 1] và `Subjectivity`: kiểu đầu ra của công cụ từ điển. Nguồn sinh nhãn không ghi rõ | A đọc mô tả dataset để xác minh. Dùng làm đại diện phụ, **không huấn luyện mô hình dự đoán nhãn này** (vòng tròn) |
| 14 | Khoá nối review → app chỉ là **tên app**. 1 074 tên trong review, 1 020 khớp bảng app, 54 không khớp (nhiều tên có chữ không phải Latin hoặc ký tự đặc biệt) | Chuẩn hoá (strip, NFKC, casefold) rồi nối vào app đã khử trùng (mỗi tên một app, không nhân dòng). Phần còn lại loại, `no_app_match`, **đếm** để dùng ở mục đạo đức |
| 15 | Sau khử trùng, trung vị ~35 review có văn bản mỗi app, chỉ ~865 app có văn bản | Số review trong file là mẫu theo app, **không dùng làm độ phổ biến**. Độ phổ biến dùng `Reviews` của bảng app |

---

## 3. Kho dữ liệu (tiêu chí 4)

- **Ranh giới làm sạch (một chỗ duy nhất):** nb02 (Python) parse kiểu, gắn `kept` và `drop_reason` cho **mọi dòng**, xuất `app_all_rows.csv`, `review_all_rows.csv`. `01-staging.sql` nạp tất cả dòng. `03-transform.sql` lọc `kept = true` và dựng fact. Nhờ vậy nb05 chạy phép thử "không khử trùng" ngay từ staging.
- **Fact_App** (grain: một app sau khử trùng): `app_key`, `category_key`, `content_key`, `price_key`, `size_key`, `install_key`, `update_key`, `rating` (nullable), `store_reviews`, `size_mb`, `price`.
- **Fact_Review** (grain: một review có văn bản sau khử trùng): `review_id`, `app_key`, `category_key`, `sentiment`, `polarity`, `subjectivity`, `topic_key`.
- **Dim:** `Dim_Category` (category, genre_primary; **conformed**, dùng chung hai fact), `Dim_ContentRating`, `Dim_Price` (Free/Paid + band), `Dim_Size` (band, có `Varies`), `Dim_Install` (band), `Dim_Date` (từ `Last Updated`, ghi rõ là ngày cập nhật app). Dimension nào cũng có dòng `Unknown` (`key = -1`); khoá ngoại fact `NOT NULL`.
- **Quy tắc drill-across:** không join Fact_Review vào Fact_App rồi `AVG(rating)` (điểm app bị lặp theo số review). Tổng hợp từng fact lên `category_key` (hoặc `app_key`) riêng, rồi nối bằng dimension chung.
- **Script:** `01-staging` → `02-star-schema` → `03-transform` (idempotent, `DROP ... CASCADE` rồi tạo lại) + `04-olap-queries` + `05-mart-views`.
- **`04-olap-queries.sql`** (mỗi truy vấn có comment nêu câu hỏi nghiệp vụ): `ROLLUP`/`GROUPING SETS` (danh mục × Free/Paid, kèm `GROUPING()` để dán nhãn dòng tổng), `CUBE` hoặc `GROUPING SETS` trên danh mục × content rating, window function (`RANK`/`PERCENT_RANK` trong danh mục có lọc `min_store_reviews`, tỉ trọng trên tổng bằng `SUM() OVER`).

---

## 4. Khai phá, đánh giá, đạo đức, dashboard

### 4.1 Họ chính: Mô tả / OLAP (nb03 + `04-olap`) — tiêu chí 5
Trả lời câu hỏi ở cấp **app**: tỉ lệ low-rated theo danh mục, giá, dung lượng, band lượt cài, độ cũ. Luôn ghi *n* bên cạnh mọi số và nêu cấp phân tích (app hay danh mục). Không tính tương quan trên số đã gộp theo danh mục mà không ghi *n* và số danh mục.

### 4.2 Họ phụ: khai phá văn bản (nb04) — tiêu chí 6
Một hướng duy nhất, không dự đoán nhãn, nên không có train/test cho văn bản; TF-IDF dùng để mô tả.
1. Đơn vị: review đã khử trùng, có văn bản, `Sentiment = Negative`.
2. NLTK (tokenise, stopwords, stemming) → TF-IDF theo danh mục → xây lexicon khoảng 5–8 chủ đề phàn nàn + nhóm "khác" → gán chủ đề bằng luật → bảng `review_topic` ghi vào `mart` (chỉ `TRUNCATE` rồi append, không dùng `if_exists='replace'`).
3. Nhãn tay: 120 mẫu phân tầng theo chủ đề + mẫu từ nhóm "khác" (ước lượng bỏ sót). A và D gán độc lập, 40 mẫu chồng nhau, báo tỉ lệ khớp (Cohen's kappa tuỳ chọn). Precision báo kèm khoảng Wilson. Lưu id mẫu, seed 42.
4. Baseline: luôn gán chủ đề phổ biến nhất.
5. Nối với câu hỏi: chủ đề × danh mục, và chủ đề trong review của app low-rated (có ghi *n*, ô dưới `min_cell_n` không diễn giải). Báo cáo phải nêu **text cho thấy điều gì mà điểm số không cho thấy** (lý do phàn nàn).

### 4.3 nb05: kiểm chứng độ vững — tiêu chí 7
Ba phiên bản dữ liệu: **A0** = bỏ dòng lệch cột; **A1** = A0 + bỏ trùng hoàn toàn; **A2** = A1 + một dòng mỗi tên (bản chính).

| Phép thử | Cách làm |
|---|---|
| Khử trùng | So kết luận trên A0, A1, A2 |
| Ngưỡng ít đánh giá | `min_store_reviews` = 0, 50, 500 |
| Trung vị thay trung bình | Đặt cạnh nhau |
| Khoảng tin cậy | Bootstrap 95%, **resample theo app**, `default_rng(42)` |
| Baseline | Tỉ lệ low-rated toàn cục, và **hoán vị nhãn danh mục** (1 000 lần) để xem chênh lệch giữa danh mục có vượt nhiễu không |
| Độ ổn định xếp hạng | Spearman và độ trùng top-5/bottom-5 giữa các phép thử |
| Tỉ lệ hiếm | Khoảng Wilson; ô dưới `min_cell_n` không diễn giải; so sánh nhiều danh mục thì báo kích thước chênh lệch và ghi rõ là khám phá |

Kết quả: bảng "kết luận nào giữ, nào đổi, đổi bao nhiêu" + phân tích lỗi bằng lời (danh mục nào nhạy nhất, vì sao).

### 4.4 Đạo đức, riêng tư, công bằng (tiêu chí 9)
1. **Xếp hạng thiên lệch theo *n*:** xếp thô bằng window function đẩy app ít đánh giá lên đầu hoặc xuống cuối (xem 274 app đúng 5.0). Đo: so thứ hạng thô với thứ hạng có `min_store_reviews`. Số liệu: C cung cấp, D diễn giải.
2. **Tiếng nói bị thiếu:** 54 tên app trong file review không khớp (nhiều app ngoại ngữ) bị loại, và văn bản là bản dịch. Kết luận chủ yếu đại diện người dùng tiếng Anh. Đo: tỉ lệ loại theo danh mục (A cung cấp). Giảm thiểu: nêu rõ phạm vi, không suy rộng.
3. **Riêng tư:** văn bản review có thể chứa thông tin cá nhân. **Không hiển thị review thô trên dashboard**; role Superset chỉ đọc schema `mart`.
4. **Gắn nhầm cho nhà phát hành:** kết luận "danh mục X tệ" có thể gây hại cho nhà phát hành nhỏ; dữ liệu cũ 2018. Ngoài ra thảo luận (định tính, không có số vì không dựng bộ phát hiện) về review giả làm lệch điểm.

### 4.5 Dashboard (tiêu chí 8): 5 chart, mỗi chart một câu hỏi
Tiêu đề chart là **kết luận**, có *n*, có bộ lọc (danh mục, Free/Paid, content rating).
1. Tỉ lệ app điểm thấp theo danh mục (Wilson; ô dưới `min_cell_n` mờ/ẩn).
2. Điểm trung vị theo Free/Paid và band giá.
3. Tỉ lệ điểm thấp theo độ cũ của bản cập nhật và theo band lượt cài.
4. Chủ đề phàn nàn hàng đầu theo danh mục.
5. Top 10 trong danh mục đã chọn (có lọc `min_store_reviews`; giữ chỉ khi kèm kết luận).

B viết view cho cả 5 chart (B5), C dựng chart 1–3 (C7), D dựng chart 4–5 và ghép bố cục (D8). Nhờ một người ngoài nhóm thử dùng.

---

## 5. Vai trò và tiêu chí rubric

Nhóm 4 người. Mỗi tiêu chí một chủ; riêng 11 tách đôi, 10 chung (A thu).

| | Vai trò | Chủ tiêu chí (điểm tối đa) | Review bởi |
|---|---|---|---|
| **A** | Chất lượng dữ liệu, tiền xử lý, báo cáo | 2 (0,75), 3 ★ (1,25), 11b báo cáo + phân công (0,25) = 2,25 | D |
| **B** | Kho dữ liệu, tái lập | 4 (1,25), 11a tái lập (0,25) = 1,50 | A |
| **C** | Câu hỏi, OLAP, đánh giá | 1 (0,75), 5 ★ (1,50), 7 ★ (1,25) = 3,50 | B |
| **D** | Text mining, dashboard, đạo đức | 6 (0,50), 8 ★ (1,00), 9 ★ (0,75) = 2,25 | C |
| *Chung* | Minh bạch AI | 10 ★ (0,50): mỗi người ghi `ai_usage/<tên>.md`, A thu, D xác nhận | |

Tổng = 10. Tiêu chí 4 và 5 cùng dùng `04-olap`: B chịu trách nhiệm schema và script chạy lại được, C chịu trách nhiệm nội dung nghiệp vụ và giải thích được từng dòng tổng của `ROLLUP`.

### Bảng việc cụ thể

**Điểm công** là đơn vị tải tương đối để so sánh giữa 4 người (không phải giờ thật). Review theo vòng A → B → C → D → A: người review đối chiếu số, không chỉ đọc code. Ba việc v2 từng có mà bản v3 đầu bị rơi (tải dữ liệu, `run_all` + `results.json`, README) đã được gán lại: A1, B6, B8.

| ID | Hạn | Việc (sản phẩm cụ thể) | Điểm công |
|---|---|---|---:|
| **A1** | G0 | `download_data.py` (có kiểm SHA-256), chép nguyên văn giấy phép, `data_quality_report.md` | 2 |
| **A2** | G1 | nb01: tái hiện các vấn đề ở mục 2 bằng số tự đếm, mỗi vấn đề có bằng chứng và hệ quả | 3 |
| **A3** | G1 | nb02 v0: parse kiểu, gắn `kept`/`drop_reason`, `assert` miền giá trị, xuất `app_all_rows.csv` và `review_all_rows.csv` | 4 |
| **A4** | G3 | nb02 bản cuối + `decision_log.md` (≥ 12 dòng, mỗi dòng có số trước → sau) | 4 |
| **A5** | G3 | Đo ảnh hưởng của từng quyết định lớn lên con số cuối | 2 |
| **A6** | G3 | Gán nhãn tay mẫu 1–80 (D gán 41–120, 40 mẫu chồng để đo đồng thuận) | 2 |
| **A7** | G3 | Số liệu cho đạo đức: tỉ lệ app/review bị loại theo danh mục (54 tên không khớp, review trống) | 1 |
| **A8** | G4 | Ghép báo cáo theo template, đối chiếu mọi số với `results.json`, đánh số hình/bảng | 4 |
| **A9** | G4 | Thu `ai_usage` của cả nhóm; viết mục phân công cụ thể | 1 |
| **A10** | G4 | Viết chương Dữ liệu & tiền xử lý; làm slide phần này | 3 |
| **A11** | G4 | Ghép slide cả nhóm | 2 |
| **B1** | G0 | Repo, `config.py`, `requirements.txt` ghim phiên bản, `.gitignore`, `.env.example` | 2 |
| **B2** | G1 | PostgreSQL, user `dm`, role chỉ đọc schema `mart` cho Superset | 2 |
| **B3** | G1 | ERD + grain từng fact, `01-staging.sql`, `02-star-schema.sql` | 4 |
| **B4** | G2 | `03-transform.sql` nạp bản v0, đối chiếu `COUNT`/`AVG` theo danh mục với A (phải khớp) | 4 |
| **B5** | G2 | `05-mart-views.sql`: view cho cả 5 chart + DDL bảng `review_topic` | 3 |
| **B6** | G2 → G3 | `run_all` (khung ở G2, đủ ở G3) và `results.json` (gồm kết quả `04`) | 4 |
| **B7** | G3 | `04-olap-queries.sql` (viết cùng C; B chịu trách nhiệm cú pháp và chạy lại được) | 3 |
| **B8** | G3 | README + dry-run trên clone sạch, ghi lỗi và sửa | 2 |
| **B9** | G4 | Dựng lại trên máy sạch, chạy hai lần cho cùng số, thử rút mạng | 2 |
| **B10** | G4 | Viết chương Kho dữ liệu & OLAP; làm slide phần này | 3 |
| **C1** | G0 | Câu hỏi một câu, giới hạn, định nghĩa low-rated, tham số vào log | 2 |
| **C2** | G1 | Thiết kế nb05, chốt `min_store_reviews`, `min_cell_n`, baseline | 2 |
| **C3** | G2 | nb03: tỉ lệ low-rated theo danh mục, giá, dung lượng, lượt cài, độ cũ; có *n* | 5 |
| **C4** | G3 | `04-olap`: chốt danh sách câu hỏi nghiệp vụ, viết truy vấn cùng B, giải thích được từng dòng `ROLLUP` | 3 |
| **C5** | G3 | nb05: 7 phép thử độ vững (mục 4.3) | 6 |
| **C6** | G3 | Số liệu cho đạo đức: thứ hạng thô so với thứ hạng có ngưỡng | 2 |
| **C7** | G3 | Dựng chart 1–3 trên Superset (từ view của B) | 3 |
| **C8** | G4 | Viết chương Câu hỏi, Khai phá chính & Đánh giá; làm slide phần này | 5 |
| **D1** | G0 | Superset Docker, kết nối Postgres, 1 chart thử | 3 |
| **D2** | G1 | TF-IDF trên CSV v0 → từ vựng chủ đề bản đầu | 3 |
| **D3** | G2 | nb04 bản đầu (đọc từ CSV v0) | 4 |
| **D4** | G2 | Rút 120 mẫu nhãn tay phân tầng (seed 42) + hướng dẫn gán | 1 |
| **D5** | G2 | Nháp `ethics.md` | 2 |
| **D6** | G3 | Gán nhãn tay mẫu 41–120 | 2 |
| **D7** | G3 | nb04 bản cuối đọc từ `mart`, ghi `review_topic`, precision kèm Wilson | 4 |
| **D8** | G3 | Chart 4–5, bố cục dashboard, nhờ người ngoài nhóm thử | 4 |
| **D9** | G3 | Chốt `ethics.md` (ghép số liệu từ A7 và C6) | 2 |
| **D10** | G4 | Viết chương Văn bản, Dashboard & Đạo đức; làm slide phần này | 3 |
| **D11** | G4 | Tổ chức tập thuyết trình cả nhóm | 1 |

**Tổng tải:** A = 28 · B = 29 · C = 28 · D = 29. C giữ nhiều điểm rubric nhất (3,50) nhưng ít việc hạ tầng nhất, nên được thêm chart 1–3 và chương báo cáo dài hơn.

**Nhóm 5 người:** thêm E nhận tiêu chí 9 (đạo đức) và nhãn tay cùng A; E cũng nhận tiêu chí 7 (nb05) từ C; D giữ text mining + dashboard + ghép slide; E review D, C review E.

---

## 6. Cổng

| Cổng | Mốc | Xong khi |
|---|---|---|
| **G0 Đề cương** | Tuần 6 | Đã đo `shape/info` thật (xong); giấy phép chép; câu hỏi + giới hạn viết xong; Superset cài được và vẽ 1 chart thử; `ai_usage` đã bắt đầu |
| **G1 Checkpoint** | Tuần 8 | nb01 có bằng chứng; nb02 v0 qua `assert`; PostgreSQL chạy; ERD + grain được duyệt; tham số chốt. **Giữ gọn vì trùng tuần giữa kỳ** |
| **G2 Tiến độ** | Tuần 11 | `run_all` dựng staging → dw → mart, số dòng khớp A; nb03 và nb04 có kết quả đầu; `results.json` bản đầu; nháp ethics |
| **G3 Đủ kết quả** | ~Tuần 13 (tự đặt) | nb02 cuối + decision log; `04-olap` đủ ROLLUP/GROUPING SETS/window; nb03, nb05, nb04 xong; dashboard xong; ethics có ≥ 1 số liệu theo nhóm; **dry-run clone sạch đã chạy** |
| **G4 Nộp** | Tuần 15 | Clone mới + `run_all` chạy hết, hai lần cùng số, khi rút mạng; mọi số trong báo cáo truy được về `results.json`; notebook đã chạy kèm output; vấn đáp chéo xong |

**Khi bị chặn:** B chưa nạp xong → C và D làm trên CSV v0 bằng pandas. A chưa xong v0 → B viết SQL theo mục 3, D dựng khung dashboard. Cả nhóm chờ `mart` → A dựng khung báo cáo từ template.

---

## 7. Quy tắc kỹ thuật

- **Decision log:** bảng *Quyết định | Lý do kèm bằng chứng | Số bị ảnh hưởng (trước → sau) | Người quyết | Ngày*. Mỗi dòng phải có số thật; không ghi "đã làm sạch".
- **`run_all`:** kiểm file/checksum → nb02 → `01-staging` → `02-star-schema` → `03-transform` → `05-mart-views` → `04-olap-queries` (xuất kết quả ra CSV) → nb03 → nb05 → nb04 (ghi `review_topic` vào `mart`) → view phụ thuộc → `results.json`. Bảng do Python ghi phải ghi lại **sau** `05`. Windows lab không có bash thì viết `run_all.py` và ghi vào README.
- **`results.json`:** chứa mọi số báo cáo dùng (*n*, trung bình, CI, precision, **kết quả OLAP từ `04`**). Báo cáo lấy số từ đây, không chép tay.
- `random_state=42` / `default_rng(42)` mọi nơi có ngẫu nhiên. Gói NLTK ghi trong README (`punkt`, `punkt_tab`, `stopwords`).
- Nộp kèm notebook đã chạy (HTML hoặc `nbconvert --execute`) đúng commit.
- **Review PR:** PR nhỏ, reviewer đối chiếu số; vòng A → B → C → D → A. Đổi tên cột/view: sửa tài liệu trước, bên nhận xác nhận rồi mới sửa code.
- **Cân bằng tải:** họp 15 phút ở mỗi cổng, mỗi người báo giờ thực tế; lệch nhiều thì chuyển việc ngay. Phân công trong báo cáo viết cụ thể ("A chốt quy tắc loại dòng trùng và viết nb02"). Trước G4, mỗi người giải thích 15 phút một giai đoạn **của người khác**.

---

## 8. Checklist trước khi nộp

- [ ] Câu hỏi một câu, giới hạn nêu trước phân tích, dùng "đi cùng" không dùng "gây ra" (tc 1)
- [ ] Số dòng/cột tự đo, giấy phép, ≥ 3 vấn đề có bằng chứng (tc 2)
- [ ] Decision log có số trước → sau; không xoá outlier theo phản xạ; không rò rỉ (tc 3)
- [ ] ≥ 1 fact + 3 dim, grain nêu rõ, 3 script chạy lại được, OLAP thật (tc 4)
- [ ] Họ chính đúng đề (Mô tả/OLAP), giải thích được cơ chế (tc 5)
- [ ] Họ phụ nối với câu hỏi, nêu nó cho thấy gì mà họ chính không thấy (tc 6)
- [ ] Baseline, khoảng tin cậy, kết luận giữ/đổi, phân tích lỗi (tc 7)
- [ ] 4–6 chart, có lọc, tiêu đề là kết luận, có khuyến nghị cho người ra quyết định (tc 8)
- [ ] Đạo đức: ai bị hại, cơ chế, biện pháp, ≥ 1 số liệu theo nhóm (tc 9)
- [ ] AI usage khai báo đủ, số khớp hệ thống (tc 10)
- [ ] Template báo cáo, đánh số hình/bảng, `requirements.txt`, phân công cụ thể (tc 11)
- [ ] Không Olist; không cloud; chạy được khi rút mạng; mọi thành viên trả lời được câu hỏi chéo
