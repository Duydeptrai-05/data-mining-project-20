"""A10: vẽ hình cho Chương 2 (Dữ liệu và báo cáo chất lượng dữ liệu).

Đọc CSV đã có trong outputs/ (không cần dữ liệu thô, không cần PostgreSQL),
ghi PNG vào docs/report/. Không có phần ngẫu nhiên.

Chạy từ thư mục gốc repo:
    python scripts/a_make_figures.py

Chốt chặn: tổng số app và số app thiếu Rating phải khớp số đã chốt
(9 638 / 1 458). Lệch thì dừng, không sửa số cho khớp.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "report"
OUT.mkdir(parents=True, exist_ok=True)

N_APPS, N_MISSING = 9638, 1458  # decision log / results.json

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11})


def pct(x):  # 64.3 -> "64,3"
    return f"{x:.1f}".replace(".", ",")


def th(n):  # 1147 -> "1 147"
    return f"{n:,}".replace(",", " ")


# ---------- Hình 2.1: thiếu Rating theo nhóm lượt cài ----------
d = pd.read_csv(ROOT / "outputs" / "a5" / "missing_rating_by_installs.csv")
assert d["n_apps"].sum() == N_APPS, d["n_apps"].sum()
assert d["n_missing"].sum() == N_MISSING, d["n_missing"].sum()

fig, ax = plt.subplots(figsize=(7.5, 4.2))
bars = ax.bar(d["install_band"], d["pct_missing_in_band"], color="#3b6ea5")
for b, p, k, n in zip(bars, d["pct_missing_in_band"], d["n_missing"], d["n_apps"]):
    ax.text(b.get_x() + b.get_width() / 2, p + 1,
            f"{pct(p)}%\n({th(k)}/{th(n)})", ha="center", va="bottom", fontsize=9)
ax.set_ylim(0, 80)
ax.set_ylabel("% ứng dụng thiếu Rating")
ax.set_xlabel("Nhóm lượt cài đặt (tăng dần)")
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig(OUT / "hinh_2_1_thieu_rating_theo_luot_cai.png", dpi=200)
plt.close()

# ---------- Hình 2.2: thiếu Rating theo danh mục ----------
c = pd.read_csv(ROOT / "outputs" / "a7" / "a7_app_by_category.csv")
assert c["n_kept"].sum() == N_APPS, c["n_kept"].sum()
assert c["n_kept_rating_missing"].sum() == N_MISSING, c["n_kept_rating_missing"].sum()
c = c[c["n_kept"] > 0].sort_values("pct_rating_missing_of_kept")  # bỏ dòng "(lech cot)", n = 0
assert len(c) == 33  # 33 danh mục (khớp reconcile)

overall = N_MISSING / N_APPS * 100
vals = c["pct_rating_missing_of_kept"] * 100
colors = ["#c0504d" if v > 25 else "#3b6ea5" for v in vals]

fig, ax = plt.subplots(figsize=(7.5, 8))
ax.barh(c["category"], vals, color=colors)
ax.axvline(overall, color="k", ls="--", lw=1)
ax.text(overall + 0.5, 0.2, f"Chung {pct(overall)}%", fontsize=9)
for y, (p, n) in enumerate(zip(vals, c["n_kept"])):
    ax.text(p + 0.4, y, f"{pct(p)}% (n={th(n)})", va="center", fontsize=7.5,
            bbox=dict(fc="white", ec="none", pad=0.5))
ax.set_xlabel("% ứng dụng thiếu Rating trong danh mục")
ax.set_xlim(0, 50)
ax.tick_params(axis="y", labelsize=8)
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig(OUT / "hinh_2_2_thieu_rating_theo_danh_muc.png", dpi=200)
plt.close()

print(f"OK. Đã ghi 2 hình vào {OUT}")
