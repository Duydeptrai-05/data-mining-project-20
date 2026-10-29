# Ghi chú star schema (B)
ERD đặt trong `docs/erd/` (xuất ảnh từ pgAdmin/dbdiagram.io sau khi chạy 02).

| Fact | Grain (một dòng là gì) |
|---|---|
| dw.fact_app | một app sau khử trùng |
| dw.fact_review | một review có văn bản, sau khử trùng, nối được với một app |

Dimension: dim_category (**conformed**, dùng chung hai fact), dim_content_rating, dim_price, dim_size, dim_install, dim_date. Mỗi dim có dòng Unknown (key = -1); khoá ngoại fact NOT NULL.

## Khác với bản kế hoạch (cần cả nhóm biết)
- `fact_review` **không có `topic_key`.** Chủ đề phàn nàn nằm ở `mart.review_topic (review_id, topic)` vì nb04 chạy SAU khi dw đã dựng xong.
- `fact_review` và `fact_app` có thêm `src_row_id` để truy vết về file nb02. D lấy văn bản review từ `stg.review_all_rows` nối theo `src_row_id` (văn bản KHÔNG nằm trong dw hay mart).
- `fact_app` giữ `app_name`, `app_name_norm` (tên app là thuộc tính suy biến, dùng để nối review).
- `Dim_Date` là ngày **cập nhật bản** của app (Last Updated), không phải ngày review (dữ liệu không có ngày review).
- `age_days` tính so với ngày lớn nhất trong dữ liệu, không dùng ngày hôm nay.
- Ngưỡng (điểm thấp ≤ 3.0, `min_store_reviews`, `min_cell_n`) nằm ở `config.py`, `run_all.py` ghi vào `mart.params`; view và `04` đọc từ đó.

## Quy tắc drill-across
Không join `fact_review` vào `fact_app` rồi `AVG(rating)` (điểm app bị lặp theo số review). Tổng hợp từng fact lên danh mục riêng rồi nối (xem `q06` trong `04-olap-queries.sql`).

## Thứ tự và quyền
`00` (một lần) → `01` → nạp CSV → `02` → `03` → `05` → `04`. Quyền `superset_ro` cấp ở **cuối 05**. Không chạy lại 05 sau nb04.
Hợp đồng cột cho nb04 (D): đọc `dw.fact_review` + `dw.dim_category` + `stg.review_all_rows` (văn bản), ghi `mart.review_topic`.
