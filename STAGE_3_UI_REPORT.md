# STAGE 3: INTERFACE & REPORTING

Giai đoạn này làm đẹp giao diện và tạo file in ấn.

## 1. Views (`views/service_request_views.xml`)
Thiết lập Tree, Form và Search view.

**Gợi ý cấu trúc Form:**
- Header: Chứa các button `action_submit`, `action_approve`... và statusbar.
- Sheet: Chứa các Group thông tin khách hàng, dịch vụ, chi phí.
- Chatter: Cuối cùng là `mail.chatter`.

## 2. PDF Report (`report/`)
Cần tạo 2 file:
1. `report_action.xml`: Khai báo nút "In" trong menu Print.
2. `service_request_report.xml`: Định dạng HTML/QWeb cho nội dung file PDF.

**Code mẫu Report Action:**
```xml
<record id="action_report_service_request" model="ir.actions.report">
    <field name="name">Phiếu yêu cầu dịch vụ</field>
    <field name="model">service.request</field>
    <field name="report_type">qweb-pdf</field>
    <field name="report_name">service_request_managemen.report_service_request_template</field>
    <field name="binding_model_id" ref="model_service_request"/>
</record>
```
