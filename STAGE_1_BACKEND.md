# STAGE 1: BACKEND LOGIC & DATA FOUNDATION

Giai đoạn này tập trung vào việc hoàn thiện cấu trúc dữ liệu và logic xử lý ngầm.

## 1. Hoàn thiện Model (`models/main.py`)
Mục tiêu: Thêm các method xử lý trạng thái (workflow) và tự động sinh mã (sequence).

**Nội dung cần cập nhật:**
```python
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ServiceRequest(models.Model):
    _name = 'service.request'
    _description = 'Service Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(string='Mã yêu cầu', required=True, copy=False, readonly=True, default='New')
    customer_id = fields.Many2one('res.partner', string='Khách hàng', tracking=True)
    service_type = fields.Selection([
        ('repair', 'Sửa chữa'),
        ('consulting', 'Tư vấn'),
        ('installation', 'Lắp đặt'),
    ], string='Loại dịch vụ', required=True, tracking=True)
    description = fields.Text(string='Mô tả')
    request_date = fields.Datetime(string='Ngày yêu cầu', default=fields.Datetime.now, tracking=True)
    deadline = fields.Datetime(string='Deadline', tracking=True)
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('submitted', 'Đã gửi'),
        ('approved', 'Đã duyệt'),
        ('done', 'Hoàn thành'),
        ('cancelled', 'Đã hủy'),
    ], string='Trạng thái', default='draft', tracking=True)
    assigned_to = fields.Many2one('res.users', string='Người phụ trách', tracking=True)
    amount_estimate = fields.Float(string='Chi phí dự kiến', tracking=True)
    note = fields.Text(string='Ghi chú')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('service.request') or 'New'
        return super().create(vals_list)

    def action_submit(self):
        for rec in self:
            if not rec.customer_id:
                raise ValidationError('Vui lòng chọn Khách hàng!')
            rec.state = 'submitted'
            self._send_notification('service_request_managemen.email_template_submit')

    def action_approve(self):
        for rec in self:
            if not rec.assigned_to:
                raise ValidationError('Vui lòng chọn Người phụ trách!')
            rec.state = 'approved'
            self._send_notification('service_request_managemen.email_template_approved')

    def action_done(self): self.write({'state': 'done'})
    def action_cancel(self): self.write({'state': 'cancelled'})
    def action_reset_draft(self): self.write({'state': 'draft'})

    def _send_notification(self, template_xml_id):
        template = self.env.ref(template_xml_id, raise_if_not_found=False)
        if template:
            for rec in self:
                template.send_mail(rec.id, force_send=True)
```

## 2. Cấu hình Sequence (`data/sequence.xml`)
Tạo file này để hệ thống tự nhảy số SR0001, SR0002...

**Nội dung:**
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="sequence_service_request" model="ir.sequence">
        <field name="name">Service Request Sequence</field>
        <field name="code">service.request</field>
        <field name="prefix">SR</field>
        <field name="padding">4</field>
        <field name="number_next">1</field>
        <field name="number_increment">1</field>
    </record>
</odoo>
```
