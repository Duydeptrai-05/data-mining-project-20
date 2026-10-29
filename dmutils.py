"""Tiện ích dùng chung. Notebook (C, D) ghi số liệu cho báo cáo bằng save_result();
scripts/build_results.py gom tất cả vào outputs/results.json. Báo cáo chỉ lấy số từ results.json."""
import json
from decimal import Decimal
from config import OUT_DIR

PARTS_DIR = OUT_DIR / "results_parts"


def _default(o):
    if isinstance(o, Decimal):
        return float(o)
    if hasattr(o, "item"):          # numpy scalar
        return o.item()
    return str(o)


def save_result(name: str, obj) -> None:
    """Ví dụ: save_result("nb03_low_rate_by_category", df.to_dict("records"))"""
    PARTS_DIR.mkdir(parents=True, exist_ok=True)
    path = PARTS_DIR / f"{name}.json"
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True, default=_default),
                    encoding="utf-8")
