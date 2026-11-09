"""A5, việc 2: cách chọn MỘT dòng cho mỗi tên app (decision_log dòng 3) có làm đổi kết luận cuối không?

Bản chính (R1) giữ dòng có Reviews lớn nhất. Script thử thêm 2 cách khác trên CÙNG tập ứng viên
(10 357 dòng = sau khi bỏ dòng lệch cột và dòng trùng hoàn toàn):
  R1: Reviews lớn nhất -> Last Updated mới nhất -> src_row_id nhỏ nhất   (bản chính, y nguyên nb02)
  R2: Last Updated mới nhất -> Reviews lớn nhất -> src_row_id nhỏ nhất
  R3: dòng đầu tiên trong file (src_row_id nhỏ nhất)

Chạy từ gốc repo:  python scripts/a5_name_dup.py
Đọc:  data/processed/app_all_rows.csv     Ghi:  outputs/a5/name_dup_rules.csv, name_dup_category_flips.csv
Định nghĩa phân tích lấy y nguyên nb05 (prep): có Rating, store_reviews >= MIN_STORE_REVIEWS, is_low = Rating <= LOW.
Không đụng PostgreSQL.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from config import LOW_RATING_THRESHOLD, MIN_CELL_N, MIN_STORE_REVIEWS  # noqa: E402

GATE_N, GATE_K = 6709, 183          # nb05: số app phân tích và số app điểm thấp ở bản chính
GATE_POOL, GATE_KEPT = 10357, 9638  # tập ứng viên và số dòng giữ (decision log)
OUT = ROOT / "outputs" / "a5"
OUT.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(ROOT / "data" / "processed" / "app_all_rows.csv", dtype=str, keep_default_na=False)
df["src_row_id"] = pd.to_numeric(df["src_row_id"])
df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
df["store_reviews"] = pd.to_numeric(df["store_reviews"], errors="coerce")
df["category"] = df["category"].replace("", np.nan)
df["last_updated"] = df["last_updated"].replace("", np.nan)   # chuỗi YYYY-MM-DD nên sắp theo chuỗi là đúng thứ tự ngày
print("tham số:", dict(MIN_STORE_REVIEWS=MIN_STORE_REVIEWS, LOW=LOW_RATING_THRESHOLD, MIN_CELL_N=MIN_CELL_N))
print("drop_reason:", df["drop_reason"].replace("", "kept").value_counts().to_dict())

pool = df[df["drop_reason"].isin(["", "name_dup"])].copy()
print(f"\nchốt chặn 1: tập ứng viên = {len(pool)} (cần {GATE_POOL}) | tên duy nhất = {pool['app_name_norm'].nunique()} (cần {GATE_KEPT})")
if len(pool) != GATE_POOL or pool["app_name_norm"].nunique() != GATE_KEPT:
    sys.exit("DỪNG: tập ứng viên không khớp decision log. Đừng sửa số cho khớp; kiểm tra tên giá trị drop_reason ở trên.")

RULES = {
    "R1 Reviews lớn nhất": (["app_name_norm", "store_reviews", "last_updated", "src_row_id"], [True, False, False, True]),
    "R2 Last Updated mới nhất": (["app_name_norm", "last_updated", "store_reviews", "src_row_id"], [True, False, False, True]),
    "R3 dòng đầu file": (["app_name_norm", "src_row_id"], [True, True]),
}


def choose(p, by, asc):
    s = p.sort_values(by, ascending=asc)            # NaN xếp cuối ở cả hai chiều
    return s.drop_duplicates("app_name_norm", keep="first").set_index("app_name_norm")


chosen = {name: choose(pool, by, asc) for name, (by, asc) in RULES.items()}

# chốt chặn 2: R1 phải dựng lại đúng tập "kept" của nb02
r1_ids = set(chosen["R1 Reviews lớn nhất"]["src_row_id"])
kept_ids = set(df.loc[df["drop_reason"] == "", "src_row_id"])
print(f"chốt chặn 2: R1 trùng tập kept của nb02: {r1_ids == kept_ids} ({len(r1_ids)} dòng)")
if r1_ids != kept_ids:
    sys.exit("DỪNG: R1 không dựng lại đúng tập kept của nb02. Đừng sửa số cho khớp.")


def prep(d):
    x = d[d["rating"].notna() & (d["store_reviews"] >= MIN_STORE_REVIEWS)].copy()
    x["is_low"] = x["rating"] <= LOW_RATING_THRESHOLD
    return x


def cat_table(x):
    g = x.groupby("category")["is_low"].agg(n="size", k="sum")
    g["rate_pct"] = 100 * g["k"] / g["n"]
    return g


tables, rows = {}, []
for name, d in chosen.items():
    x = prep(d)
    t = cat_table(x)
    tables[name] = t
    ok = t[t["n"] >= MIN_CELL_N].sort_values("rate_pct", ascending=False)
    rows.append({"rule": name, "n_analysis": len(x), "k_low": int(x["is_low"].sum()),
                 "rate_pct": 100 * x["is_low"].mean(), "top1": ok.index[0], "top1_rate_pct": ok["rate_pct"].iloc[0],
                 "top2": ok.index[1], "top2_rate_pct": ok["rate_pct"].iloc[1],
                 "gap_top1_top2_pp": ok["rate_pct"].iloc[0] - ok["rate_pct"].iloc[1],
                 "top5": ", ".join(ok.index[:5])})
res = pd.DataFrame(rows)

r1 = res.iloc[0]
print(f"chốt chặn 3: R1 có {r1.n_analysis} app phân tích, {r1.k_low} điểm thấp (cần {GATE_N} và {GATE_K})")
if (r1.n_analysis, r1.k_low) != (GATE_N, GATE_K):
    sys.exit("DỪNG: không khớp nb05 của C. Đừng sửa số cho khớp.")

# so từng cách với R1
ref = tables["R1 Reviews lớn nhất"]
ref_ok = ref[ref["n"] >= MIN_CELL_N]
for i, name in enumerate(res["rule"]):
    t = tables[name]
    common = ref_ok.index.intersection(t[t["n"] >= MIN_CELL_N].index)
    res.loc[i, "spearman_vs_R1"] = spearmanr(ref_ok.loc[common, "rate_pct"], t.loc[common, "rate_pct"]).statistic
    res.loc[i, "top5_overlap_with_R1"] = len(set(ref_ok["rate_pct"].nlargest(5).index) & set(t.loc[common, "rate_pct"].nlargest(5).index))
    cur = chosen[name]
    res.loc[i, "rows_differ_from_R1"] = int((cur["src_row_id"] != chosen["R1 Reviews lớn nhất"].reindex(cur.index)["src_row_id"]).sum())
res.to_csv(OUT / "name_dup_rules.csv", index=False)

print("\n--- so sánh 3 cách chọn ---")
show = ["rule", "n_analysis", "k_low", "rate_pct", "top1", "top1_rate_pct", "top2", "gap_top1_top2_pp",
        "spearman_vs_R1", "top5_overlap_with_R1", "rows_differ_from_R1"]
print(res[show].round(3).to_string(index=False))
print("\ntop-5 mỗi cách:")
for _, r in res.iterrows():
    print(f"  {r['rule']}: {r['top5']}")

# --- tên nằm ở nhiều danh mục: chọn dòng nào quyết định app thuộc danh mục nào ---
multi = pool.groupby("app_name_norm")["category"].nunique()
multi = multi[multi > 1].index
print(f"\ntên có dòng ở >1 danh mục: {len(multi)}")
flip = pd.DataFrame({name: chosen[name].loc[multi, "category"] for name in RULES})
r1c = flip.iloc[:, 0]
for c in flip.columns[1:]:
    print(f"  {c}: {int((flip[c] != r1c).sum())} tên đổi danh mục so với R1")
flip.reset_index().to_csv(OUT / "name_dup_category_flips.csv", index=False)

print("\nĐã ghi:", OUT / "name_dup_rules.csv", "và", OUT / "name_dup_category_flips.csv")

# --- ghi số cho báo cáo (results.json lấy từ đây qua build_results.py) ---
from dmutils import save_result  # noqa: E402

_res = res.astype(object)
save_result("a5_name_dup", {
    "n_pool": len(pool), "n_kept": len(chosen["R1 Reviews lớn nhất"]),
    "n_multi_category_names": int(len(multi)),
    "category_flips_vs_R1": {c: int((flip[c] != r1c).sum()) for c in flip.columns[1:]},
    "rules": _res.where(_res.notna(), None).to_dict("records"),
})
