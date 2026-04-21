# Service Request Management (Odoo 17)

## 📌 Tổng quan (Overview)
**Service Request Management** là một module tùy chỉnh dành cho Odoo 17, được thiết kế để số hóa và tự động hóa quy trình quản lý các yêu cầu cung cấp dịch vụ nội bộ hoặc từ khách hàng.

Module giúp chuẩn hóa quy trình tiếp nhận, phê duyệt và theo dõi tiến độ công việc, đồng thời tự động hóa việc giao tiếp qua Email và hệ thống nhắc việc (Activity/Cron) tích hợp sẵn trong Odoo.

## ✨ Tính năng chính (Key Features)
1. **Quản lý Vòng đời Yêu cầu (Workflow Management):**
   - Thiết lập luồng trạng thái chuẩn: `Draft` ➔ `Submitted` ➔ `Approved` ➔ `Done` (hoặc `Cancelled`).
   - Tích hợp kiểm tra tính hợp lệ (Validation): Ràng buộc dữ liệu khách hàng khi gửi và dữ liệu người phụ trách khi phê duyệt.

2. **Hệ thống Thông báo Tự động (Automated Notifications):**
   - Tự động gửi Email chuyên nghiệp có nhúng link bản ghi đến khách hàng khi yêu cầu được Nhận (Submit) và Phê duyệt (Approve).
   - Tự động sinh hành động cần làm (To-do Activity) để nhắc việc trực tiếp trên giao diện Odoo.

3. **Cảnh báo Hạn chót (Deadline Reminder via Cron):**
   - Lên lịch hành động tự động (Scheduled Action) chạy mỗi ngày.
   - Gửi Email cảnh báo kèm việc tạo Activity khi một phiếu yêu cầu sắp đến hạn (trong vòng 24h) mà chưa hoàn thành.

4. **Báo cáo In ấn (QWeb PDF Report):**
   - Tự động kết xuất báo cáo PDF chuẩn hóa.
   - Bao gồm đầy đủ Layout Header/Footer, Logo công ty, phân tách thông tin khách hàng, dịch vụ, chi phí và thông tin chữ ký.

5. **Phân quyền Bảo mật (Security & Access Rights):**
   - Lớp **Service User**: Quyền tạo và quản lý hồ sơ cá nhân.
   - Lớp **Service Manager**: Toàn quyền kiểm soát và phê duyệt mọi yêu cầu dịch vụ trên toàn hệ thống.

## 🛠 Cấu trúc Kỹ thuật (Technical Architecture)
Dự án áp dụng chặt chẽ kiến trúc MVC tùy biến của Odoo:
- **Models (`models/main.py`)**: Chứa logic xử lý, kiểm tra dữ liệu (`ValidationError`), xử lý hành động chuyển trạng thái, tạo sequence (`@api.model_create_multi`) và hàm quét deadline (`action_send_deadline_reminder`).
- **Views (`views/service_request_views.xml`)**: 
  - Giao diện Form View với `statusbar` và các component nhóm dữ liệu rõ ràng.
  - Giao diện Tree View rút gọn 5 cột quan trọng nhất.
- **Data (`data/`)**: 
  - `sequence.xml`: Cấu hình bộ đếm tự động (Ví dụ: `SR0001`).
  - `email_templates.xml`: 3 mẫu Email HTML tích hợp mã QWeb.
  - `cron.xml`: Khởi tạo tác vụ nền theo chu kỳ thời gian.
- **Security (`security/`)**: Chứa tệp `res_groups.xml`, phân quyền Record Rules và `ir.model.access.csv`.

## 🚀 Hướng dẫn Cài đặt & Sử dụng (Installation & Usage)
1. Copy thư mục `service_request_managemen` vào thư mục `addons` của hệ thống Odoo 17.
2. Bật chế độ nhà phát triển (Developer Mode) trong Odoo.
3. Chuyển đến menu **Apps** (Ứng dụng), chọn **Update Apps List** (Cập nhật danh sách ứng dụng).
4. Tìm kiếm từ khóa `Service Request Management` và nhấn **Install**.

### Sử dụng
- Tìm ứng dụng bằng biểu tượng **Service** trên thanh Menu chính.
- Click **New** để tạo mới một yêu cầu. Luồng công việc sẽ được hướng dẫn trực quan bằng các nút bấm trên thanh Header.
- Để kiểm tra nhắc nhở Cron, truy cập `Settings > Technical > Scheduled Actions`, tìm `Service Request: Deadline Reminder` và click `Run Manually`.
