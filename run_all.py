"""B6: chạy toàn bộ pipeline từ đầu.
    python run_all.py                  # chạy thật (cần dữ liệu trong data/raw + nb02 của A)
    python run_all.py --sample         # dữ liệu GIẢ để thử hạ tầng khi A chưa xong (bỏ qua kiểm tải + nb02)
    python run_all.py --no-notebooks   # chỉ chạy phần SQL/Python hạ tầng
Thứ tự: kiểm file -> nb02 -> 00 -> 01 -> nạp stg -> 02 -> 03 -> đối chiếu -> 05 -> 04 -> nb03 -> nb05 -> nb04 -> results.json
Lưu ý: 05 chạy MỘT lần, trước nb04 (nb04 ghi mart.review_topic; chạy lại 05 sau đó sẽ xoá bảng này)."""
import argparse
import csv
import re
import subprocess
import sys
from config import (DB_URL, SQL_DIR, NB_DIR, OLAP_DIR,
                    LOW_RATING_THRESHOLD, MIN_STORE_REVIEWS, MIN_CELL_N)
from sqlalchemy import create_engine

PY = sys.executable
ENGINE = create_engine(DB_URL)


def run_sql(fname: str, optional: bool = False):
    p = SQL_DIR / fname
    print(f"\n=== SQL: {fname}")
    raw = ENGINE.raw_connection()          # cursor.execute(sql) không tham số: ký tự % không bị hiểu nhầm
    try:
        cur = raw.cursor()
        cur.execute(p.read_text(encoding="utf-8"))
        raw.commit()
    except Exception as e:
        raw.rollback()
        if optional:
            print(f"   (bỏ qua, không bắt buộc) {str(e).splitlines()[0]}")
        else:
            raise
    finally:
        raw.close()


def sync_params():
    """Ghi ngưỡng từ config.py vào mart.params (nguồn duy nhất cho view và 04)."""
    raw = ENGINE.raw_connection()
    try:
        cur = raw.cursor()
        cur.execute("UPDATE mart.params SET low_rating_threshold = %s, min_store_reviews = %s, min_cell_n = %s",
                    (LOW_RATING_THRESHOLD, MIN_STORE_REVIEWS, MIN_CELL_N))
        raw.commit()
    finally:
        raw.close()


def run_olap():
    """Tách 04-olap-queries.sql theo dòng '-- @query <ten>' và xuất mỗi truy vấn ra outputs/olap/<ten>.csv"""
    text = (SQL_DIR / "04-olap-queries.sql").read_text(encoding="utf-8")
    parts = re.split(r"^-- @query\s+(\S+)\s*$", text, flags=re.M)
    OLAP_DIR.mkdir(parents=True, exist_ok=True)
    for old in OLAP_DIR.glob("*.csv"):
        old.unlink()
    raw = ENGINE.raw_connection()
    try:
        for name, sql in zip(parts[1::2], parts[2::2]):
            cur = raw.cursor()
            cur.execute(sql)
            cols = [d[0] for d in cur.description]
            rows = cur.fetchall()
            with open(OLAP_DIR / f"{name}.csv", "w", encoding="utf-8", newline="") as f:
                w = csv.writer(f)
                w.writerow(cols)
                w.writerows(rows)
            print(f"   {name}: {len(rows)} dòng")
    finally:
        raw.close()


def run_nb(fname: str):
    p = NB_DIR / fname
    print(f"\n=== NOTEBOOK: {fname}")
    if not p.exists():
        print("   (chưa có - bỏ qua)")
        return
    subprocess.run([PY, "-m", "jupyter", "nbconvert", "--to", "notebook", "--execute", "--inplace",
                    "--ExecutePreprocessor.timeout=1800", str(p)], check=True)


def run_py(rel: str):
    print(f"\n=== PY: {rel}")
    subprocess.run([PY, rel], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", action="store_true", help="dùng dữ liệu giả, bỏ qua kiểm tải và nb02")
    ap.add_argument("--no-notebooks", action="store_true", help="không chạy notebook")
    a = ap.parse_args()

    if a.sample:
        run_py("scripts/make_sample_data.py")
    else:
        run_py("scripts/download_data.py")
        if not a.no_notebooks:
            run_nb("nb02_cleaning.ipynb")      # A: xuất data/processed/*_all_rows.csv

    run_sql("00-init-roles.sql", optional=True)   # cần quyền tạo role; Docker (user dm là superuser) thì chạy được
    run_sql("01-staging.sql")
    run_py("scripts/load_staging.py")
    run_sql("02-star-schema.sql")
    run_sql("03-transform.sql")
    run_py("scripts/reconcile.py")
    run_sql("05-mart-views.sql")
    sync_params()
    print("\n=== OLAP: 04-olap-queries.sql")
    run_olap()

    if not a.no_notebooks:
        run_nb("nb03_main_analysis.ipynb")     # C
        run_nb("nb05_robustness.ipynb")        # C
        run_nb("nb04_text_mining.ipynb")       # D: TRUNCATE + ghi mart.review_topic
    run_py("scripts/build_results.py")
    print("\nXONG.")


if __name__ == "__main__":
    main()
