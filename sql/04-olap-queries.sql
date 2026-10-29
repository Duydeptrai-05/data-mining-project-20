-- 04-olap-queries.sql | Viết cùng C. B: cú pháp + chạy lại được. C: chốt/duyệt câu hỏi nghiệp vụ.
-- BẢN NHÁP: C xem lại từng câu hỏi, sửa/thêm/bớt, và phải GIẢI THÍCH ĐƯỢC từng dòng tổng của ROLLUP/CUBE.
--
-- Quy ước để run_all tự chạy và xuất CSV: mỗi truy vấn bắt đầu bằng một dòng
--     -- @query <ten_file_csv>
-- Kết quả ghi vào outputs/olap/<ten_file_csv>.csv và được gom vào results.json.
-- Ngưỡng lấy từ mart.params (nguồn duy nhất, đồng bộ với config.py), KHÔNG gõ cứng số.
-- Drill-across: KHÔNG join fact_review vào fact_app rồi AVG(rating); tổng hợp từng fact riêng rồi nối theo danh mục.
-- Cần đủ 3 nhóm kỹ thuật theo đề: ROLLUP/GROUPING SETS (có GROUPING()), CUBE, window function.

-- @query q01_rollup_category_pricetype
-- Câu hỏi: điểm trung bình/trung vị theo danh mục × Free/Paid, kèm dòng tổng từng cấp?
SELECT CASE WHEN GROUPING(c.category)   = 1 THEN 'ALL' ELSE c.category   END AS category,
       CASE WHEN GROUPING(p.price_type) = 1 THEN 'ALL' ELSE p.price_type END AS price_type,
       COUNT(*)                                                           AS n_apps,
       ROUND(AVG(f.rating), 3)                                            AS avg_rating,
       ROUND((PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY f.rating))::numeric, 2) AS median_rating
FROM dw.fact_app f
JOIN dw.dim_category c USING (category_key)
JOIN dw.dim_price    p USING (price_key)
CROSS JOIN mart.params prm
WHERE f.rating IS NOT NULL AND f.store_reviews >= prm.min_store_reviews
GROUP BY ROLLUP (c.category, p.price_type)
ORDER BY GROUPING(c.category), GROUPING(p.price_type), c.category, p.price_type;

-- @query q02_groupingsets_lowrate_category_contentrating
-- Câu hỏi: tỉ lệ app điểm thấp theo danh mục × content rating, và từng chiều riêng, và toàn cục?
SELECT CASE WHEN GROUPING(c.category)       = 1 THEN 'ALL' ELSE c.category       END AS category,
       CASE WHEN GROUPING(cr.content_rating) = 1 THEN 'ALL' ELSE cr.content_rating END AS content_rating,
       COUNT(*)                                                                    AS n_apps,
       SUM((f.rating <= prm.low_rating_threshold)::int)                            AS n_low,
       ROUND(AVG((f.rating <= prm.low_rating_threshold)::int), 4)                  AS low_rate
FROM dw.fact_app f
JOIN dw.dim_category       c  USING (category_key)
JOIN dw.dim_content_rating cr USING (content_key)
CROSS JOIN mart.params prm
WHERE f.rating IS NOT NULL AND f.store_reviews >= prm.min_store_reviews
GROUP BY GROUPING SETS ((c.category, cr.content_rating), (c.category), (cr.content_rating), ())
ORDER BY GROUPING(c.category), GROUPING(cr.content_rating), c.category, cr.content_rating;

-- @query q03_cube_lowrate_price_install
-- Câu hỏi: tỉ lệ điểm thấp theo giá (Free/Paid) × band lượt cài, mọi tổ hợp tổng?
SELECT CASE WHEN GROUPING(p.price_type)   = 1 THEN 'ALL' ELSE p.price_type   END AS price_type,
       CASE WHEN GROUPING(i.install_band) = 1 THEN 'ALL' ELSE i.install_band END AS install_band,
       COUNT(*)                                                                  AS n_apps,
       SUM((f.rating <= prm.low_rating_threshold)::int)                          AS n_low,
       ROUND(AVG((f.rating <= prm.low_rating_threshold)::int), 4)                AS low_rate
FROM dw.fact_app f
JOIN dw.dim_price   p USING (price_key)
JOIN dw.dim_install i USING (install_key)
CROSS JOIN mart.params prm
WHERE f.rating IS NOT NULL AND f.store_reviews >= prm.min_store_reviews
GROUP BY CUBE (p.price_type, i.install_band)
ORDER BY GROUPING(p.price_type), GROUPING(i.install_band), p.price_type, i.install_band;

-- @query q04_window_rank_top3_in_category
-- Câu hỏi: top 3 app điểm cao nhất trong từng danh mục (đã loại app ít đánh giá)?
SELECT *
FROM (
  SELECT c.category, f.app_name, f.rating, f.store_reviews,
         RANK()         OVER (PARTITION BY c.category ORDER BY f.rating DESC, f.store_reviews DESC) AS rk,
         PERCENT_RANK() OVER (PARTITION BY c.category ORDER BY f.rating)                            AS pct_rank
  FROM dw.fact_app f
  JOIN dw.dim_category c USING (category_key)
  CROSS JOIN mart.params prm
  WHERE f.rating IS NOT NULL AND f.store_reviews >= prm.min_store_reviews
) x
WHERE rk <= 3
ORDER BY category, rk, app_name;

-- @query q05_share_of_total_by_category
-- Câu hỏi: mỗi danh mục chiếm bao nhiêu phần trăm số app (có điểm) của toàn bộ dữ liệu?
SELECT c.category,
       COUNT(*) AS n_apps,
       ROUND(COUNT(*)::numeric / SUM(COUNT(*)) OVER (), 4) AS share_of_total
FROM dw.fact_app f
JOIN dw.dim_category c USING (category_key)
WHERE f.rating IS NOT NULL
GROUP BY c.category
ORDER BY n_apps DESC, c.category;

-- @query q06_drill_across_apps_and_reviews
-- Câu hỏi: mỗi danh mục có bao nhiêu app, điểm trung bình, và tỉ lệ review Negative? (drill-across, không nhân dòng)
WITH app_agg AS (
  SELECT c.category, COUNT(*) AS n_apps, ROUND(AVG(f.rating), 3) AS avg_rating
  FROM dw.fact_app f JOIN dw.dim_category c USING (category_key)
  WHERE f.rating IS NOT NULL
  GROUP BY c.category
), rev_agg AS (
  SELECT c.category, COUNT(*) AS n_reviews,
         SUM((r.sentiment = 'Negative')::int) AS n_negative
  FROM dw.fact_review r JOIN dw.dim_category c USING (category_key)
  GROUP BY c.category
)
SELECT a.category, a.n_apps, a.avg_rating,
       COALESCE(r.n_reviews, 0)  AS n_reviews,
       COALESCE(r.n_negative, 0) AS n_negative,
       ROUND(r.n_negative::numeric / NULLIF(r.n_reviews, 0), 4) AS negative_share
FROM app_agg a
LEFT JOIN rev_agg r USING (category)
ORDER BY a.category;
