# Service Request Management (Odoo 17)

## 📌 Tổng quan (Overview)
**Service Request Management** là module Odoo 17 quản lý yêu cầu dịch vụ theo workflow: `Draft → Submitted → Approved → Done` (hoặc `Cancelled`).

## ✨ Tính năng chính (Key Features)
1. **Workflow Management:** Duyệt yêu cầu qua các trạng thái, có nút Submit/Approve/Done/Cancel/Reopen.
2. **Automated Notifications:** Gửi email tự động khi submit, approve, và nhắc deadline qua cron job chạy hàng ngày.
3. **QWeb PDF Report:** In báo cáo yêu cầu dịch vụ kèm bảng service lines.
4. **Security & Access Rights:** 2 nhóm phân quyền — Service User và Service Manager.

## ✅ Đã fix / cải thiện
- **Email template:** Thay IP cứng `100.81.225.45:8069` bằng `object.get_base_url()` dynamic.
- **Stock integration:** `action_confirm()` tạo `stock.picking` + `stock.move`, `action_cancel()` hủy picking.
- **Model cleanup:** Xóa `laptop.inventory`, dùng `product.product` + `stock` chuẩn Odoo.
- **Model cleanup:** Xóa field `amount_estimate`, dùng `amount_total` với `currency_id`.
- **Model cleanup:** Xóa `service_type` khỏi header, chỉ giữ ở line level.
- **Validation:** Cảnh báo khi đặt deadline trong quá khứ (`_onchange_deadline`).
- **PDF report:** Cập nhật hiển thị bảng `request_line_ids` đầy đủ.

