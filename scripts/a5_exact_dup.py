"""A5, việc 1: bỏ dòng trùng hoàn toàn (decision_log dòng 2) có làm đổi danh mục đứng đầu không?

nb05 của C thấy: ở ngưỡng 50, A0 (chưa bỏ dòng trùng) cho top-1 = DATING, A1 (đã bỏ) cho top-1 = LIFESTYLE.
Script này dựng lại đúng bước đó từ CSV (không cần PostgreSQL) và chỉ ra dòng trùng nằm ở danh mục nào.

Chạy từ gốc repo:  python scripts/a5_exact_dup.py
Đọc:  data/processed/app_all_rows.csv      Ghi:  outputs/a5/exact_dup_by_category.csv
Định nghĩa lấy y nguyên nb05 (prep): có Rating, store_reviews >= MIN_STORE_REVIEWS, is_low = Rating <= LOW_RATING_THRESHOLD;
top-1 chỉ xét danh mục n >= MIN_CELL_N.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from config import LOW_RATING_THRESHOLD, MIN_CELL_N, MIN_STORE_REVIEWS  # noqa: E402

GATE_A0, GATE_A1 = 7874, 7416          # số dòng phân tích của nb05 ở ngưỡng 50
OUT = ROOT / "outputs" / "a5"
OUT.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(ROOT / "data" / "processed" / "app_all_rows.csv", dtype=str, keep_default_na=False)
df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
df["store_reviews"] = pd.to_numeric(df["store_reviews"], errors="coerce")
df["category"] = df["category"].replace("", np.nan)
print("tham số:", dict(MIN_STORE_REVIEWS=MIN_STORE_REVIEWS, LOW=LOW_RATING_THRESHOLD, MIN_CELL_N=MIN_CELL_N))
print("giá trị drop_reason:", df["drop_reason"].replace("", "kept").value_counts().to_dict())

A0 = df[df["drop_reason"] != "misaligned"]
A1 = A0[A0["drop_reason"] != "exact_dup"]


def prep(d):
    x = d[d["rating"].notna() & (d["store_reviews"] >= MIN_STORE_REVIEWS)].copy()
    x["is_low"] = x["rating"] <= LOW_RATING_THRESHOLD
    return x


x0, x1 = prep(A0), prep(A1)
print(f"\nchốt chặn: A0 = {len(x0)} (cần {GATE_A0}) | A1 = {len(x1)} (cần {GATE_A1})")
if (len(x0), len(x1)) != (GATE_A0, GATE_A1):
    sys.exit("DỪNG: không khớp số nb05 của C. Đừng sửa số cho khớp; kiểm tra tên giá trị drop_reason ở trên.")


def table(x):
    g = x.groupby("category")["is_low"].agg(n="size", k="sum")
    g["rate_pct"] = 100 * g["k"] / g["n"]
    return g


t0, t1 = table(x0), table(x1)
res = t0.join(t1, how="outer", lsuffix="_A0", rsuffix="_A1").fillna(0)
res["n_dup_removed"] = res["n_A0"] - res["n_A1"]          # dòng trùng nằm trong phân tích
res["k_dup_removed"] = res["k_A0"] - res["k_A1"]          # trong đó là app điểm thấp
res = res.sort_values("rate_pct_A0", ascending=False)
res.reset_index().to_csv(OUT / "exact_dup_by_category.csv", index=False)


def top(t):
    ok = t[t["n"] >= MIN_CELL_N]
    return ok["rate_pct"].idxmax()


top0, top1 = top(t0), top(t1)
print(f"\ntop-1 ở A0 = {top0} | top-1 ở A1 = {top1}")
print(f"dòng trùng nằm trong phân tích: {int(res['n_dup_removed'].sum())} dòng, "
      f"trong đó điểm thấp: {int(res['k_dup_removed'].sum())}")

show = list(dict.fromkeys([top0, top1]))
cols = ["n_A0", "k_A0", "rate_pct_A0", "n_dup_removed", "k_dup_removed", "n_A1", "k_A1", "rate_pct_A1"]
print("\n--- hai danh mục đang tranh top-1 ---")
print(res.loc[show, cols].round(2).to_string())
if len(show) == 2:
    a, b = show
    for tag, key in (("A0", "rate_pct_A0"), ("A1", "rate_pct_A1")):
        print(f"khoảng cách {a} - {b} ở {tag}: {res.loc[a, key] - res.loc[b, key]:+.2f} điểm %")

print("\n--- 6 danh mục đứng đầu ở A0 và A1 (n >= MIN_CELL_N) ---")
for tag, t in (("A0", t0), ("A1", t1)):
    ok = t[t["n"] >= MIN_CELL_N].sort_values("rate_pct", ascending=False).head(6)
    print(tag); print(ok.round(2).to_string())

print("\n--- danh mục có nhiều dòng trùng nhất trong phân tích ---")
print(res.sort_values("n_dup_removed", ascending=False).head(6)[["n_A0", "n_dup_removed", "k_dup_removed"]].to_string())
print("\nĐã ghi:", OUT / "exact_dup_by_category.csv")
