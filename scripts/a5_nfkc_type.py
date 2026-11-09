"""A5, việc 4: hai quyết định nhỏ có làm đổi kết luận cuối không?
  (a) chuẩn hoá tên NFKC + strip + casefold (decision_log dòng 8): gộp 17 tên (21 dòng)
  (b) gán Type theo Price (dòng 12): chỉ 1 dòng

Cách đo (cùng tập ứng viên 10 357 dòng như a5_name_dup.py):
  N0 = bản chính: khoá tên = app_name_norm (NFKC + strip + casefold)
  N1 = không chuẩn hoá mạnh: khoá tên = app_name.strip()  (chỉ cắt khoảng trắng)
  Mỗi cách giữ một dòng mỗi tên theo quy tắc R1 (Reviews lớn nhất -> Last Updated mới nhất -> src_row_id nhỏ nhất).
  (b) kiểm tra dòng Type được gán: có nằm trong tập phân tích không, và Type có được dùng ở đâu không.

Chạy từ gốc repo:  python scripts/a5_nfkc_type.py
Đọc:  data/processed/app_all_rows.csv     Ghi:  outputs/a5/nfkc_rules.csv
Không đụng PostgreSQL. Chốt chặn khớp decision log / nb05; lệch thì DỪNG, không sửa số cho khớp.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from config import LOW_RATING_THRESHOLD, MIN_CELL_N, MIN_STORE_REVIEWS  # noqa: E402

GATE_N, GATE_K = 6709, 183
GATE_POOL, GATE_KEPT = 10357, 9638
OUT = ROOT / "outputs" / "a5"
OUT.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(ROOT / "data" / "processed" / "app_all_rows.csv", dtype=str, keep_default_na=False)
df["src_row_id"] = pd.to_numeric(df["src_row_id"])
df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
df["store_reviews"] = pd.to_numeric(df["store_reviews"], errors="coerce")
df["price"] = pd.to_numeric(df["price"], errors="coerce")
df["category"] = df["category"].replace("", np.nan)
df["last_updated"] = df["last_updated"].replace("", np.nan)

pool = df[df["drop_reason"].isin(["", "name_dup"])].copy()
print(f"chốt chặn 1: tập ứng viên = {len(pool)} (cần {GATE_POOL}) | tên chuẩn hoá duy nhất = {pool['app_name_norm'].nunique()} (cần {GATE_KEPT})")
if len(pool) != GATE_POOL or pool["app_name_norm"].nunique() != GATE_KEPT:
    sys.exit("DỪNG: tập ứng viên không khớp decision log. Đừng sửa số cho khớp.")

BY, ASC = ["name_key", "store_reviews", "last_updated", "src_row_id"], [True, False, False, True]


def choose(key):
    p = pool.assign(name_key=key)
    return p.sort_values(BY, ascending=ASC).drop_duplicates("name_key", keep="first")


def prep(d):
    x = d[d["rating"].notna() & (d["store_reviews"] >= MIN_STORE_REVIEWS)].copy()
    x["is_low"] = x["rating"] <= LOW_RATING_THRESHOLD
    return x


def cat_table(x):
    g = x.groupby("category")["is_low"].agg(n="size", k="sum")
    g["rate_pct"] = 100 * g["k"] / g["n"]
    return g


chosen = {"N0 NFKC+casefold (bản chính)": choose(pool["app_name_norm"]),
          "N1 chỉ strip": choose(pool["app_name"].str.strip())}

main_ids = set(chosen["N0 NFKC+casefold (bản chính)"]["src_row_id"])
if main_ids != set(df.loc[df["drop_reason"] == "", "src_row_id"]):
    sys.exit("DỪNG: N0 không dựng lại đúng tập kept của nb02.")

tables, rows = {}, []
for name, d in chosen.items():
    x = prep(d)
    t = cat_table(x)
    tables[name] = t
    ok = t[t["n"] >= MIN_CELL_N].sort_values("rate_pct", ascending=False)
    rows.append({"rule": name, "n_kept": len(d), "n_analysis": len(x), "k_low": int(x["is_low"].sum()),
                 "rate_pct": 100 * x["is_low"].mean(), "top1": ok.index[0], "top1_rate_pct": ok["rate_pct"].iloc[0],
                 "top2": ok.index[1], "gap_top1_top2_pp": ok["rate_pct"].iloc[0] - ok["rate_pct"].iloc[1],
                 "top5": ", ".join(ok.index[:5])})
res = pd.DataFrame(rows)

r0 = res.iloc[0]
print(f"chốt chặn 2: N0 có {r0.n_analysis} app phân tích, {r0.k_low} điểm thấp (cần {GATE_N} và {GATE_K})")
if (r0.n_analysis, r0.k_low) != (GATE_N, GATE_K):
    sys.exit("DỪNG: không khớp nb05 của C. Đừng sửa số cho khớp.")

ref = tables["N0 NFKC+casefold (bản chính)"]
ref_ok = ref[ref["n"] >= MIN_CELL_N]
for i, name in enumerate(res["rule"]):
    t = tables[name]
    common = ref_ok.index.intersection(t[t["n"] >= MIN_CELL_N].index)
    res.loc[i, "spearman_vs_N0"] = spearmanr(ref_ok.loc[common, "rate_pct"], t.loc[common, "rate_pct"]).statistic
    res.loc[i, "top5_overlap_with_N0"] = len(set(ref_ok["rate_pct"].nlargest(5).index) & set(t.loc[common, "rate_pct"].nlargest(5).index))
res.to_csv(OUT / "nfkc_rules.csv", index=False)

print("\n--- (a) NFKC: so 2 cách khoá tên ---")
show = ["rule", "n_kept", "n_analysis", "k_low", "rate_pct", "top1", "gap_top1_top2_pp", "spearman_vs_N0", "top5_overlap_with_N0"]
print(res[show].round(3).to_string(index=False))
for _, r in res.iterrows():
    print(f"  top-5 {r['rule']}: {r['top5']}")
extra = len(chosen["N1 chỉ strip"]) - len(chosen["N0 NFKC+casefold (bản chính)"])
print(f"N1 giữ thêm {extra} dòng so với bản chính")
n0, n1 = (set(chosen[k]["src_row_id"]) for k in chosen)
added = df[df["src_row_id"].isin(n1 - n0)]
print(f"dòng chỉ có ở N1: {len(added)} | trong đó nằm trong tập phân tích: {len(prep(added))}")

print("\n--- (b) Type gán theo Price ---")
raw = pd.read_csv(ROOT / "data" / "raw" / "googleplaystore.csv", dtype=str, keep_default_na=False)
raw["src_row_id"] = raw.index
miss = raw[(raw["Type"].isin(["", "NaN"])) & (raw["Price"] == "0")]
print("dòng Type thiếu và Price = 0:", len(miss), "| src_row_id:", miss["src_row_id"].tolist())
hit = df[df["src_row_id"].isin(miss["src_row_id"])]
print(hit[["src_row_id", "app_name", "drop_reason", "rating", "store_reviews", "type"]].to_string(index=False))
print("nằm trong tập phân tích (kept, có Rating, >= ngưỡng):", len(prep(hit[hit["drop_reason"] == ""])))
print("Type KHÔNG dùng trong SQL/notebook phân tích (đã grep sql/03, sql/05, nb03, nb05: 0 kết quả) -> Free/Paid lấy từ price.")
print("\nĐã ghi:", OUT / "nfkc_rules.csv")
