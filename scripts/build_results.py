"""B6: gom mọi con số vào outputs/results.json (báo cáo lấy số từ file này, không chép tay).
Gồm: số dòng các bảng dw, tham số, kết quả OLAP (outputs/olap/*.csv), và các phần notebook ghi bằng dmutils.save_result()."""
import json
import subprocess
import sys
from decimal import Decimal
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
from sqlalchemy import create_engine
from config import DB_URL, OLAP_DIR, RESULTS_JSON
from dmutils import PARTS_DIR

TABLES = ["dw.dim_category", "dw.dim_content_rating", "dw.dim_price", "dw.dim_size", "dw.dim_install",
          "dw.dim_date", "dw.fact_app", "dw.fact_review", "mart.review_topic"]


def _default(o):
    if isinstance(o, Decimal):
        return float(o)
    if hasattr(o, "item"):
        return o.item()
    return str(o)


def main():
    res = {"warehouse": {}, "params": {}, "olap": {}, "parts": {}}
    raw = create_engine(DB_URL).raw_connection()
    try:
        cur = raw.cursor()
        for t in TABLES:
            cur.execute(f"SELECT COUNT(*) FROM {t}")
            res["warehouse"][t] = cur.fetchone()[0]
        cur.execute("SELECT low_rating_threshold, min_store_reviews, min_cell_n FROM mart.params")
        a, b, c = cur.fetchone()
        res["params"] = {"low_rating_threshold": float(a), "min_store_reviews": b, "min_cell_n": c}
    finally:
        raw.close()

    for p in sorted(OLAP_DIR.glob("*.csv")):
        df = pd.read_csv(p).astype(object)
        res["olap"][p.stem] = df.where(df.notna(), None).to_dict("records")

    if PARTS_DIR.exists():
        for p in sorted(PARTS_DIR.glob("*.json")):
            res["parts"][p.stem] = json.loads(p.read_text(encoding="utf-8"))

    try:
        res["git_commit"] = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"],
                                                    stderr=subprocess.DEVNULL, text=True).strip()
    except Exception:
        res["git_commit"] = None

    RESULTS_JSON.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_JSON.write_text(json.dumps(res, ensure_ascii=False, indent=2, sort_keys=True, default=_default),
                            encoding="utf-8")
    print(f"Đã ghi {RESULTS_JSON} ({len(res['olap'])} truy vấn OLAP, {len(res['parts'])} phần từ notebook)")


if __name__ == "__main__":
    main()
