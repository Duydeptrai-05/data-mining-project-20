# 8. Dashboard và kết luận cho người ra quyết định

## 8.1 Dashboard Superset

**Bảng 9.** Các biểu đồ trên dashboard

| #   | Biểu đồ                                            | Câu hỏi nó trả lời                                                                          | Bộ lọc áp dụng                                           |
| --- | -------------------------------------------------- | ------------------------------------------------------------------------------------------- | -------------------------------------------------------- |
| 1   | Tỉ lệ app Rating ≤ 3,0 theo danh mục (cột ngang)   | Danh mục nào có tỉ lệ app điểm thấp cao nhất, và chênh lệch giữa danh mục có đáng kể không? | App có điểm và từ 50 đánh giá; ô n < 30 bị ẩn            |
| 2   | Điểm trung bình theo mức giá                       | App trả phí có điểm khác app miễn phí không?                                                | Như trên                                                 |
| 3   | Tỉ lệ điểm thấp theo độ cũ của lần cập nhật cuối   | App lâu không cập nhật có tỉ lệ điểm thấp cao hơn không?                                    | Như trên                                                 |
| 4   | Tỉ lệ điểm thấp theo lượt cài                      | Lượt cài tăng thì tỉ lệ điểm thấp thay đổi thế nào?                                         | Như trên                                                 |
| 5   | Chủ đề phàn nàn hàng đầu theo danh mục (cột chồng) | Người dùng phàn nàn về điều gì theo từng danh mục?                                          | Bỏ nhóm "khác"; chỉ 27 danh mục có từ 30 review tiêu cực |
| 6   | Top 10 app theo điểm (bảng, minh hoạ FAMILY)       | Xếp hạng theo điểm trung bình có đáng tin không?                                            | Danh mục FAMILY; app từ 50 đánh giá                      |

Dashboard hiện chưa có bộ lọc tương tác (người xem chưa tự chọn danh mục); các bộ lọc ở bảng là bộ lọc cố định của từng chart.

**Hình 6.** Ảnh chụp dashboard (docs/report/dashboard_D.jpg). Chú thích: hàng đầu là biểu đồ 1 (tỉ lệ điểm thấp theo danh mục); hàng hai gồm ba biểu đồ 2–4 (theo lượt cài, theo giá, theo độ cũ cập nhật); hàng ba là biểu đồ 5 (chủ đề phàn nàn theo danh mục); hàng cuối là ô lưu ý khi đọc và biểu đồ 6 (top 10 FAMILY).

**Thử nghiệm với người dùng ngoài nhóm.** Người thử: [:Bảo Thùy, không thuộc nhóm]. Ngày thử: 6/11/2026. Cách làm: cho người thử xem dashboard (hoặc ảnh Hình 6), không giải thích trước, hỏi ba câu dưới đây và ghi lại nguyên văn.

| Câu hỏi                                                                         | Trả lời nguyên văn                     | Đúng / sai / hiểu nhầm |
| ------------------------------------------------------------------------------- | -------------------------------------- | ---------------------- |
| 1. Nhìn vào đây, bạn thấy điều chính là gì?                                     | Không Biết                             | Hiểu Nhầm              |
| 2. Danh mục nào có tỉ lệ app điểm thấp cao nhất? (đáp án đúng: LIFESTYLE, 9,0%) | Cao nhất: LIFESTYLE, thấp nhất: BEAUTY | Đúng                   |
| 3. Có chỗ nào bạn không hiểu hoặc hiểu nhầm không?                              | Quá rối ko hiểu gì hết                 | Hiểu Nhầm              |

Chỉnh sửa dashboard sau khi thử: [ĐIỀN: đã đổi gì, hoặc ghi "không đổi" nếu người thử hiểu đúng].

## 8.2 Khuyến nghị

