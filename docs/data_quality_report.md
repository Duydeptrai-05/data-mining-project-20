# Báo cáo chất lượng dữ liệu — Đồ án 20 (Google Play Store)

## 1. Nguồn dữ liệu

- Tên bộ dữ liệu: Google Play Store Apps
- Tác giả / tài khoản đăng: lava18 (Kaggle)
- Trang nguồn: https://www.kaggle.com/datasets/lava18/google-play-store-apps
- Ngày tải / ngày đo: 30/10/2026
- Người đo: A

## 2. Giấy phép

> This work is licensed under the Creative Commons Attribution 3.0 Unported License. To view a copy of this license, visit http://creativecommons.org/licenses/by/3.0/.

Nguồn chép: file `license.txt` đi kèm bộ dữ liệu tải về. Mục License trên trang Kaggle khớp với nội dung này (CC BY 3.0 Unported).
Ngày xem trang giấy phép: 30/10/2026

Giấy phép CC BY 3.0 cho phép sao chép, phân phối lại và chỉnh sửa tác phẩm, kể cả khi dùng trong lớp học, với điều kiện ghi công tác giả. Nhóm ghi công bộ dữ liệu trong phần tài liệu tham khảo của báo cáo. Giấy phép này chỉ phản ánh quyền do người đăng bộ dữ liệu cấp, không xác nhận quyền của Google hay của các nhà phát hành app đối với dữ liệu gốc. Nhóm chỉ dùng dữ liệu cục bộ và không đăng lại.

## 3. File và số đo thật

Số dòng × cột do nhóm tự đo bằng `pd.read_csv(...).shape` (chưa khử trùng, chưa loại dòng nào).

| File                               | SHA-256                                                            | Số dòng × cột |
| ---------------------------------- | ------------------------------------------------------------------ | ------------- |
| `googleplaystore.csv`              | `3e438f48161961933d26e99a8d9fc8ed79edfaa9fb34f8838e1ab4ec7a9fab91` | 10 841 × 13   |
| `googleplaystore_user_reviews.csv` | `5074250eaf0722db4a5707f0b06dcdf3663310348761ccaab01ec6f94411269b` | 64 295 × 5    |

Hash được kiểm tự động bằng `scripts/download_data.py` (mã thoát 1 nếu file thiếu hoặc khác bản này).

## 4. Các vấn đề chất lượng đã tìm thấy

Mọi số dưới đây do nhóm tự đếm trong `notebooks/nb01_data_quality.ipynb`. Bảng app đo theo thứ tự: thô (10 841 dòng) → bỏ dòng lệch cột (A0, 10 840) → bỏ trùng hoàn toàn (A1, 10 357). Tỉ lệ ở vấn đề 4 và 5 tính trên A1.

| #   | Vấn đề                                                        | Bằng chứng (số tự đếm)                                                                                                                                                          | Hệ quả                                                                                                                                      | Xử lý                                                                                             |
| --- | ------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| 1   | Dòng lệch cột: mọi trường dịch trái một cột                   | 1 dòng (chỉ số 10472, app "Life Made WI-Fi Touchscreen Photo Frame"): Rating = 19.0 (miền hợp lệ 1–5), Category = 1.9, Installs = "Free", Reviews = "3.0M". nb01 ô 2            | Rating = 19 làm sai trung bình, ngưỡng low-rated và biểu đồ phân phối; Category là số làm sai nhóm theo danh mục                            | Loại, `drop_reason = misaligned`. Không sửa tay vì cần tra ngoài dữ liệu. decision_log #\_\_      |
| 2   | Dòng trùng hoàn toàn ở bảng app                               | 483 dòng (10 840 → 10 357). nb01 ô 3                                                                                                                                            | App bị đếm nhiều lần, làm lệch tỉ lệ low-rated theo danh mục                                                                                | Loại, `exact_dup`. decision_log #\_\_                                                             |
| 3   | Cùng tên app nhưng khác thuộc tính sau khi bỏ trùng hoàn toàn | 10 357 dòng nhưng chỉ 9 659 tên duy nhất: thừa 698 dòng. Ví dụ "8 Ball Pool" có 8 dòng, 7 dòng Category = GAME và 1 dòng SPORTS, Reviews từ 14 184 910 đến 14 201 891. nb01 ô 4 | Một app bị tính nhiều lần; khoá nối review → app chỉ là tên nên không còn duy nhất; cách chọn dòng giữ lại quyết định luôn danh mục của app | Giữ dòng có `Reviews` lớn nhất (hoà: `Last Updated` mới nhất). decision_log #\_\_                 |
| 4   | Rating thiếu                                                  | 1 465 dòng (14,1% của 10 357). nb01 ô 5                                                                                                                                         | Hơn 1/7 app không có điểm nên không phân loại được low-rated; nhóm thiếu có thể không ngẫu nhiên                                            | Không điền. Loại khỏi phân tích điểm, kết luận chỉ áp dụng cho app đã có điểm. decision_log #\_\_ |
| 5   | `Size` trộn đơn vị M/k và giá trị chữ "Varies with device"    | 8 516 dòng đuôi M, 315 đuôi k, 1 526 dòng "Varies with device" (14,7%). nb01 ô 6                                                                                                | Không so sánh được dung lượng khi chưa quy về MB; điền trung bình cho "Varies" sẽ bịa dữ liệu cho gần 1/7 app                               | Đổi sang MB (k ÷ 1024); "Varies" → NULL + band `Varies`. decision_log #\_\_                       |
| 6   | `Installs` và `Price` là chuỗi có ký tự (`+`, `,`, `$`)       | 21 giá trị Installs khác nhau (dạng "1,000,000+"); 765 giá có `$`. nb01 ô 7                                                                                                     | Không tính toán hay sắp thứ tự đúng được (sắp theo chuỗi sẽ sai); Installs chỉ là cận dưới của khoảng nên trung bình trên đó không có nghĩa | Đổi sang cận dưới số nguyên + band thứ tự; bỏ `$` thành số. decision_log #\_\_                    |
| 7   | Review trùng hoàn toàn và review trống                        | 33 616 / 64 295 dòng trùng (52,3%); 26 868 dòng không có văn bản (41,8%). nb01 ô 8                                                                                              | Phân tích văn bản bị thổi phồng bởi bản sao; chỉ còn khoảng 30 679 dòng khác nhau, trong đó phần có văn bản còn ít hơn                      | Loại trùng; giữ dòng trống ở staging, loại khỏi phân tích văn bản (`no_text`). decision_log #\_\_ |
