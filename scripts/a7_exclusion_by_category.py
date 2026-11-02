"""A7 - So lieu dao duc: ai/cai gi bi loai, theo danh muc.

Dat file nay vao scripts/ cua repo, roi tu thu muc goc repo chay:  python scripts/a7_exclusion_by_category.py
Doc:   data/processed/app_all_rows.csv va review_all_rows.csv
Ra:    outputs/a7/ (4 file: a7_app_by_category.csv, a7_review_coverage_by_category.csv,
       a7_unmatched_names.csv, a7_results.json)
Chi doc 2 file CSV cua nb02. Khong ghi vao DB.
"""
import argparse, json, sys, unicodedata
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent  # thu muc goc repo (file nam trong scripts/)
MIN_CELL_N = 30  # khop config.py (min_cell_n)

# --- Ten cot co the co (viet thuong). Sua o day neu script bao khong tim thay ---
APP_CANDS = {
    "category": ["category", "category_clean"],
    "name": ["app_name_norm", "name_norm", "app_norm", "app", "app_name"],
    "rating": ["rating"],
}
REV_CANDS = {
    "name": ["app_name_norm", "name_norm", "app_norm", "app", "app_name"],
    "category": ["category", "category_clean"],
    "sentiment": ["sentiment"],
}


def pick(df, cands, what, required=True):
    low = {c.lower(): c for c in df.columns}
    for c in cands:
        if c in low:
            return low[c]
    if required:
        raise SystemExit(f"Khong tim thay cot '{what}'. Cot hien co: {list(df.columns)}\n"
                         f"-> them ten dung vao APP_CANDS/REV_CANDS o dau file.")
    return None


def as_bool(s):
    return s.astype(str).str.strip().str.lower().eq("true")


