"""Nạp CSV của nb02 vào schema stg (sau khi chạy sql/01-staging.sql).
Dùng COPY của psycopg2 (không cần cài psql). Map cột theo TÊN trong dòng header của CSV,
nên thứ tự cột trong CSV không cần giống thứ tự cột của bảng."""
import csv
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sqlalchemy import create_engine
from config import DB_URL, APP_ALL_ROWS, REVIEW_ALL_ROWS


def copy_csv(conn, table: str, csv_path: Path):
    if not csv_path.exists():
        raise FileNotFoundError(f"Thiếu {csv_path} (chạy nb02 trước, hoặc python run_all.py --sample)")
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        header = next(csv.reader(f))
        f.seek(0)
        cols = ", ".join(header)
        cur = conn.cursor()
        cur.execute(f"TRUNCATE {table}")
        cur.copy_expert(f"COPY {table} ({cols}) FROM STDIN WITH (FORMAT csv, HEADER true)", f)
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
