"""Cấu hình dùng chung. Tham số chốt ở G1, KHÔNG đổi sau đó (nếu đổi: ghi decision_log)."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent
RAW_DIR = ROOT / "data" / "raw"
PROC_DIR = ROOT / "data" / "processed"
OUT_DIR = ROOT / "outputs"
OLAP_DIR = OUT_DIR / "olap"
SQL_DIR = ROOT / "sql"
NB_DIR = ROOT / "notebooks"

# Chuỗi kết nối mặc định của môn học; có thể ghi đè bằng biến môi trường
DB_URL = os.getenv("DM_DB_URL", "postgresql://dm:dm@localhost:5432/dm_course")

# Tham số phân tích (C chốt ở G1)
LOW_RATING_THRESHOLD = 3.0   # "điểm thấp" = Rating <= 3.0
MIN_STORE_REVIEWS = 50       # thử thêm 500 ở nb05
MIN_CELL_N = 30              # ô có ít hơn 30 app thì không diễn giải
RANDOM_STATE = 42            # dùng cho random_state / default_rng ở mọi nơi

# Tên file do nb02 (A) xuất ra, dùng làm đầu vào staging
APP_ALL_ROWS = PROC_DIR / "app_all_rows.csv"
REVIEW_ALL_ROWS = PROC_DIR / "review_all_rows.csv"
RESULTS_JSON = OUT_DIR / "results.json"
