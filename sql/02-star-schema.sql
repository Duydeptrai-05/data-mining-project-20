-- 02-star-schema.sql | Chủ: B | Idempotent (DROP SCHEMA ... CASCADE rồi tạo lại)
-- Grain:  fact_app    = 1 app sau khử trùng
--         fact_review = 1 review có văn bản sau khử trùng (và nối được với 1 app)
-- Mọi dimension có dòng Unknown (key = -1); khoá ngoại trong fact NOT NULL.
-- dim_category là CONFORMED: dùng chung cho cả hai fact.
-- Không lưu văn bản review trong dw (riêng tư). Chủ đề phàn nàn nằm ở mart.review_topic.

DROP SCHEMA IF EXISTS dw CASCADE;
CREATE SCHEMA dw;

CREATE TABLE dw.dim_category (
  category_key  INT  PRIMARY KEY,
  category      TEXT NOT NULL,
  genre_primary TEXT NOT NULL,
  UNIQUE (category, genre_primary)
);

CREATE TABLE dw.dim_content_rating (
  content_key    INT  PRIMARY KEY,
  content_rating TEXT NOT NULL UNIQUE
);

CREATE TABLE dw.dim_price (
  price_key  INT  PRIMARY KEY,
  price_type TEXT NOT NULL,           -- Free | Paid | Unknown
  price_band TEXT NOT NULL UNIQUE,
  band_order INT  NOT NULL
);

CREATE TABLE dw.dim_size (
  size_key   INT  PRIMARY KEY,
  size_band  TEXT NOT NULL UNIQUE,    -- có band 'Varies' (Varies with device)
  band_order INT  NOT NULL
);

CREATE TABLE dw.dim_install (
  install_key  INT  PRIMARY KEY,
  install_band TEXT NOT NULL UNIQUE,
  band_order   INT  NOT NULL
);

-- Ngày CẬP NHẬT BẢN của app (Last Updated), không phải ngày của review.
CREATE TABLE dw.dim_date (
  update_key INT  PRIMARY KEY,        -- YYYYMMDD
  full_date  DATE,
  year       INT,
  month      INT,
  quarter    INT,
  age_days   INT,                     -- so với ngày lớn nhất trong dữ liệu (không dùng ngày hôm nay)
  age_band   TEXT NOT NULL,
  age_order  INT  NOT NULL
);

CREATE TABLE dw.fact_app (
  app_key       INT  PRIMARY KEY,
  src_row_id    INT,                  -- truy vết về file nb02 xuất
  app_name      TEXT,
  app_name_norm TEXT,
  category_key  INT NOT NULL REFERENCES dw.dim_category,
  content_key   INT NOT NULL REFERENCES dw.dim_content_rating,
  price_key     INT NOT NULL REFERENCES dw.dim_price,
  size_key      INT NOT NULL REFERENCES dw.dim_size,
  install_key   INT NOT NULL REFERENCES dw.dim_install,
  update_key    INT NOT NULL REFERENCES dw.dim_date,
  rating        NUMERIC(2,1),         -- NULL = chưa có điểm (không điền)
  store_reviews BIGINT,               -- lượt đánh giá trên store (KHÁC số dòng trong file review)
  size_mb       NUMERIC,
  price         NUMERIC,
  CONSTRAINT chk_rating_domain CHECK (rating IS NULL OR rating BETWEEN 1 AND 5)
);
CREATE UNIQUE INDEX ux_fact_app_name_norm ON dw.fact_app (app_name_norm);

CREATE TABLE dw.fact_review (
  review_id    INT  PRIMARY KEY,
  src_row_id   INT  NOT NULL UNIQUE,  -- nối lại stg.review_all_rows để lấy văn bản khi cần (nb04)
  app_key      INT  NOT NULL REFERENCES dw.fact_app,
  category_key INT  NOT NULL REFERENCES dw.dim_category,
  sentiment    TEXT,
  polarity     NUMERIC,
  subjectivity NUMERIC
);

CREATE INDEX ix_fact_app_category   ON dw.fact_app (category_key);
CREATE INDEX ix_fact_review_app     ON dw.fact_review (app_key);
CREATE INDEX ix_fact_review_category ON dw.fact_review (category_key);
