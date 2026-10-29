# Hợp đồng giữa các gói (đổi tên cột/view: sửa file này TRƯỚC, bên nhận xác nhận, rồi mới sửa code)

## A → B: file nb02 xuất ra `data/processed/`
`app_all_rows.csv` (MỌI dòng, kể cả bị loại) cột: src_row_id, app_name, app_name_norm, category, genre_primary,
rating (trống = NULL), store_reviews, size_mb, size_is_varies, installs_min, type, price, content_rating,
last_updated (YYYY-MM-DD), kept (true/false), drop_reason.
`review_all_rows.csv` cột: src_row_id, app_name, app_name_norm, review_text, sentiment, polarity, subjectivity, kept, drop_reason.
Yêu cầu: sau khử trùng mỗi `app_name_norm` xuất hiện ĐÚNG MỘT lần trong các dòng kept = true của app (index unique ở 02 sẽ báo lỗi nếu vi phạm).
Ô trống = NULL. Tên cột nào khác (A đổi) thì báo B sửa `sql/01-staging.sql`.

## B → C, D: schema `mart` (và `dw` cho notebook)
View: v_lowrated_by_category, v_rating_by_price, v_lowrated_by_age_install, v_topic_by_category, v_top10_in_category.
Bảng: mart.params, mart.review_topic (D ghi). Hàm: mart.wilson_lo / mart.wilson_hi.

## C, D → B: số liệu cho báo cáo
Notebook gọi `dmutils.save_result("ten_phan", obj)`; `build_results.py` gom vào `outputs/results.json`.
