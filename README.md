# Project Dashboard

[Mở Project Dashboard](outputs/dashboard.md) để xem biểu đồ theo tuần, phân bố thời gian từ mở đến đóng và số issue theo nhóm nội dung.

Bản bàn giao độc lập có `SHA256SUMS`. Từ thư mục chứa README, chạy `sha256sum --check SHA256SUMS` để kiểm tra các tệp trước khi chạy lại phân tích. MS Project Desktop là tùy chọn. Các mốc Excel và MS Project Desktop bên dưới là kết quả kỳ vọng từ phép tính bằng Python.

## Bản dữ liệu cố định

- Kho nguồn: [`openmrs-indianaems/openmrs-indianaems-config`](https://github.com/openmrs-indianaems/openmrs-indianaems-config).
- Nguồn: [GitHub REST API, phiên bản `2022-11-28`](https://api.github.com/repos/openmrs-indianaems/openmrs-indianaems-config/issues?state=all&per_page=100&page=1). Thu thập ngày 18/11/2026 lúc 08:05:34 UTC.
- Phạm vi: `state=all` lấy cả issue mở và đã đóng, không lọc ngày. Phản hồi có 26 bản ghi và không có liên kết `rel="next"`. Loại mọi bản ghi có khóa `pull_request` trước khi chọn cột. Phản hồi này không có pull request.
- [`data/issues.csv`](data/issues.csv) giữ đúng bốn cột: `number` là mã issue, `state` là trạng thái, `created_at` và `closed_at` là thời điểm UTC. Với issue còn mở, cột `closed_at` để trống. Không lưu phản hồi gốc, nội dung issue, thông tin bệnh nhân hay thông tin xác thực.

## Chạy lại ngoại tuyến

Cài Python 3.10 trở lên và XeLaTeX. Bản này kiểm tra bằng Python 3.15.2 và TeX Live 2026. Bộ cài TeX Live đầy đủ có các gói cần dùng: `standalone`, `fontspec`, `pgf`, `pgfplots` và phông Latin Modern Sans. Bản cài tối giản cần cài thêm các gói này trước khi chạy. Python chỉ dùng thư viện chuẩn.

Mở thư mục chứa README này và chạy lệnh sau.

```sh
python3 build_all.py
```

Lệnh đọc các tệp CSV trong `data/` và tái lập Dashboard, lịch CPM và chi phí trong `outputs/`. Lệnh chạy ngoại tuyến với Python và XeLaTeX. Trong thư mục chứa `main.tex`, dùng `python3 repo/build_all.py`.

### Kết quả Dashboard

| Tệp | Nội dung |
| --- | --- |
| [`outputs/weekly.csv`](outputs/weekly.csv) | Ngày thứ Hai đầu tuần UTC, lượt tạo và lượt đóng. |
| [`outputs/issue-weeks.csv`](outputs/issue-weeks.csv) | Mã issue và tuần UTC của từng sự kiện, để đối chiếu về dữ liệu gốc. |
| [`outputs/weekly.pdf`](outputs/weekly.pdf) | Biểu đồ cột dựng từ `weekly.csv`. Chương 3 và slide 11 dùng cùng tệp. |
| [`outputs/dashboard.md`](outputs/dashboard.md) | Project Dashboard, có bảng phân bố thời gian và bảng phân loại. |
| [`outputs/issue-analysis.tex`](outputs/issue-analysis.tex) | Cùng số liệu phân bố, trung vị và phân loại ở định dạng dùng trong Chương 3 và slide 12, 13. |

Nếu chỉ cần tái lập Dashboard, chạy `python3 build_weekly.py`.

## Quy tắc đếm và đối chiếu

Tuần bắt đầu lúc 00:00 UTC thứ Hai. Mỗi issue có một lượt tạo ở tuần của `created_at`. Chỉ issue ở trạng thái `closed` có lượt đóng ở tuần của `closed_at`. Bảng giữ tuần trống giữa tuần đầu và tuần cuối. Bản cố định không cho biết lịch sử mở lại và không đo năng suất.

Cộng hai cột số đếm trong `weekly.csv` cho kết quả 26 lượt tạo và 25 lượt đóng. Tra mã 17 trong `data/issues.csv` và đối chiếu với `outputs/issue-weeks.csv`. Thời điểm tạo thuộc tuần 20/04/2020. Cả thời điểm đóng và tuần đóng đều để trống. Mã 26 được tạo trong cùng tuần và được tính đóng vào tuần 11/05/2020.

## Thời gian từ mở đến đóng và phân loại

Với mỗi issue đã đóng, lấy `closed_at` trừ `created_at` rồi đổi sang giờ. Trung vị dùng các giá trị chưa làm tròn. Dashboard làm tròn trung vị đến một chữ số thập phân. Bảng phân bố và trung vị bỏ qua issue còn mở. Bảng phân loại vẫn tính issue còn mở. Chênh lệch giữa hai mốc gồm cả thời gian chờ. Bản cố định chỉ bao quát issue công khai ở kho cấu hình. Dự án còn có công việc ở kho khác và ngoài GitHub.

[`data/issue-classifications.csv`](data/issue-classifications.csv) có đúng một nhóm và lý do ngắn cho mỗi mã trong bản cố định. Đọc tiêu đề, mô tả và thảo luận khi cần trên [danh sách issue của kho](https://github.com/openmrs-indianaems/openmrs-indianaems-config/issues). Các mã nhóm gồm `bug` khi nội dung nêu hành vi không đúng, `change` khi nội dung đề nghị thêm, bỏ hoặc sửa chức năng hoặc quy tắc, và `insufficient` khi nội dung chưa đủ để xác định hành vi hoặc thay đổi cụ thể. Chạy lại lệnh sẽ đếm các nhóm đã ghi trong CSV. Người đọc có thể đối chiếu từng lý do bằng cách mở issue theo mã.

## Tự đối chiếu bằng Excel

1. Nhập [`data/issues.csv`](data/issues.csv) vào trang tính trắng bằng **Data > From Text/CSV**. Chọn UTF-8, dấu phẩy và **Do not detect data types** để giữ `created_at` và `closed_at` ở dạng văn bản UTC. Nạp tiêu đề ở hàng 1 và bốn cột gốc ở A đến D.
2. Tạo ba cột E, F, G với tiêu đề `created_excel`, `closed_excel`, `hours`. Nhập các công thức sau ở hàng 2 rồi sao chép xuống hết 26 dòng dữ liệu. Công thức dùng hàm tiếng Anh và dấu phẩy ngăn cách đối số. Nếu Excel dùng dấu chấm phẩy, đổi dấu phân cách trong công thức.

   | Ô | Công thức |
   | --- | --- |
   | E2 | `=DATE(LEFT(C2,4),MID(C2,6,2),MID(C2,9,2))+TIME(MID(C2,12,2),MID(C2,15,2),MID(C2,18,2))` |
   | F2 | `=IF(B2="closed",DATE(LEFT(D2,4),MID(D2,6,2),MID(D2,9,2))+TIME(MID(D2,12,2),MID(D2,15,2),MID(D2,18,2)),"")` |
   | G2 | `=IF(B2="closed",24*(F2-E2),"")` |

3. Lọc `state=closed`. Ở các ô ngoài vùng lọc, dùng `=COUNT(G2:G27)` và `=ROUND(MEDIAN(G2:G27),1)`. Công thức cột G trả chuỗi rỗng cho issue còn mở. `COUNT` và `MEDIAN` chỉ dùng các ô chứa số, ngay cả khi vẫn tham chiếu cả cột dữ liệu.
4. Chạy lại Dashboard từ cùng CSV. Tiêu chí khớp là cùng số issue có giờ và cùng trung vị làm tròn một chữ số thập phân.

Chạy kiểm thử bằng `python3 -m unittest discover -s tests`. Bộ kiểm thử dựng lại kết quả từ dữ liệu cố định trong thư mục tạm và kiểm tra Dashboard, lịch và chi phí.

## Tái lập lịch đề xuất

[`data/schedule.csv`](data/schedule.csv) ghi các gói WBS thuộc phạm vi Project Charter. `id` là số dòng công việc theo thứ tự nhập. `predecessors` liệt kê ID của các gói đi trước, phân cách bằng dấu phẩy. Cột `calendar` dùng mã `LV` cho lịch thứ Hai đến thứ Sáu, 08:00 đến 12:00 và 13:00 đến 17:00, 8 giờ mỗi ngày, không có ngoại lệ. Toàn bộ liên kết là kết thúc rồi mới bắt đầu (FS) với độ trễ 0. Thời lượng trong `duration_days` là giả định lập kế hoạch của sinh viên. Căn cứ và giới hạn nằm ở Chương 2 của báo cáo.

Chạy `python3 build_schedule.py` từ thư mục này hoặc `python3 repo/build_schedule.py` từ thư mục báo cáo. Lệnh chỉ dùng thư viện chuẩn của Python 3.10 trở lên. Lệnh tính lịch cơ sở rồi cộng 3 ngày vào riêng gói 2.3 để tính kịch bản HL7.

| Tệp | Nội dung |
| --- | --- |
| [`outputs/schedule-baseline.csv`](outputs/schedule-baseline.csv) | Lịch cơ sở, 9 ngày làm việc. |
| [`outputs/schedule-hl7-delay.csv`](outputs/schedule-hl7-delay.csv) | Kịch bản tăng thời lượng HL7, 10 ngày làm việc. |
| [`outputs/schedule.tex`](outputs/schedule.tex) | Số liệu dùng chung cho bảng, mạng phụ thuộc và Gantt trong LaTeX. |

Các cột `es`, `ef`, `ls`, `lf` đếm ngày làm việc từ mốc 0. Để đọc Gantt hoặc phân bổ chi phí theo ngày, lấy khoảng từ `es` đến trước `ef`. Khoảng `es=1`, `ef=3` chiếm ngày làm việc thứ 2 và thứ 3. `total_float` bằng `ls` trừ `es`. `critical=1` đánh dấu gói găng. Báo cáo và slide đặt vị trí các nút theo mã WBS. Khi thêm hoặc đổi mã WBS, cập nhật vị trí nút trong `schedule-charts.tex` ở thư mục báo cáo. Khi sửa giả định, cập nhật các ví dụ diễn giải số liệu và mốc đối chiếu tương ứng.

## Tái lập nguồn lực và chi phí

Từ thư mục chứa README này, chạy `python3 build_schedule.py && python3 build_cost.py`. Từ thư mục báo cáo, thêm `repo/` vào trước tên hai tệp Python. Lệnh thứ hai dùng các mốc CPM vừa tính, [`data/resource-hours.csv`](data/resource-hours.csv) và [`data/resource-rates.csv`](data/resource-rates.csv). Mỗi ô giờ là số giờ công của một vai trò trong một ngày làm việc của gói WBS. Đơn giá là số nguyên USD/giờ. Tất cả số giờ và đơn giá là giả định lập kế hoạch của sinh viên.

| Tệp | Nội dung |
| --- | --- |
| [`outputs/cost-allocations.csv`](outputs/cost-allocations.csv) | Giờ công, đơn giá và thành tiền theo kịch bản, ngày, gói WBS và vai trò. |
| [`outputs/cost-daily.csv`](outputs/cost-daily.csv) | Tổng giờ công, chi phí ngày và chi phí tích lũy cuối ngày theo kịch bản. |
| [`outputs/cost.tex`](outputs/cost.tex) | Số liệu dùng chung cho các bảng và đường chi phí tích lũy trong báo cáo và slide. |

Để đối chiếu, lọc `scenario=baseline` và `day=2` trong bảng phân bổ. Bốn dòng khác 0 thuộc các gói `2.1`, `2.2` và `2.3`. Tổng là 19 giờ công và 1.760 USD. Cộng 610 USD của ngày 1 để có 2.370 USD tích lũy cuối ngày 2. Cộng chi phí của cả chín ngày để có 9.620 USD.

`hl7-delay` dùng lịch tăng thời lượng của gói `2.3`, giữ đơn giá và giờ công mỗi ngày. Kết quả là 130 giờ công, 10 ngày và 11.600 USD. `hl7-rate` dùng lịch cơ sở và đổi riêng đơn giá INT từ 110 sang 135 USD/giờ. Chênh lệch bằng 29 giờ nhân 25 USD/giờ, tức 725 USD. Tổng mới là 10.345 USD trong 9 ngày. Có thể thử một mức riêng bằng `python3 build_cost.py --hl7-rate 150`, rồi chạy lại lệnh không có tùy chọn để khôi phục kịch bản của bài nộp. Nếu sửa bảng giả định cơ sở, cập nhật các ví dụ đối chiếu trong báo cáo và README theo kết quả mới.

## Đối chiếu bằng MS Project Desktop

Quy trình dưới đây dùng ngày giả định 01/02/2027 để chuyển mốc tương đối sang ngày lịch. Kết quả đối chiếu kỳ vọng lấy từ phép tính CPM bằng Python. Sinh viên có thể tự chạy quy trình nếu chọn dùng MS Project Desktop.

1. Tạo dự án trống. Trong **Project Information**, lập lịch từ ngày bắt đầu và đặt **Start date** là 01/02/2027 lúc 08:00. Trong **Change Working Time**, tạo lịch `LV`, đặt thứ Hai đến thứ Sáu làm việc 08:00 đến 12:00 và 13:00 đến 17:00. Đặt thứ Bảy và Chủ nhật nghỉ, bỏ các ngoại lệ nếu có, rồi chọn lịch `LV` cho dự án. Trong **File > Options > Schedule**, đặt 8 giờ/ngày, 40 giờ/tuần, giờ bắt đầu mặc định 08:00 và giờ kết thúc 17:00. Bật tính toán tự động và chọn **Auto Scheduled** cho công việc mới.
2. Mở CSV bằng chức năng nhập văn bản của Excel với UTF-8 và dấu phẩy làm dấu phân cách. Đặt `wbs` và `predecessors` là văn bản để Excel giữ mã như `4.1` và danh sách như `6,7,8`. Trong **Gantt Chart**, chép chín dòng theo thứ tự `id`. Chép `name` vào **Task Name**, `wbs` vào **Text1**, và `duration_days` vào **Duration** với đơn vị ngày, ví dụ `4d` với giao diện tiếng Anh. Để Project cấp ID 1 đến 9. Sau khi đã có cả chín dòng, chép `predecessors` vào **Predecessors** theo đúng ID. Gói 4.2 có các tiền nhiệm `6,7,8`. Dùng dấu phân cách danh sách theo thiết lập vùng của Project. Nếu dán không được, nhập từng ID trong thẻ **Predecessors** của **Task Information**, chọn **Finish-to-Start** và **Lag** bằng 0.
3. Kiểm tra **Task Mode** là **Auto Scheduled** cho cả chín dòng. Dùng lịch chung `LV`, giữ công việc ở cấp thường và lập lịch sớm nhất có thể. Để trống tài nguyên và ngày ràng buộc. Tắt cân bằng tài nguyên tự động. Đặt ngưỡng găng là 0 ngày trong **File > Options > Advanced**. Bật **Critical Tasks** trong Gantt và thêm cột **Total Slack**. Công việc cuối kỳ vọng kết thúc lúc 17:00 ngày 11/02/2027, tức 9 ngày làm việc. Mã WBS găng kỳ vọng là `1.1`, `2.2`, `3.1`, `3.2`, `4.2`. Gói 2.3 và 3.3 có 2 ngày dự trữ.
4. Lưu một bản riêng rồi đổi **Duration** của ID 4, WBS 2.3, từ 4 sang 7 ngày. Công việc cuối kỳ vọng kết thúc lúc 17:00 ngày 12/02/2027, tức 10 ngày làm việc. Mã WBS găng kỳ vọng là `1.1`, `2.3`, `3.3`, `4.2`. Gói 3.2 có 1 ngày dự trữ. Nếu kết quả khác, so lại thứ tự ID, lịch `LV`, chế độ lập lịch, các liên kết FS và cột **Total Slack** với hai tệp CSV.
