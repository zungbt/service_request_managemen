# STAGE 2: COMMUNICATION (EMAIL & CRON)

Giai đoạn này thiết lập hệ thống thông báo tự động.

## 1. Email Templates (`data/email_templates.xml`)
Tạo các mẫu email gửi cho khách hàng và nhân viên.

**Mẫu Email Submit:**
```xml
<record id="email_template_submit" model="mail.template">
    <field name="name">Service Request: Submitted</field>
    <field name="model_id" ref="model_service_request"/>
    <field name="subject">[Service Request] {{ object.name }} đã được tạo</field>
    <field name="email_to">{{ object.customer_id.email }}</field>
    <field name="body_html" type="html">
        <p>Chào {{ object.customer_id.name }}, yêu cầu <b>{{ object.name }}</b> của bạn đã được gửi thành công!</p>
    </field>
</record>
```
*(Lưu ý: Bạn có thể copy full code từ implementation_plan.md để có nội dung đẹp hơn)*

## 2. Deadline Reminder Method (Bổ sung vào `models/main.py`)
Thêm hàm này vào cuối class `ServiceRequest`:
```python
    @api.model
    def action_send_deadline_reminder(self):
        from datetime import timedelta
        today = fields.Datetime.now().replace(hour=0, minute=0, second=0)
        tomorrow = today + timedelta(days=1)
        records = self.search([
            ('state', 'not in', ['done', 'cancelled']),
            ('deadline', '>=', tomorrow),
            ('deadline', '<', tomorrow + timedelta(days=1)),
        ])
        template = self.env.ref('service_request_managemen.email_template_deadline_reminder', False)
        if template:
            for rec in records:
                template.send_mail(rec.id, force_send=True)
```

## 3. Scheduled Action (`data/cron.xml`)
Thiết lập để hệ thống tự quét deadline mỗi ngày.
```xml
<record id="cron_deadline_reminder" model="ir.cron">
    <field name="name">Service Request: Nhắc Deadline</field>
    <field name="model_id" ref="model_service_request"/>
    <field name="state">code</field>
    <field name="code">model.action_send_deadline_reminder()</field>
    <field name="interval_number">1</field>
    <field name="interval_type">days</field>
    <field name="numbercall">-1</field>
</record>
```
