# ERD star schema (schema `dw`)

## Grain

- **fact_app**: mỗi dòng là một ứng dụng sau khi đã khử trùng (`app_name_norm` là duy nhất).
- **fact_review**: mỗi dòng là một review có văn bản, sau khi đã khử trùng và nối được với đúng một ứng dụng (`src_row_id` là duy nhất).

## Sơ đồ

```mermaid
erDiagram
  dim_category ||--o{ fact_app : "category_key"
  dim_content_rating ||--o{ fact_app : "content_key"
  dim_price ||--o{ fact_app : "price_key"
  dim_size ||--o{ fact_app : "size_key"
  dim_install ||--o{ fact_app : "install_key"
  dim_date ||--o{ fact_app : "update_key"
  fact_app ||--o{ fact_review : "app_key"
  dim_category ||--o{ fact_review : "category_key"
  dim_category {
    int category_key PK
    text category
    text genre_primary
  }
  dim_content_rating {
    int content_key PK
    text content_rating
  }
  dim_price {
    int price_key PK
    text price_type
    text price_band
    int band_order
  }
  dim_size {
    int size_key PK
    text size_band
    int band_order
  }
  dim_install {
    int install_key PK
    text install_band
    int band_order
  }
  dim_date {
    int update_key PK
    date full_date
    int year
    int month
    int quarter
    int age_days
    text age_band
    int age_order
  }
  fact_app {
    int app_key PK
    int src_row_id
    text app_name
    text app_name_norm
    int category_key FK
    int content_key FK
    int price_key FK
    int size_key FK
    int install_key FK
    int update_key FK
    numeric rating
    bigint store_reviews
    numeric size_mb
    numeric price
  }
  fact_review {
    int review_id PK
    int src_row_id
    int app_key FK
    int category_key FK
    text sentiment
    numeric polarity
    numeric subjectivity
  }
```

## Ghi chú

- `dim_category` là conformed dimension, dùng chung cho cả hai fact (phục vụ truy vấn drill-across).
- `dim_date` là ngày cập nhật bản của app (Last Updated), không phải ngày của review.
- `store_reviews` (lượt đánh giá trên store) khác với số dòng trong `fact_review`.
- Dòng Unknown (khóa -1) do `03-transform.sql` chèn vào các dimension.
- Chủ đề phàn nàn nằm ở `mart.review_topic`, không nằm trong `dw`.
