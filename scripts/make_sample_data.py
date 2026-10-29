"""Sinh dữ liệu GIẢ (synthetic) đúng định dạng nb02 sẽ xuất, để B chạy thử toàn pipeline khi A chưa xong.
KHÔNG phải dữ liệu thật: tuyệt đối không dùng cho phân tích hay báo cáo.
Dùng:  python run_all.py --sample"""
import csv
import random
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import PROC_DIR, APP_ALL_ROWS, REVIEW_ALL_ROWS, RANDOM_STATE
 
APP_COLS = ["src_row_id", "app_name", "app_name_norm", "category", "genre_primary", "rating", "store_reviews",
            "size_mb", "size_is_varies", "installs_min", "type", "price", "content_rating", "last_updated",
            "kept", "drop_reason"]
REV_COLS = ["src_row_id", "app_name", "app_name_norm", "review_text", "sentiment", "polarity",
            "subjectivity", "kept", "drop_reason"]
CATS = ["GAME", "FAMILY", "TOOLS", "BUSINESS", "MEDICAL"]
GENRES = {"GAME": ["Action", "Puzzle"], "FAMILY": ["Education", "Entertainment"], "TOOLS": ["Tools"],
          "BUSINESS": ["Business"], "MEDICAL": ["Medical"]}
INSTALLS = [0, 100, 1000, 10000, 100000, 1000000, 10000000]
NEG = ["crashes all the time", "too many ads", "does not work after update", "very slow and laggy"]
POS = ["love it", "works great", "very useful app"]
 
 
def main(n_apps=300, seed=RANDOM_STATE):
    rnd = random.Random(seed)
    PROC_DIR.mkdir(parents=True, exist_ok=True)
    apps, names = [], []
    for i in range(1, n_apps + 1):
        cat = rnd.choice(CATS)
        name = f"SampleApp {i}"
        kept, why = True, ""
        if i % 50 == 0:
            kept, why = False, "exact_dup"
        paid = rnd.random() < 0.1
        rating = "" if rnd.random() < 0.12 else round(rnd.uniform(1.5, 5.0), 1)
        varies = rnd.random() < 0.15
        apps.append([i, name, name.lower(), cat, rnd.choice(GENRES[cat]), rating, rnd.randint(1, 20000),
                     "" if varies else round(rnd.uniform(1, 90), 1), str(varies).lower(),
                     rnd.choice(INSTALLS), "Paid" if paid else "Free",
                     round(rnd.uniform(0.99, 25), 2) if paid else 0, rnd.choice(["Everyone", "Teen", "Mature 17+"]),
                     f"201{rnd.randint(5,8)}-{rnd.randint(1,7):02d}-{rnd.randint(1,28):02d}",
                     str(kept).lower(), why])
        names.append(name)
    dropped_names = {row[1] for row in apps if row[14] == "false"}
    revs = []
    for j in range(1, 1501):
        name = rnd.choice(names + ["Ứng dụng không khớp"])
        neg = rnd.random() < 0.3
        text = rnd.choice(NEG if neg else POS)
        kept, why = True, ""
        if name == "Ứng dụng không khớp" or name in dropped_names:
            kept, why = False, "no_app_match"
        revs.append([j, name, name.lower(), text, "Negative" if neg else "Positive",
                     round(rnd.uniform(-1, 0) if neg else rnd.uniform(0, 1), 3), round(rnd.random(), 3),
                     str(kept).lower(), why])
    for path, cols, rows in [(APP_ALL_ROWS, APP_COLS, apps), (REVIEW_ALL_ROWS, REV_COLS, revs)]:
        with open(path, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(cols)
            w.writerows(rows)
    print(f"[DỮ LIỆU GIẢ] {len(apps)} app, {len(revs)} review -> {PROC_DIR}")
 
 
if __name__ == "__main__":
    main()
 