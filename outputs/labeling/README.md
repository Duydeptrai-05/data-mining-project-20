# Nhãn tay cho nb04 (chủ đề phàn nàn)
Người thực hiện: A (mẫu 1-80) và D (mẫu 41-120); 40 mẫu chồng nhau để đo mức đồng thuận.

- D rút 120 mẫu phân tầng theo chủ đề + mẫu từ nhóm "khác" (seed = 42).
- Mỗi người lưu file riêng: `labels_A.csv`, `labels_D.csv`.
- Cột: `sample_id, review_id, topic_label` (gán độc lập, không xem nhãn của nhau).
- KHÔNG lưu nguyên văn review vào repo (có thể chứa thông tin cá nhân). Chỉ lưu review_id.
- Báo cáo tỉ lệ khớp trên 40 mẫu chồng; precision kèm khoảng Wilson.
