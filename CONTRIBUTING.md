# Quy tắc làm việc nhóm

## Nhánh và PR
- `main` luôn chạy được. KHÔNG push thẳng vào main.
- Mỗi việc một nhánh, tiền tố = ID việc: `a2-nb01`, `b4-transform`, `c5-robustness`, `d7-text-final`.
- PR nhỏ. Người review theo vòng **A → B → C → D → A** và phải **đối chiếu số**, không chỉ đọc code.
- Commit: `B4: nạp fact_app từ stg, khớp COUNT với nb02`.

## Không commit
Dữ liệu thô (`data/raw`, `data/processed`), `.env`, mật khẩu thật. Chỉ commit script tải và script dựng lại.
Không lưu nguyên văn review vào repo (riêng tư): nhãn tay chỉ lưu `review_id`.

## Đổi tên cột / view
Sửa `docs/contracts.md` trước → bên nhận xác nhận → rồi mới sửa code.

## Notebook
Commit bản đã chạy kèm output. Số dùng trong báo cáo phải ghi bằng `dmutils.save_result()` để vào `outputs/results.json`.
Mọi nơi có ngẫu nhiên: `random_state=42` / `default_rng(42)` (lấy từ `config.RANDOM_STATE`).

## Họp 15 phút mỗi cổng (G1 tuần 8, G2 tuần 11, G3 ~tuần 13, G4 tuần 15)
Mỗi người báo giờ làm thực tế; lệch nhiều thì chuyển việc ngay.
