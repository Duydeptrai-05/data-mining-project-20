"""A: điều tra các tên review không khớp bảng app (no_app_match), nhóm tên chỉ có chữ Latin.

Chạy từ gốc repo:  python scripts/a_nomatch_latin.py
Đọc:  data/processed/app_all_rows.csv, data/processed/review_all_rows.csv  (do nb02 sinh ra)
Ghi:  outputs/a_nomatch/nomatch_latin_classified.csv  (chỉ tên app + số đếm, KHÔNG có văn bản review)

Phân loại mỗi tên Latin không khớp:
  (a) key lỏng (bỏ dấu, bỏ mọi ký tự không phải chữ/số) TRÙNG với một app đã giữ  -> chuẩn hoá của nb02 bỏ sót
  (b) key lỏng trùng với một dòng app đã bị loại (lech_cot / exact_dup / name_dup)  -> hệ quả khử trùng
  (c) không trùng key lỏng nào                                                   -> giới hạn dữ liệu
Với (c): in thêm ứng viên "gần giống" (chứa nhau / difflib) để NGƯỜI xem. Gần giống chưa chắc là cùng app.
"""
import difflib
import re
import sys
import unicodedata
from pathlib import Path

import pandas as pd

PROC = Path("data/processed")
OUT = Path("outputs/a_nomatch")
OUT.mkdir(parents=True, exist_ok=True)

EXPECT_NOMATCH_NAMES = 54      # số đo ở nb02
EXPECT_NOMATCH_ROWS = 1442     # số dòng drop_reason == no_app_match
EXPECT_NON_LATIN = 9


def loose(s: str) -> str:
    """Bỏ dấu (NFKD), casefold, giữ chữ/số Latin-Unicode, bỏ ký tự còn lại."""
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[\W_]+", "", s.casefold())


def is_latin_only(s: str) -> bool:
    letters = [c for c in s if c.isalpha()]
    return bool(letters) and all(unicodedata.name(c, "").startswith("LATIN") for c in letters)


app = pd.read_csv(PROC / "app_all_rows.csv", dtype=str, keep_default_na=False)
rv = pd.read_csv(PROC / "review_all_rows.csv", dtype=str, keep_default_na=False)

kept_norm = set(app.loc[app["kept"] == "true", "app_name_norm"])

# 1. Tập tên không khớp: tính trên TẤT CẢ dòng review (đúng cách nb02 in ra số 54)
nomatch_names = sorted(set(rv["app_name_norm"]) - kept_norm)
rows_nomatch = int((rv["drop_reason"] == "no_app_match").sum())
print(f"tên không khớp: {len(nomatch_names)} (kỳ vọng {EXPECT_NOMATCH_NAMES})")
print(f"dòng no_app_match: {rows_nomatch} (kỳ vọng {EXPECT_NOMATCH_ROWS})")
if len(nomatch_names) != EXPECT_NOMATCH_NAMES or rows_nomatch != EXPECT_NOMATCH_ROWS:
    sys.exit("DỪNG: số không khớp số đã chốt. Kiểm tra lại file *_all_rows.csv trước khi đi tiếp.")

# 2. Tách Latin / không Latin
latin = [n for n in nomatch_names if is_latin_only(n)]
non_latin = [n for n in nomatch_names if n not in set(latin)]
print(f"Latin: {len(latin)} | không Latin: {len(non_latin)} (kỳ vọng {EXPECT_NON_LATIN})")
if len(non_latin) != EXPECT_NON_LATIN:
    print("[CHÚ Ý] số không-Latin khác 9: kiểm tra định nghĩa 'Latin' (tên chỉ có số/ký hiệu?)")

# 3. Chỉ mục khoá lỏng cho bảng app
app["loose"] = app["app_name"].map(loose)
kept_by_loose = app[app["kept"] == "true"].groupby("loose")["app_name"].first().to_dict()
dropped = app[app["kept"] == "false"]
dropped_by_loose = (dropped.groupby("loose")
                    .apply(lambda g: "; ".join(sorted(set(g["drop_reason"]))))
                    .to_dict())
kept_loose_keys = list(kept_by_loose)

# số dòng review mỗi tên: toàn bộ / dòng no_app_match (đây là số dòng bị loại vì lý do này)
n_all = rv.groupby("app_name_norm").size()
n_nm = rv[rv["drop_reason"] == "no_app_match"].groupby("app_name_norm").size()

rows = []
for n in latin:
    k = loose(n)
    rec = {"name_norm": n, "loose_key": k,
           "n_review_rows_all": int(n_all.get(n, 0)),
           "n_rows_no_app_match": int(n_nm.get(n, 0)),
           "class": "", "matched_app": "", "dropped_reason": "", "near_candidates": ""}
    if k and k in kept_by_loose:
        rec.update({"class": "a", "matched_app": kept_by_loose[k]})
    elif k and k in dropped_by_loose:
        rec.update({"class": "b", "dropped_reason": dropped_by_loose[k]})
    else:
        rec["class"] = "c"
        cont = [kept_by_loose[x] for x in kept_loose_keys
                if len(k) >= 6 and len(x) >= 6 and (k in x or x in k)]
        close = [kept_by_loose[x] for x in difflib.get_close_matches(k, kept_loose_keys, n=3, cutoff=0.85)]
        rec["near_candidates"] = " | ".join(dict.fromkeys(cont[:3] + close))
    rows.append(rec)

res = pd.DataFrame(rows)
res.to_csv(OUT / "nomatch_latin_classified.csv", index=False, encoding="utf-8")

# 4. Tổng kết: ba số phải cộng bằng số tên Latin
cnt = res["class"].value_counts().reindex(["a", "b", "c"], fill_value=0)
print("\n=== TỔNG KẾT ===")
print(f"(a) nb02 bỏ sót chuẩn hoá : {cnt['a']} tên | {res.loc[res['class']=='a','n_rows_no_app_match'].sum()} dòng review bị loại oan")
print(f"(b) bị loại khi khử trùng : {cnt['b']} tên | {res.loc[res['class']=='b','n_rows_no_app_match'].sum()} dòng")
print(f"(c) không có trong bảng app: {cnt['c']} tên | {res.loc[res['class']=='c','n_rows_no_app_match'].sum()} dòng")
assert cnt.sum() == len(latin), "ba số không cộng bằng số tên Latin"
print(f"a+b+c = {cnt.sum()} = {len(latin)} OK")

if cnt["a"]:
    print("\n--- (a): CHI TIẾT (cần sửa nb02) ---")
    print(res.loc[res["class"] == "a", ["name_norm", "matched_app", "n_rows_no_app_match"]].to_string(index=False))
if cnt["b"]:
    print("\n--- (b) ---")
    print(res.loc[res["class"] == "b", ["name_norm", "dropped_reason", "n_rows_no_app_match"]].to_string(index=False))
nc = res[(res["class"] == "c") & (res["near_candidates"] != "")]
if len(nc):
    print("\n--- (c) có ứng viên gần giống: NGƯỜI quyết định, mặc định vẫn là (c) ---")
    print(nc[["name_norm", "near_candidates"]].to_string(index=False))
print("\nĐã ghi:", OUT / "nomatch_latin_classified.csv")
