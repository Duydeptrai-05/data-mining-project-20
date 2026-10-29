-- 05-mart-views.sql | Chủ: B | Idempotent
-- mart = thứ DUY NHẤT Superset được đọc (role superset_ro). Không đưa review thô vào mart.
-- Chạy SAU 03 và TRƯỚC nb04. KHÔNG chạy lại 05 sau nb04 (sẽ xoá review_topic D vừa ghi).
-- Superset đọc view bằng quyền của chủ view (dm) nên superset_ro không cần quyền trên schema dw.

CREATE SCHEMA IF NOT EXISTS mart;

-- Tham số: giá trị thật do run_all.py ghi đè từ config.py (nguồn duy nhất).
DROP TABLE IF EXISTS mart.params CASCADE;
CREATE TABLE mart.params (
  low_rating_threshold NUMERIC NOT NULL,
  min_store_reviews    INT     NOT NULL,
  min_cell_n           INT     NOT NULL
);
INSERT INTO mart.params VALUES (3.0, 50, 30);

-- Bảng D (nb04) ghi vào: TRUNCATE rồi append, KHÔNG dùng if_exists='replace'.
-- review_id khớp dw.fact_review.review_id.
DROP TABLE IF EXISTS mart.review_topic CASCADE;
CREATE TABLE mart.review_topic (
  review_id INT  PRIMARY KEY,
  topic     TEXT NOT NULL
);

-- Khoảng tin cậy Wilson 95 phan tram cho tỉ lệ k/n
CREATE OR REPLACE FUNCTION mart.wilson_lo(k NUMERIC, n NUMERIC) RETURNS NUMERIC
LANGUAGE sql IMMUTABLE AS $$
  SELECT CASE WHEN n IS NULL OR n = 0 THEN NULL ELSE
    ROUND(GREATEST(0,
      ((k/n + 1.96^2/(2*n)) - 1.96*SQRT((k/n)*(1-k/n)/n + 1.96^2/(4*n^2))) / (1 + 1.96^2/n)), 4)
  END
$$;

CREATE OR REPLACE FUNCTION mart.wilson_hi(k NUMERIC, n NUMERIC) RETURNS NUMERIC
LANGUAGE sql IMMUTABLE AS $$
  SELECT CASE WHEN n IS NULL OR n = 0 THEN NULL ELSE
    ROUND(LEAST(1,
      ((k/n + 1.96^2/(2*n)) + 1.96*SQRT((k/n)*(1-k/n)/n + 1.96^2/(4*n^2))) / (1 + 1.96^2/n)), 4)
  END
$$;

-- Chart 1: tỉ lệ app điểm thấp theo danh mục (n_enough = false -> không diễn giải)
CREATE OR REPLACE VIEW mart.v_lowrated_by_category AS
SELECT c.category,
       COUNT(*)                                          AS n_apps,
       SUM((f.rating <= p.low_rating_threshold)::int)    AS n_low,
       ROUND(AVG((f.rating <= p.low_rating_threshold)::int), 4) AS low_rate,
       mart.wilson_lo(SUM((f.rating <= p.low_rating_threshold)::int), COUNT(*)) AS ci_low,
       mart.wilson_hi(SUM((f.rating <= p.low_rating_threshold)::int), COUNT(*)) AS ci_high,
       (COUNT(*) >= p.min_cell_n)                        AS n_enough
FROM dw.fact_app f
JOIN dw.dim_category c USING (category_key)
CROSS JOIN mart.params p
WHERE f.rating IS NOT NULL AND f.store_reviews >= p.min_store_reviews
GROUP BY c.category, p.min_cell_n;

-- Chart 2: điểm trung vị theo Free/Paid và band giá
CREATE OR REPLACE VIEW mart.v_rating_by_price AS
SELECT pr.price_type, pr.price_band, pr.band_order,
       COUNT(*) AS n_apps,
       ROUND((PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY f.rating))::numeric, 2) AS median_rating,
       ROUND(AVG(f.rating), 3) AS avg_rating,
       (COUNT(*) >= p.min_cell_n) AS n_enough
