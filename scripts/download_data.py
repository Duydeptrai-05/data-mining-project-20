"""A1: tải dữ liệu + kiểm SHA-256. Dữ liệu KHÔNG được commit vào repo.

Nguồn: Kaggle - Google Play Store Apps. Hai file cần có trong data/raw/:
  googleplaystore.csv                (10 841 x 13)
  googleplaystore_user_reviews.csv   (64 295 x 5)
"""
import hashlib, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import RAW_DIR

EXPECTED_SHA256 = {
    "googleplaystore.csv": "TODO_A_ĐIỀN_SAU_KHI_TẢI",
    "googleplaystore_user_reviews.csv": "TODO_A_ĐIỀN_SAU_KHI_TẢI",
}

def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def check() -> bool:
    ok = True
    for name, expected in EXPECTED_SHA256.items():
        p = RAW_DIR / name
        if not p.exists():
            print(f"[THIẾU] {p}  -> tải thủ công từ trang Kaggle vào data/raw/")
            ok = False
            continue
        got = sha256(p)
        status = "OK" if got == expected else "KHÁC/CHƯA GHI"
        print(f"[{status}] {name}: {got}")
        ok &= (got == expected)
    return ok

if __name__ == "__main__":
    sys.exit(0 if check() else 1)
