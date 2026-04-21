# STAGE 4: FINALIZATION & DEPLOYMENT

Giai đoạn cuối: Kết nối mọi thứ và chạy thử.

## 1. Cập nhật Manifest (`__manifest__.py`)
Đảm bảo thứ tự load file chính xác để không bị lỗi ID.

```python
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'security/record_rules.xml',
        'data/sequence.xml',
        'data/email_templates.xml',
        'views/service_request_views.xml',
        'report/report_action.xml',
        'report/service_request_report.xml',
        'data/cron.xml',
    ],
```

## 2. Lệnh nâng cấp module
Mở Terminal và chạy lệnh sau (Windows):
```powershell
python odoo-bin -c odoo.conf -d DATABASE_NAME -u service_request_managemen
```

## 3. Checklist nghiệm thu
- [ ] Record mới có mã SR tự nhảy?
- [ ] Button chuyển trạng thái hoạt động đúng (Draft -> Submitted...)?
- [ ] Có báo lỗi khi không chọn Khách hàng mà đã Submit?
- [ ] File PDF in ra có logo và đúng thông tin?
- [ ] Email đã được log trong Chatter khi bấm nút?