| #   | Nên làm gì                                                                                                                            | Căn cứ                                                                                                                             | Mức độ chắc chắn                                                                                                                       |
| --- | ------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Khi so sánh hay xếp hạng app theo điểm trung bình, đặt ngưỡng số đánh giá cao hơn 50 (đề xuất thử 500) và chạy lại top 10 để kiểm tra | Bảng 9 #6 và mục 9: top 10 FAMILY có 5/10 app chỉ 55–119 đánh giá, hạng 1–2 điểm 5,0 chỉ dựa trên 100 và 90 đánh giá               | Trung bình. Ngưỡng 500 chưa được kiểm thử trong báo cáo này                                                                            |
| 2   | Rà soát luồng tính tiền (giá, trả tiền để chơi tiếp, hoàn tiền) trước ở các danh mục GAME, FAMILY, TRAVEL_AND_LOCAL                   | Bảng 9 #5: tiền và thanh toán là chủ đề cụ thể đứng đầu ở 7/27 danh mục, các danh mục này chiếm 2 970/5 945 review tiêu cực (50%)  | Thấp đến trung bình. Precision của chủ đề này 0,38–0,88 (hai người gán lệch nhau); cần đọc thủ công một mẫu review trước khi hành động |
| 3   | Chưa dùng chủ đề "thiết bị" và "tài khoản" để ra quyết định                                                                           | Mục 6: precision "thiết bị" chỉ 0,17–0,22, "tài khoản" 0,30–0,38                                                                   | Cao (mức chắc chắn rằng nhãn không đủ tin)                                                                                             |
| 4   | Không phân bổ nguồn lực theo danh mục chỉ dựa trên tỉ lệ điểm thấp                                                                    | Bảng 9 #1: LIFESTYLE cao nhất (9,0%, n = 223) nhưng chênh lệch giữa các danh mục chưa vượt nhiều (hoán vị p ≈ 0,12; n = 6 709 app) | Trung bình                                                                                                                             |
| 5   | Không dùng giá (trả phí hay miễn phí) làm căn cứ dự đoán chất lượng                                                                   | Bảng 9 #2: dấu chênh lệch đổi giữa các cấu hình kiểm chứng (n = 6 709 app)                                                         | Trung bình                                                                                                                             |
| 6   | Ưu tiên kiểm tra chất lượng nhóm 10K–100K lượt cài                                                                                    | Bảng 9 #4: tỉ lệ điểm thấp 7,2% ở 10K–100K (n = 1 328), xuống 0,1% ở 10M+ (n = 1 373); đi cùng, không chứng minh nguyên nhân       | Trung bình                                                                                                                             |

# 9. Đạo đức, quyền riêng tư và công bằng

**Bảng 10.** Rủi ro và biện pháp giảm thiểu

| Ai có thể bị tổn hại                                                                 | Cơ chế gây hại                                                                                                                                                                                    | Mức độ                   | Biện pháp giảm thiểu                                                                                                     |
| ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------ | ------------------------------------------------------------------------------------------------------------------------ |
| Nhà phát triển app có nhiều đánh giá thật; người dùng dashboard chọn app theo top 10 | Xếp hạng chỉ theo điểm trung bình: 266/271 app (98,2%) điểm 5,0 có dưới 50 đánh giá; 305/520 vị trí (58,7%) top 10 thô thuộc app dưới 50 đánh giá (FAMILY: 65/67)                                 | Cao                      | Ngưỡng min_store_reviews = 50 và min_cell_n = 30; ghi n cạnh mọi số; khuyến nghị 1                                       |
| Người dùng của danh mục ít review có văn bản; chủ app có tên bị lệch khi nối review  | Chỉ 816/9 638 app (8,5%) có review văn bản. 54 tên không khớp bị loại (1 489 review, 4,85%), trong đó 44 tên (81,5%) không có trong bảng app, 9 tên (16,7%, 225 review) không phải chữ Latin, 1 tên là lỗi chuẩn hoá chưa sửa (decision log dòng 14). FAMILY có chỉ số đại diện 0,45, COMICS 0,28 | Trung bình               | Loại 6 danh mục dưới 30 review tiêu cực khỏi chart 5; báo công khai lượng dữ liệu bị loại                                |
| Người viết review                                                                    | Văn bản review có thể chứa thông tin cá nhân                                                                                                                                                      | Thấp (chưa quét tự động) | Dashboard không hiện review thô; role superset_ro chỉ đọc schema mart; repo không chứa văn bản review; dữ liệu CC BY 3.0 |
| Nhà phát triển (nhất là app nhỏ)                                                     | Gắn nhầm lý do phàn nàn: precision từ điển 0,36 (nhãn D) và 0,52 (nhãn A), đồng thuận người gán 65%                                                                                               | Trung bình               | Chú thích precision trên dashboard; không dùng thiết bị và tài khoản để kết luận; không dùng chủ đề để xếp hạng từng app |

**Thuộc tính nhạy cảm và proxy.** Dữ liệu không có thuộc tính nhạy cảm của người dùng (giới tính, tuổi, vùng miền). Có hai proxy đáng lưu ý: danh mục app (FAMILY, DATING, MEDICAL, FINANCE) gợi ra nhóm người dùng, và chữ viết của tên app (9/54 tên không khớp là chữ không phải Latin) gợi ra vùng ngôn ngữ. Chúng tôi không có thuộc tính nhóm của người dùng nên không thể so sánh hiệu năng theo nhóm người; chỉ so sánh được theo danh mục (chỉ số đại diện, precision theo chủ đề). Đây là một giới hạn đã nêu.
