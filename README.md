# Đồ án 20: Phân tích đánh giá ứng dụng di động (Google Play)

Học phần Khai phá dữ liệu | Họ bài toán chính: Mô tả / OLAP | Thuần on-premise (không cloud)

**Câu hỏi:** Với một nhà phát hành ứng dụng, những danh mục và đặc điểm nào (giá, dung lượng, lượt cài, độ mới của bản cập nhật) đi cùng tỉ lệ app điểm thấp cao nhất, và người dùng phàn nàn về chủ đề gì nhiều nhất trong từng danh mục?

Thành viên và phân công: `docs/team_roles.md`, `docs/phan_cong_do_an_20_v3.md`. Hợp đồng giữa các gói: `docs/contracts.md`.

## Cấu trúc repo

```
config.py            tham số + chuỗi kết nối (đọc từ .env hoặc biến môi trường DM_DB_URL)
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

Không dùng Docker: cài PostgreSQL, rồi dùng tài khoản `postgres` (trong pgAdmin hoặc psql) tạo user và database:

```sql
CREATE USER dm WITH PASSWORD 'dm' CREATEROLE;
CREATE DATABASE dm_course OWNER dm ENCODING 'UTF8';
```

User `dm` cần quyền tạo role để chạy `00-init-roles.sql`; nếu không có thì bước đó tự bỏ qua, nhờ người có quyền chạy một lần.

**2. Python**

```bash
python -m venv .venv
source .venv/bin/activate          # Windows PowerShell: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -c "import nltk; [nltk.download(p) for p in ('punkt','punkt_tab','stopwords')]"
```

(Windows PowerShell: nếu `Activate.ps1` bị chặn, chạy `Set-ExecutionPolicy -Scope Process Bypass` rồi thử lại.)

**3. Chuỗi kết nối.** Repo không chứa `.env` (bí mật không commit), nên máy mới phải tự cấu hình một trong hai cách:

```bash
cp .env.example .env               # Windows: copy .env.example .env, rồi sửa dòng DM_DB_URL cho đúng mật khẩu
```

hoặc đặt biến môi trường cho cửa sổ terminal hiện tại:

```powershell
$env:DM_DB_URL = "postgresql://dm:MẬT_KHẨU@localhost:5432/dm_course"     # PowerShell
export DM_DB_URL="postgresql://dm:MẬT_KHẨU@localhost:5432/dm_course"     # Linux/macOS
```

Viết liền mật khẩu thật, **không giữ dấu `<` `>`**. Nếu mật khẩu có ký tự đặc biệt (`@ # / : %`) thì URL bị hiểu sai, hãy dùng mật khẩu chỉ gồm chữ và số. Kiểm tra trước khi chạy (dòng in ra phải đúng tên database mong muốn):

```bash
python -c "import config; print(config.DB_URL)"
```

**4. Dữ liệu:** không cần tải tay. `run_all.py` tự gọi `scripts/download_data.py`, script này tải 2 file CSV vào `data/raw/` và kiểm SHA-256 (thấy `[OK]` cho cả hai file là đúng). Nếu file đã có sẵn thì chỉ kiểm SHA-256, không cần Internet.

## Chạy

```bash
python run_all.py                  # chạy thật
python run_all.py --sample         # thử hạ tầng bằng dữ liệu GIẢ (khi nb02 của A chưa xong)
python run_all.py --no-notebooks   # chỉ phần SQL/Python hạ tầng
```

Chạy hai lần phải ra cùng số. Mọi số trong báo cáo lấy từ `outputs/results.json`.
Khi rút mạng: chỉ lần tải dữ liệu đầu tiên và `nltk.download` cần Internet, phần còn lại chạy offline.

**Kết quả đúng** khi chạy xong (thấy `XONG.`):

- `reconcile`: 33 danh mục, 0 lệch; app nb02 = db = 9 638; review nb02 = db = 28 250.
- `04-olap-queries.sql`: 6 truy vấn OLAP (95 / 150 / 21 / 99 / 33 / 33 dòng).
- `outputs/results.json` được ghi lại.

Đã kiểm tra trên máy sạch (Windows, venv mới, database trống) ở cả hai chế độ: có mạng và rút mạng.

## Lỗi thường gặp

| Triệu chứng                                                                                                 | Nguyên nhân và cách xử lý                                                                                                                                                    |
| ----------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `password authentication failed for user "dm"`                                                              | Mật khẩu trong `DM_DB_URL`/`.env` sai, hoặc còn dấu `< >`, hoặc biến chưa được đặt trong cửa sổ terminal này. In lại bằng `python -c "import config; print(config.DB_URL)"`. |
| `database "..." does not exist`                                                                             | Chưa tạo database; xem bước 1.                                                                                                                                               |
| Cảnh báo `RuntimeWarning: Proactor event loop`, `MissingIDFieldWarning`, `Connection reset by peer [10054]` | Cảnh báo của Jupyter trên Windows, không ảnh hưởng kết quả.                                                                                                                  |
| Notebook báo thiếu `stopwords`/`punkt`                                                                      | Chưa chạy lệnh `nltk.download` ở bước 2 (cần Internet một lần).                                                                                                              |

## Lưu ý khi commit

`run_all.py` ghi đè các notebook (thêm output) và ghi lại `outputs/results.json`. Sau khi chạy:

```bash
git restore notebooks/             # bỏ phần output tự sinh của notebook
git add outputs/results.json       # chỉ commit file số liệu nếu có thay đổi
git pull
git push
```

Không dùng `git add .`.

## Superset

Kết nối bằng role chỉ đọc `superset_ro` (mật khẩu `superset_ro`), chỉ thấy schema `mart`. Không đưa review thô lên dashboard.

## Tiến độ theo cổng

G0 tuần 6 · G1 tuần 8 · G2 tuần 11 · G3 ~tuần 13 · G4 tuần 15
