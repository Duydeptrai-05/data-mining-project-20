-- 03-transform.sql | Chủ: B | Chạy ngay sau 02 (02 đã tạo bảng rỗng)
-- Đọc stg (chỉ kept = true) -> dựng dim -> dựng fact. KHÔNG làm sạch lại ở đây (việc của nb02).
-- Sau khi chạy: scripts/reconcile.py đối chiếu COUNT / AVG(rating) theo danh mục với nb02 (phải khớp).

-- ---------- dim_category ----------
INSERT INTO dw.dim_category (category_key, category, genre_primary)
SELECT ROW_NUMBER() OVER (ORDER BY category, genre_primary), category, genre_primary
FROM (SELECT DISTINCT category, COALESCE(genre_primary, 'Unknown') AS genre_primary
      FROM stg.app_all_rows
      WHERE kept AND category IS NOT NULL) s;
INSERT INTO dw.dim_category VALUES (-1, 'Unknown', 'Unknown');

-- ---------- dim_content_rating ----------
INSERT INTO dw.dim_content_rating (content_key, content_rating)
SELECT ROW_NUMBER() OVER (ORDER BY content_rating), content_rating
FROM (SELECT DISTINCT content_rating FROM stg.app_all_rows
      WHERE kept AND content_rating IS NOT NULL) s;
INSERT INTO dw.dim_content_rating VALUES (-1, 'Unknown');

-- ---------- dim_price / dim_size / dim_install (band cố định) ----------
INSERT INTO dw.dim_price (price_key, price_type, price_band, band_order) VALUES
  (-1, 'Unknown', 'Unknown',    0),
  ( 1, 'Free',    'Free',       1),
  ( 2, 'Paid',    '$0.01-0.99', 2),
  ( 3, 'Paid',    '$1-4.99',    3),
  ( 4, 'Paid',    '$5-19.99',   4),
  ( 5, 'Paid',    '$20+',       5);

INSERT INTO dw.dim_size (size_key, size_band, band_order) VALUES
  (-1, 'Unknown', 0),
  ( 1, 'Varies',  1),
  ( 2, '<5MB',    2),
  ( 3, '5-20MB',  3),
  ( 4, '20-50MB', 4),
  ( 5, '50MB+',   5);

INSERT INTO dw.dim_install (install_key, install_band, band_order) VALUES
  (-1, 'Unknown',   0),
  ( 1, '<1K',       1),
  ( 2, '1K-10K',    2),
  ( 3, '10K-100K',  3),
  ( 4, '100K-1M',   4),
  ( 5, '1M-10M',    5),
  ( 6, '10M+',      6);

-- ---------- dim_date (ngày cập nhật bản) ----------
INSERT INTO dw.dim_date (update_key, full_date, year, month, quarter, age_days, age_band, age_order)
SELECT to_char(s.d, 'YYYYMMDD')::int,
       s.d,
       EXTRACT(YEAR FROM s.d)::int,
       EXTRACT(MONTH FROM s.d)::int,
       EXTRACT(QUARTER FROM s.d)::int,
       (m.max_d - s.d),
       CASE WHEN (m.max_d - s.d) <= 90  THEN '<=3m'
            WHEN (m.max_d - s.d) <= 365 THEN '3-12m'
            WHEN (m.max_d - s.d) <= 730 THEN '1-2y'
            ELSE '>2y' END,
       CASE WHEN (m.max_d - s.d) <= 90  THEN 1
            WHEN (m.max_d - s.d) <= 365 THEN 2
            WHEN (m.max_d - s.d) <= 730 THEN 3
            ELSE 4 END
FROM (SELECT DISTINCT last_updated AS d FROM stg.app_all_rows
      WHERE kept AND last_updated IS NOT NULL) s
CROSS JOIN (SELECT MAX(last_updated) AS max_d FROM stg.app_all_rows WHERE kept) m;
INSERT INTO dw.dim_date VALUES (-1, NULL, NULL, NULL, NULL, NULL, 'Unknown', 0);

-- ---------- fact_app ----------
INSERT INTO dw.fact_app
  (app_key, src_row_id, app_name, app_name_norm, category_key, content_key, price_key,
   size_key, install_key, update_key, rating, store_reviews, size_mb, price)
SELECT ROW_NUMBER() OVER (ORDER BY a.src_row_id),
       a.src_row_id, a.app_name, a.app_name_norm,
       COALESCE(c.category_key, -1),
       COALESCE(cr.content_key, -1),
       COALESCE(p.price_key, -1),
       COALESCE(s.size_key, -1),
       COALESCE(i.install_key, -1),
       COALESCE(d.update_key, -1),
       a.rating, a.store_reviews, a.size_mb, a.price
FROM (
  SELECT t.*,
    CASE WHEN t.price IS NULL THEN 'Unknown'
         WHEN t.price = 0     THEN 'Free'
         WHEN t.price < 1     THEN '$0.01-0.99'
         WHEN t.price < 5     THEN '$1-4.99'
         WHEN t.price < 20    THEN '$5-19.99'
         ELSE '$20+' END AS price_label,
    CASE WHEN t.size_is_varies THEN 'Varies'
         WHEN t.size_mb IS NULL THEN 'Unknown'
         WHEN t.size_mb < 5    THEN '<5MB'
         WHEN t.size_mb < 20   THEN '5-20MB'
         WHEN t.size_mb < 50   THEN '20-50MB'
         ELSE '50MB+' END AS size_label,
    CASE WHEN t.installs_min IS NULL THEN 'Unknown'
         WHEN t.installs_min < 1000     THEN '<1K'
         WHEN t.installs_min < 10000    THEN '1K-10K'
         WHEN t.installs_min < 100000   THEN '10K-100K'
         WHEN t.installs_min < 1000000  THEN '100K-1M'
         WHEN t.installs_min < 10000000 THEN '1M-10M'
         ELSE '10M+' END AS install_label
  FROM stg.app_all_rows t
  WHERE t.kept
) a
LEFT JOIN dw.dim_category       c  ON c.category = a.category
                                  AND c.genre_primary = COALESCE(a.genre_primary, 'Unknown')
LEFT JOIN dw.dim_content_rating cr ON cr.content_rating = a.content_rating
LEFT JOIN dw.dim_price          p  ON p.price_band   = a.price_label
LEFT JOIN dw.dim_size           s  ON s.size_band    = a.size_label
LEFT JOIN dw.dim_install        i  ON i.install_band = a.install_label
LEFT JOIN dw.dim_date           d  ON d.update_key   = to_char(a.last_updated, 'YYYYMMDD')::int;

-- ---------- fact_review ----------
-- Nối review -> app bằng tên đã chuẩn hoá (mỗi tên 1 app, không nhân dòng; unique index ở 02 bảo vệ).
INSERT INTO dw.fact_review
  (review_id, src_row_id, app_key, category_key, sentiment, polarity, subjectivity)
SELECT ROW_NUMBER() OVER (ORDER BY r.src_row_id),
       r.src_row_id, f.app_key, f.category_key, r.sentiment, r.polarity, r.subjectivity
FROM stg.review_all_rows r
JOIN dw.fact_app f ON f.app_name_norm = r.app_name_norm
WHERE r.kept;

ANALYZE dw.fact_app;
ANALYZE dw.fact_review;
