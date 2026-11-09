"""A5, việc 3: app thiếu Rating (decision_log dòng 4: không điền, loại khỏi phân tích điểm) có phân bố lượt cài khác app có Rating không?

Nếu khác, thì "thiếu Rating" không ngẫu nhiên, và kết luận chỉ đúng cho app ĐÃ CÓ điểm (không suy rộng cho mọi app).

Chạy từ gốc repo:  python scripts/a5_missing_rating.py
Đọc:  data/processed/app_all_rows.csv     Ghi:  outputs/a5/missing_rating_by_installs.csv
Band lượt cài lấy y nguyên sql/03-transform.sql (dim_install). Chỉ xét dòng kept (9 638 app). Không đụng PostgreSQL.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from config import MIN_STORE_REVIEWS  # noqa: E402

GATE_KEPT, GATE_MISSING = 9638, 1458     # decision log / PROGRESS_A: số giữ và số thiếu Rating sau khử trùng
OUT = ROOT / "outputs" / "a5"
OUT.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(ROOT / "data" / "processed" / "app_all_rows.csv", dtype=str, keep_default_na=False)
df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
df["store_reviews"] = pd.to_numeric(df["store_reviews"], errors="coerce")
df["installs_min"] = pd.to_numeric(df["installs_min"], errors="coerce")

k = df[df["drop_reason"] == ""].copy()
k["rating_missing"] = k["rating"].isna()
print(f"chốt chặn: kept = {len(k)} (cần {GATE_KEPT}) | thiếu Rating = {int(k['rating_missing'].sum())} (cần {GATE_MISSING})")
if (len(k), int(k["rating_missing"].sum())) != (GATE_KEPT, GATE_MISSING):
    sys.exit("DỪNG: không khớp số đã chốt. Đừng sửa số cho khớp; kiểm tra tên giá trị drop_reason.")

BANDS = [(1_000, "<1K"), (10_000, "1K-10K"), (100_000, "10K-100K"), (1_000_000, "100K-1M"), (10_000_000, "1M-10M")]


def band(v):
    if pd.isna(v):
        return "Unknown"
    for lim, lab in BANDS:
        if v < lim:
            return lab
    return "10M+"


ORDER = ["<1K", "1K-10K", "10K-100K", "100K-1M", "1M-10M", "10M+", "Unknown"]
k["install_band"] = k["installs_min"].map(band)

t = k.groupby("install_band")["rating_missing"].agg(n_apps="size", n_missing="sum").reindex(ORDER).dropna()
t["n_has_rating"] = t["n_apps"] - t["n_missing"]
t["pct_missing_in_band"] = 100 * t["n_missing"] / t["n_apps"]                 # trong band này, bao nhiêu % app thiếu Rating
t["share_of_missing_pct"] = 100 * t["n_missing"] / t["n_missing"].sum()       # nhóm thiếu Rating phân bố theo band
t["share_of_has_rating_pct"] = 100 * t["n_has_rating"] / t["n_has_rating"].sum()  # nhóm có Rating phân bố theo band
t = t.astype({"n_apps": int, "n_missing": int, "n_has_rating": int})
t.reset_index().to_csv(OUT / "missing_rating_by_installs.csv", index=False)

print("\n--- thiếu Rating theo band lượt cài ---")
print(t.round(1).to_string())

chi2, p, dof, _ = chi2_contingency(t[["n_missing", "n_has_rating"]].values)
print(f"\nkiểm định chi-bình phương (thiếu Rating độc lập với band?): chi2 = {chi2:.1f}, dof = {dof}, p = {p:.3g}")

med = k.groupby("rating_missing")["installs_min"].median()
print(f"trung vị lượt cài (cận dưới): có Rating = {med[False]:,.0f} | thiếu Rating = {med[True]:,.0f}")

# app đủ điều kiện về số lượt đánh giá trên store: bao nhiêu bị loại chỉ vì thiếu Rating?
big = k[k["store_reviews"] >= MIN_STORE_REVIEWS]
print(f"\napp có store_reviews >= {MIN_STORE_REVIEWS}: {len(big)}, trong đó thiếu Rating: {int(big['rating_missing'].sum())}")

print("\nĐã ghi:", OUT / "missing_rating_by_installs.csv")

# --- ghi số cho báo cáo (results.json lấy từ đây qua build_results.py) ---
from dmutils import save_result  # noqa: E402

save_result("a5_missing_rating", {
    "n_kept": len(k), "n_missing_rating": int(k["rating_missing"].sum()),
    "chi2": float(chi2), "dof": int(dof), "p_value": float(p),
    "median_installs_has_rating": float(med[False]), "median_installs_missing_rating": float(med[True]),
    "min_store_reviews": MIN_STORE_REVIEWS,
    "n_apps_ge_min_store_reviews": int(len(big)),
    "n_missing_among_ge_min_store_reviews": int(big["rating_missing"].sum()),
    "by_install_band": t.reset_index().to_dict("records"),
})
