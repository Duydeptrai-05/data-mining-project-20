# Khai báo sử dụng AI - thành viên C
(Tiêu chí 10: mỗi người tự ghi. A thu, D xác nhận. Số lần/ nội dung phải khớp lịch sử hệ thống.)

| Ngày | Công cụ | Dùng cho việc gì | Prompt chính (tóm tắt) | Em đã kiểm tra/sửa gì |
|---|---|---|---|---|
| 30/10/2026 | Claude (Anthropic) | Hướng dẫn chi tiết cách làm phần C (tiêu chí 1, 5, 7); giải thích ROLLUP / GROUPING SETS / Wilson / bootstrap / hoán vị | Nhờ hướng dẫn phần người C từ khâu chuẩn bị đến thực hiện, kèm file phân công v3 và dữ liệu của nhóm | Em đọc hướng dẫn và đối chiếu với file phân công v3 |
| 30/10/2026 | Claude (Anthropic) | Soạn bản nháp `nb03_main_analysis.ipynb`, `nb05_robustness.ipynb`, câu SQL `q07`, khung chương báo cáo, dàn ý slide; đọc repo (chỉ đọc, không sửa) | "xem github và làm tiếp, không sửa gì trong github" | Em chép các file vào repo để chạy thử; chưa chạy trên dữ liệu thật tại thời điểm khai báo này |
| 04/11/2026 | Claude (Anthropic) | Rút số thật từ `outputs/results.json` (6 709 app đủ điều kiện, 183 app điểm thấp, bảng theo danh mục, Wilson); soạn các dòng decision log C-1 đến C-7 và gợi ý lý do cho các ngưỡng nb05 | "làm lại phần người C"; nhờ AI làm giúp phần ngưỡng vì em chưa đủ chuyên môn tự chọn | Em giao AI đề xuất ngưỡng C-1 đến C-5; em đọc lời giải thích, đồng ý với các giá trị và commit vào decision_log trước khi chạy nb05 |
| 04/11/2026 | Claude (Anthropic) | Soạn ghi chú: bảng lỗi khi chạy `run_all.py`, các bước Superset, dàn ý câu hỏi bảo vệ | "làm tất cả" cho 3 việc còn lại | Em dùng làm ghi chú tham khảo cá nhân |

## Phần do em tự làm
- Em đọc lời giải thích của AI cho từng ngưỡng C-1 đến C-5, đồng ý với các giá trị AI đề xuất, rồi tự commit vào `docs/decision_log.md` trước khi chạy nb05. Các ngưỡng này do AI đề xuất, em không tự chọn.
- Em tự chạy `run_all.py`, đọc kết quả nb03/nb05 và tự viết phần "Kết luận" (nb03) và "Phân tích lỗi" (nb05).

## Giới hạn em biết
- Ngày 30/10 và 04/11, nb03/nb05 do AI soạn mới được thử trên dữ liệu giả lập, chưa phải dữ liệu thật. (Cập nhật dòng này sau khi em chạy xong trên dữ liệu thật.)
- Em chưa đủ chuyên môn để tự chọn ngưỡng C-1 đến C-5 nên đã nhờ AI đề xuất; em hiểu lý do từng ngưỡng như ghi trong decision log.
