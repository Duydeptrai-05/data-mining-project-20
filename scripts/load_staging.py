"""Nạp CSV của nb02 vào schema stg (sau khi chạy sql/01-staging.sql).
Dùng COPY của psycopg2 (không cần cài psql). Map cột theo TÊN trong dòng header của CSV,
nên thứ tự cột trong CSV không cần giống thứ tự cột của bảng."""
import csv
import io
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
from sqlalchemy import create_engine
from config import DB_URL, APP_ALL_ROWS, REVIEW_ALL_ROWS


INT_COLS = ("src_row_id", "store_reviews", "installs_min")   # cột số nguyên: pandas hay ghi "159.0"


def copy_csv(conn, table: str, csv_path: Path):
    if not csv_path.exists():
        raise FileNotFoundError(f"Thiếu {csv_path} (chạy nb02 trước, hoặc python run_all.py --sample)")
    # Đọc toàn bộ dạng chuỗi để không đổi giá trị, chỉ bỏ đuôi ".0" ở cột số nguyên
    df = pd.read_csv(csv_path, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    for c in INT_COLS:
        if c in df.columns:
            df[c] = df[c].str.replace(r"\.0$", "", regex=True)
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    buf.seek(0)
    cols = ", ".join(df.columns)
    cur = conn.cursor()
    cur.execute(f"TRUNCATE {table}")
    cur.copy_expert(f"COPY {table} ({cols}) FROM STDIN WITH (FORMAT csv, HEADER true)", buf)
    conn.commit()
    cur.execute(f"SELECT COUNT(*) FROM {table}")
    print(f"{table}: {cur.fetchone()[0]} dòng")


if __name__ == "__main__":
    raw = create_engine(DB_URL).raw_connection()
    try:
        copy_csv(raw, "stg.app_all_rows", APP_ALL_ROWS)
        copy_csv(raw, "stg.review_all_rows", REVIEW_ALL_ROWS)
    finally:
        raw.close()