FROM dw.fact_app f
JOIN dw.dim_price pr USING (price_key)
CROSS JOIN mart.params p
WHERE f.rating IS NOT NULL AND f.store_reviews >= p.min_store_reviews
GROUP BY pr.price_type, pr.price_band, pr.band_order, p.min_cell_n;

-- Chart 3: tỉ lệ điểm thấp theo độ cũ bản cập nhật VÀ theo band lượt cài (cột dimension phân biệt)
CREATE OR REPLACE VIEW mart.v_lowrated_by_age_install AS
WITH base AS (
  SELECT f.rating, d.age_band, d.age_order, i.install_band, i.band_order AS install_order,
         p.low_rating_threshold AS thr, p.min_cell_n
  FROM dw.fact_app f
  JOIN dw.dim_date    d USING (update_key)
  JOIN dw.dim_install i USING (install_key)
  CROSS JOIN mart.params p
  WHERE f.rating IS NOT NULL AND f.store_reviews >= p.min_store_reviews
)
SELECT 'age'::text AS dimension, age_band AS band, age_order AS band_order,
       COUNT(*) AS n_apps,
       SUM((rating <= thr)::int) AS n_low,
       ROUND(AVG((rating <= thr)::int), 4) AS low_rate,
       mart.wilson_lo(SUM((rating <= thr)::int), COUNT(*)) AS ci_low,
       mart.wilson_hi(SUM((rating <= thr)::int), COUNT(*)) AS ci_high,
       (COUNT(*) >= min_cell_n) AS n_enough
FROM base GROUP BY age_band, age_order, min_cell_n
UNION ALL
SELECT 'install'::text, install_band, install_order,
       COUNT(*), SUM((rating <= thr)::int),
       ROUND(AVG((rating <= thr)::int), 4),
       mart.wilson_lo(SUM((rating <= thr)::int), COUNT(*)),
       mart.wilson_hi(SUM((rating <= thr)::int), COUNT(*)),
       (COUNT(*) >= min_cell_n)
FROM base GROUP BY install_band, install_order, min_cell_n;

-- Chart 4: chủ đề phàn nàn theo danh mục; app_group = low / not_low / no_rating (chỉ đếm, không chứa văn bản)
CREATE OR REPLACE VIEW mart.v_topic_by_category AS
SELECT c.category,
       CASE WHEN f.rating IS NULL THEN 'no_rating'
            WHEN f.rating <= p.low_rating_threshold THEN 'low'
            ELSE 'not_low' END AS app_group,
       t.topic,
       COUNT(*) AS n_reviews,
       ROUND(COUNT(*)::numeric / SUM(COUNT(*)) OVER (PARTITION BY c.category,
         CASE WHEN f.rating IS NULL THEN 'no_rating'
              WHEN f.rating <= p.low_rating_threshold THEN 'low'
              ELSE 'not_low' END), 4) AS share_in_group
FROM mart.review_topic t
JOIN dw.fact_review r ON r.review_id = t.review_id
JOIN dw.fact_app    f ON f.app_key   = r.app_key
JOIN dw.dim_category c ON c.category_key = r.category_key
CROSS JOIN mart.params p
GROUP BY c.category, app_group, t.topic, p.low_rating_threshold;

-- Chart 5: top 10 trong từng danh mục (chỉ giữ nếu kèm kết luận)
CREATE OR REPLACE VIEW mart.v_top10_in_category AS
SELECT *
FROM (
  SELECT c.category, f.app_name, f.rating, f.store_reviews,
         RANK() OVER (PARTITION BY c.category ORDER BY f.rating DESC, f.store_reviews DESC) AS rk
  FROM dw.fact_app f
  JOIN dw.dim_category c USING (category_key)
  CROSS JOIN mart.params p
  WHERE f.rating IS NOT NULL AND f.store_reviews >= p.min_store_reviews
) x
WHERE rk <= 10;

-- Quyền cho Superset: đặt Ở CUỐI file (role tạo bởi 00-init-roles.sql; nếu chưa có thì bỏ qua)
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'superset_ro') THEN
    GRANT USAGE ON SCHEMA mart TO superset_ro;
    GRANT SELECT ON ALL TABLES IN SCHEMA mart TO superset_ro;
  END IF;
END
$$;
