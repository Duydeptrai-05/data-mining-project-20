-- 01-staging.sql | Chủ: B | Idempotent
-- Nạp NGUYÊN các dòng nb02 xuất (kể cả dòng bị loại: kept=false, drop_reason).
-- !! TÊN VÀ KIỂU CỘT DƯỚI ĐÂY LÀ ĐỀ XUẤT - chốt với A trước (đổi tên cột: sửa tài liệu trước, bên nhận xác nhận rồi mới sửa code).
-- Việc nạp CSV do scripts/load_staging.py làm (COPY), file này chỉ tạo bảng.

DROP SCHEMA IF EXISTS stg CASCADE;
CREATE SCHEMA stg;

CREATE TABLE stg.app_all_rows (
  src_row_id     INT,            -- số thứ tự dòng trong file gốc
  app_name       TEXT,
  app_name_norm  TEXT,           -- strip + NFKC + casefold (dùng để nối review)
  category       TEXT,
  genre_primary  TEXT,
  rating         NUMERIC,
  store_reviews  BIGINT,
  size_mb        NUMERIC,
  size_is_varies BOOLEAN,
  installs_min   BIGINT,
  type           TEXT,
  price          NUMERIC,
  content_rating TEXT,
  last_updated   DATE,
  kept           BOOLEAN,
  drop_reason    TEXT            -- misaligned | exact_dup | name_dup | NULL
);

CREATE TABLE stg.review_all_rows (
  src_row_id     INT,
  app_name       TEXT,
  app_name_norm  TEXT,
  review_text    TEXT,
  sentiment      TEXT,
  polarity       NUMERIC,
  subjectivity   NUMERIC,
  kept           BOOLEAN,
  drop_reason    TEXT            -- exact_dup | no_text | no_app_match | NULL
);
