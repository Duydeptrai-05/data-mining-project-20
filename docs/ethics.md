# Đạo đức, riêng tư, công bằng

Chủ: D. Số liệu: A7 (outputs/a7/a7_results.json), C (results.json: q07, nb05_ethics_rank_bias), D (results.json: nb04_*).

## 1. Xếp hạng thiên lệch theo số đánh giá
- **Ai bị hại:** nhà phát triển app có nhiều đánh giá thật nhưng điểm thấp hơn 5,0; và người dùng dashboard dựa vào top-10 để chọn app hoặc đối tác.
- **Cơ chế:** xếp hạng chỉ theo điểm trung bình, mà app ít đánh giá dễ có điểm cực đoan.
- **Số liệu:** 271 app có đúng 5,0 điểm, trong đó 266 app (98,2%) có dưới 50 đánh giá trên store. Trong top-10 thô của 33 danh mục (520 vị trí), 305 vị trí (58,7%) thuộc app dưới 50 đánh giá; riêng FAMILY là 65/67 (97,0%).
- **Biện pháp:** ngưỡng `min_store_reviews` = 50 và `min_cell_n` = 30; ô dưới ngưỡng không được diễn giải; mọi số trên dashboard ghi kèm n.

## 2. Tiếng nói bị thiếu
- **Ai bị hại:** người dùng của các danh mục có ít review có văn bản, và nhà phát triển có app bị loại do lệch tên khi nối review với app.
- **Cơ chế:** review chỉ nối với app qua tên app; chỉ 816/9 638 app (8,5%) có review có văn bản. 54 tên không khớp bị loại: 1 489 review (4,85% review không trùng lặp), trong đó 9 tên (16,7%, 225 review) không phải chữ Latin. Nguyên nhân của 45 tên chữ Latin còn lại chưa được kết luận.
- **Số liệu theo nhóm (chỉ số đại diện = tỉ lệ review / tỉ lệ app):** FAMILY 0,45 (chiếm 19,4% số app nhưng chỉ 8,7% số review; 3,7% app có văn bản); COMICS 0,28; ngược lại ENTERTAINMENT 2,76 (24,1% app có văn bản) và DATING 2,19. Sáu danh mục dưới 30 review tiêu cực: COMICS 1, EVENTS 16, AUTO_AND_VEHICLES 17, PARENTING 23, MAPS_AND_NAVIGATION 27, WEATHER 28.
- **Biện pháp:** loại các danh mục này khỏi biểu đồ chủ đề; đếm và báo cáo công khai lượng dữ liệu bị loại (decision log); không kết luận thay cho danh mục thiếu mẫu.

## 3. Riêng tư
- **Ai bị hại:** người viết review, vì văn bản có thể vô tình chứa thông tin cá nhân.
- **Cơ chế:** văn bản review gốc nằm trong schema staging của cơ sở dữ liệu.
- **Biện pháp:** dashboard không hiển thị review thô; role `superset_ro` chỉ đọc schema `mart`; `mart.review_topic` chỉ chứa `review_id` và chủ đề; repo không chứa văn bản review (file nhãn chỉ có id và nhãn); dữ liệu nguồn dùng đúng giấy phép CC BY 3.0.

## 4. Gắn nhầm chủ đề phàn nàn
- **Ai bị hại:** nhà phát triển (nhất là app nhỏ) bị gắn nhầm lý do phàn nàn, và người đọc dashboard hiểu sai nguyên nhân.
- **Cơ chế:** chủ đề được gán bằng từ điển, không phải mô hình đã kiểm chứng.
- **Số liệu:** precision gộp 8 chủ đề là 0,36 (23/64, Wilson 0,25–0,48) theo nhãn của D và 0,52 (35/67, Wilson 0,40–0,64) theo nhãn của A. Hai người đồng thuận 26/40 = 65% (Wilson 0,50–0,78), kappa 0,58. Chủ đề thiet_bi chỉ 0,22 (D) và 0,17 (A); nhóm "khac" chiếm 31,5% (1 909/6 057).
- **Biện pháp:** chú thích precision ngay trên chart; không dùng thiet_bi và tai_khoan để kết luận; không dùng chủ đề để xếp hạng hay đánh giá từng app.

## 5. Giới hạn (định tính, không có số)
- Dữ liệu đã cũ: `Last Updated` chỉ đến 2018-08.
- Review giả có thể làm lệch điểm; nhóm không dựng bộ phát hiện nên không có số.
- Nhãn `Sentiment` do công cụ từ điển sinh ra, không rõ nguồn; file review không có số sao.
- Chỉ nói "đi cùng", không nói "gây ra".