def has_non_latin(name):
    for ch in str(name):
        if ch.isalpha() and not unicodedata.name(ch, "").startswith("LATIN"):
            return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--app", default=str(ROOT / "data/processed/app_all_rows.csv"))
    ap.add_argument("--review", default=str(ROOT / "data/processed/review_all_rows.csv"))
    ap.add_argument("--out", default=str(ROOT / "outputs/a7"))
    a = ap.parse_args()
    for f in (a.app, a.review):
        if not Path(f).exists():
            sys.exit(f"Khong thay file: {f}\n-> chay nb02 de sinh file (CSV khong commit), roi chay lai.")
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)

    # contract: o trong = NULL. Khong de pandas doi "NA"/"None"/"null" thanh NaN (ten app, review co the la chu that)
    rd = dict(keep_default_na=False, na_values=[""])
    app = pd.read_csv(a.app, **rd)
    rev = pd.read_csv(a.review, **rd)
    print("Cot app   :", list(app.columns))
    print("Cot review:", list(rev.columns))

    # ---------- APP ----------
    a_cat = pick(app, APP_CANDS["category"], "app.category")
    a_name = pick(app, APP_CANDS["name"], "app.name")
    a_rat = pick(app, APP_CANDS["rating"], "app.rating")
    app["_kept"] = as_bool(app["kept"])
    app["_reason"] = app["drop_reason"].fillna("").astype(str)
    # dong lech cot co Category rac ("1.9") -> gom ve 1 nhan rieng
    app["_cat"] = np.where(app["_reason"].eq("misaligned"), "(lech cot)", app[a_cat].astype(str))
    app["_rating_missing"] = pd.to_numeric(app[a_rat], errors="coerce").isna()

    g = app.groupby("_cat")
    t1 = pd.DataFrame({
        "n_raw_rows": g.size(),
        "n_exact_dup": g["_reason"].apply(lambda s: (s == "exact_dup").sum()),
        "n_name_dup": g["_reason"].apply(lambda s: (s == "name_dup").sum()),
        "n_kept": g["_kept"].sum(),
    })
    kept = app[app["_kept"]]
    t1["n_kept_rating_missing"] = kept.groupby("_cat")["_rating_missing"].sum()
    t1 = t1.fillna(0).astype(int)
    t1["pct_dropped_of_raw"] = (1 - t1["n_kept"] / t1["n_raw_rows"]).round(4)
    t1["pct_rating_missing_of_kept"] = (t1["n_kept_rating_missing"] / t1["n_kept"].replace(0, np.nan)).round(4)
    t1["cell_ok_min_n"] = t1["n_kept"] >= MIN_CELL_N
    t1.index.name = "category"
    t1.sort_values("n_kept", ascending=False).to_csv(out / "a7_app_by_category.csv")

    # ---------- REVIEW ----------
    r_name = pick(rev, REV_CANDS["name"], "review.name")
    r_cat = pick(rev, REV_CANDS["category"], "review.category", required=False)
    r_sent = pick(rev, REV_CANDS["sentiment"], "review.sentiment")
    rev["_kept"] = as_bool(rev["kept"])
    rev["_reason"] = rev["drop_reason"].fillna("").astype(str)

    # a) tong quan ly do loai
    reason_counts = rev["_reason"].replace("", "kept").value_counts()
    n_raw_rev = len(rev)
    n_after_exact = int((rev["_reason"] != "exact_dup").sum())

    # b) nhom khong khop: khong co danh muc -> dac trung bang ten.
    # Do thu tu uu tien drop_reason (no_text > no_app_match), review TRONG cua ten khong khop
    # mang nhan 'no_text'. Nen dinh nghia theo TEN (khong co trong bang app giu lai), khong theo nhan.
    nd = rev[rev["_reason"] != "exact_dup"]
    un = nd[~nd[r_name].isin(set(kept[a_name]))]
    n_un_labelled = int((rev["_reason"] == "no_app_match").sum())
    un_names = (un.groupby(r_name).agg(n_reviews=("_reason", "size"),
                                        n_no_text=("_reason", lambda s: int((s == "no_text").sum())))
                  .reset_index().sort_values("n_reviews", ascending=False))
    un_names["non_latin"] = un_names[r_name].map(has_non_latin)
    un_names.to_csv(out / "a7_unmatched_names.csv", index=False)

    # c) do phu review theo danh muc (gan danh muc qua ten chuan hoa)
    rk = rev[rev["_kept"]].copy()
    if r_cat is None:
        name2cat = kept.drop_duplicates(a_name).set_index(a_name)[a_cat]
        rk["_cat"] = rk[r_name].map(name2cat)
    else:
        rk["_cat"] = rk[r_cat]
    n_unassigned = int(rk["_cat"].isna().sum())
    rk = rk.dropna(subset=["_cat"])
    rk["_neg"] = rk[r_sent].astype(str).str.lower().eq("negative")

    names_with_text = rk.groupby("_cat")[r_name].nunique()
    t2 = pd.DataFrame({
        "n_kept_apps": kept.groupby(a_cat).size(),
        "n_apps_with_text": names_with_text,
        "n_kept_reviews": rk.groupby("_cat").size(),
        "n_negative_reviews": rk.groupby("_cat")["_neg"].sum(),
    }).fillna(0).astype(int)
    t2["pct_apps_with_text"] = (t2["n_apps_with_text"] / t2["n_kept_apps"].replace(0, np.nan)).round(4)
    t2["share_of_apps"] = (t2["n_kept_apps"] / t2["n_kept_apps"].sum()).round(4)
    t2["share_of_reviews"] = (t2["n_kept_reviews"] / t2["n_kept_reviews"].sum()).round(4)
    t2["representation_index"] = (t2["share_of_reviews"] / t2["share_of_apps"].replace(0, np.nan)).round(2)
    t2["neg_cell_ok_min_n"] = t2["n_negative_reviews"] >= MIN_CELL_N
    t2.index.name = "category"
    t2.sort_values("n_kept_apps", ascending=False).to_csv(out / "a7_review_coverage_by_category.csv")

    # ---------- results ----------
    res = {
        "app": {"n_raw": len(app), "n_kept": int(app["_kept"].sum()),
                "drop_reason_counts": app["_reason"].replace("", "kept").value_counts().to_dict(),
                "rating_missing_of_kept": int(kept["_rating_missing"].sum())},
        "review": {"n_raw": n_raw_rev, "n_after_exact_dup": n_after_exact,
                   "n_kept": int(rev["_kept"].sum()),
                   "drop_reason_counts": reason_counts.to_dict(),
                   "kept_reviews_without_category": n_unassigned},
        "unmatched": {
            "n_reviews": int(len(un)), "n_reviews_labelled_no_app_match": n_un_labelled,
            "n_names": int(len(un_names)),
            "pct_of_non_exact_dup_reviews": round(len(un) / n_after_exact, 4),
            "n_names_non_latin": int(un_names["non_latin"].sum()),
            "pct_names_non_latin": round(float(un_names["non_latin"].mean()), 4) if len(un_names) else None,
            "n_reviews_non_latin_names": int(un_names.loc[un_names["non_latin"], "n_reviews"].sum()),
        },
        "coverage": {
            "n_apps_with_text": int(names_with_text.sum()),
            "pct_apps_with_text": round(float(names_with_text.sum() / len(kept)), 4),
            "categories_below_min_cell_n_apps": int((~t1.loc[t1.index != "(lech cot)", "cell_ok_min_n"]).sum()),
            "categories_neg_below_min_cell_n": int((~t2["neg_cell_ok_min_n"]).sum()),
        },
        "min_cell_n": MIN_CELL_N,
    }

    # ---------- doi chieu voi decision_log (30/10/2026) ----------
    expected = {
        "app n_raw (log #1)": (len(app), 10841),
        "app misaligned (log #1)": (int((app["_reason"] == "misaligned").sum()), 1),
        "app exact_dup (log #2)": (int((app["_reason"] == "exact_dup").sum()), 483),
        "app name_dup (log #3)": (int((app["_reason"] == "name_dup").sum()), 719),
        "app kept (log #3)": (int(app["_kept"].sum()), 9638),
        "app rating thieu / kept (log #4)": (int(kept["_rating_missing"].sum()), 1458),
        "review n_raw (log #7)": (n_raw_rev, 64295),
        "review exact_dup (log #7)": (int((rev["_reason"] == "exact_dup").sum()), 33616),
        "review no_text (log #9)": (int((rev["_reason"] == "no_text").sum()), 987),
        "review no_app_match (log #10)": (n_un_labelled, 1442),
        "review kept (log #9)": (int(rev["_kept"].sum()), 28250),
        "ten khong khop (log #10)": (int(len(un_names)), 54),
    }
    print("\n=== Doi chieu decision_log ===")
    for k, (got, exp) in expected.items():
        print(f"{'OK   ' if got == exp else 'LECH '} {k}: do duoc {got:,} | log {exp:,}")
    res["check_vs_decision_log"] = {k: {"got": g, "log": e, "match": g == e} for k, (g, e) in expected.items()}
    (out / "a7_results.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=2))
    print(f"\nDa ghi 4 file vao {out.resolve()}")


if __name__ == "__main__":
    main()
