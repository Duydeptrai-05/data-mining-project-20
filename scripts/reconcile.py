"""B4: đối chiếu kho dữ liệu với nb02 (A). COUNT và AVG(rating) theo danh mục, và tổng số review PHẢI khớp.
Exit code 1 nếu lệch -> run_all dừng. Lệch nghĩa là có lỗi ở nb02 hoặc ở SQL: tìm ra trước khi đi tiếp."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
from sqlalchemy import create_engine
from config import DB_URL, APP_ALL_ROWS, REVIEW_ALL_ROWS


def kept_mask(df):
    return df["kept"].astype(str).str.lower().isin(["true", "t", "1"])


def main() -> int:
    apps = pd.read_csv(APP_ALL_ROWS)
    apps = apps[kept_mask(apps)]
    exp = (apps.groupby("category")
               .agg(n_apps=("category", "size"), n_rated=("rating", "count"), avg_rating=("rating", "mean"))
               .round(4))

    raw = create_engine(DB_URL).raw_connection()
    try:
        cur = raw.cursor()
        cur.execute("""
            SELECT c.category, COUNT(*), COUNT(f.rating), ROUND(AVG(f.rating)::numeric, 4)
            FROM dw.fact_app f JOIN dw.dim_category c USING (category_key)
            GROUP BY c.category""")
        got = pd.DataFrame(cur.fetchall(), columns=["category", "n_apps", "n_rated", "avg_rating"]).set_index("category")
        got["avg_rating"] = got["avg_rating"].astype(float)

        cur.execute("SELECT COUNT(*) FROM dw.fact_review")
        n_rev_db = cur.fetchone()[0]
    finally:
        raw.close()

    revs = pd.read_csv(REVIEW_ALL_ROWS)
    n_rev_csv = int(kept_mask(revs).sum())

    bad = 0
    joined = exp.join(got, how="outer", lsuffix="_nb02", rsuffix="_db")
    for cat, r in joined.iterrows():
        diff = (r["n_apps_nb02"] != r["n_apps_db"] or r["n_rated_nb02"] != r["n_rated_db"]
                or abs((r["avg_rating_nb02"] or 0) - (r["avg_rating_db"] or 0)) > 1e-3)
        if diff:
            bad += 1
            print(f"[LỆCH] {cat}: nb02={r['n_apps_nb02']}/{r['n_rated_nb02']}/{r['avg_rating_nb02']}  "
                  f"db={r['n_apps_db']}/{r['n_rated_db']}/{r['avg_rating_db']}")
    print(f"App: {len(joined)} danh mục, {bad} lệch. Tổng app nb02={int(exp['n_apps'].sum())} db={int(got['n_apps'].sum())}")
    if n_rev_csv != n_rev_db:
        bad += 1
        print(f"[LỆCH] review kept: nb02={n_rev_csv} db={n_rev_db} (kept nhưng không nối được app -> kiểm tra no_app_match)")
    else:
        print(f"Review: nb02={n_rev_csv} db={n_rev_db} khớp")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
