# Đồ án 20: Phân tích đánh giá ứng dụng di động (Google Play)
Học phần Khai phá dữ liệu | Họ bài toán chính: Mô tả / OLAP | Thuần on-premise (không cloud)

**Câu hỏi:** Với một nhà phát hành ứng dụng, những danh mục và đặc điểm nào (giá, dung lượng, lượt cài, độ mới của bản cập nhật) đi cùng tỉ lệ app điểm thấp cao nhất, và người dùng phàn nàn về chủ đề gì nhiều nhất trong từng danh mục?

Thành viên và phân công: `docs/team_roles.md`, `docs/phan_cong_do_an_20_v3.md`. Hợp đồng giữa các gói: `docs/contracts.md`.

## Cấu trúc repo
```
config.py            tham số + chuỗi kết nối (đọc từ .env)
dmutils.py           save_result(): notebook ghi số liệu cho báo cáo
run_all.py           chạy toàn bộ pipeline từ đầu
scripts/             download_data, load_staging, reconcile, build_results, make_sample_data
notebooks/           nb01..nb05 (đánh số theo thứ tự chạy)
sql/                 00-init-roles, 01-staging, 02-star-schema, 03-transform, 04-olap-queries, 05-mart-views
data/raw|processed/  dữ liệu (KHÔNG commit)
outputs/             results.json, olap/ (CSV), labeling/ (id nhãn tay)
docs/                decision_log, data_quality_report, ethics, schema_notes, contracts, erd/, report/
ai_usage/            khai báo dùng AI của từng thành viên
dashboard/           file export Superset + ảnh chụp
```

## Cài đặt (máy sạch)
**1. PostgreSQL (cách dễ nhất: Docker)**
```bash
docker run --name dm-pg -e POSTGRES_USER=dm -e POSTGRES_PASSWORD=dm -e POSTGRES_DB=dm_course \
  -p 5432:5432 -d postgres:16
```
Không dùng Docker: cài PostgreSQL, rồi tạo database `dm_course` (encoding UTF8) và user `dm` / mật khẩu `dm`
(user cần quyền tạo role để chạy `00-init-roles.sql`; nếu không có thì bước đó tự bỏ qua, nhờ người có quyền chạy một lần).

**2. Python**
```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # Windows: copy .env.example .env
python -c "import nltk; [nltk.download(p) for p in ('punkt','punkt_tab','stopwords')]"
```
**3. Dữ liệu:** tải 2 file CSV từ trang Kaggle vào `data/raw/` (xem `scripts/download_data.py`).

## Chạy
```bash
python run_all.py                  # chạy thật
python run_all.py --sample         # thử hạ tầng bằng dữ liệu GIẢ (khi nb02 của A chưa xong)
python run_all.py --no-notebooks   # chỉ phần SQL/Python hạ tầng
```
Chạy hai lần phải ra cùng số. Mọi số trong báo cáo lấy từ `outputs/results.json`.
Khi rút mạng: chỉ bước tải dữ liệu ban đầu và `nltk.download` cần Internet, phần còn lại chạy offline.

## Superset
Kết nối bằng role chỉ đọc `superset_ro` (mật khẩu `superset_ro`), chỉ thấy schema `mart`. Không đưa review thô lên dashboard.

## Tiến độ theo cổng
G0 tuần 6 · G1 tuần 8 · G2 tuần 11 · G3 ~tuần 13 · G4 tuần 15
