# Kế Hoạch Chi Tiết: Module Service Request Management (Odoo 17)

> Dành cho lập trình viên tự làm theo từng bước.
> Mỗi bước có giải thích **TẠI SAO** và **CODE MẪU** đầy đủ.

---

## Tổng quan cấu trúc file cuối cùng

```
service_request_managemen/
├── __init__.py                          ✅ đã có
├── __manifest__.py                      🔧 cần sửa
├── models/
│   ├── __init__.py                      ✅ đã có
│   └── main.py                          🔧 cần sửa (thêm workflow)
├── data/
│   ├── sequence.xml                     🆕 tạo mới
│   ├── email_templates.xml              🆕 tạo mới
│   └── cron.xml                         🆕 tạo mới
├── views/
│   └── service_request_views.xml        🆕 tạo mới
├── report/
│   ├── report_action.xml                🆕 tạo mới
│   └── service_request_report.xml       🆕 tạo mới
└── security/
    ├── res_groups.xml                   ✅ đã có
    ├── ir.model.access.csv              ✅ đã có
    └── record_rules.xml                 ✅ đã có
```

---

## BƯỚC 1 — Hoàn thiện Model (`models/main.py`)

> **Tại sao:** Model hiện tại chỉ có fields, chưa có workflow (buttons chuyển state), sequence tự động sinh mã SR, và gửi email.

**Mở file:** `models/main.py`  
**Xóa toàn bộ nội dung cũ**, thay bằng code sau:

```python
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ServiceRequest(models.Model):
    _name = 'service.request'
    _description = 'Service Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    # ── Fields ──────────────────────────────────────────────
    name = fields.Char(
        string='Mã yêu cầu',
        required=True, copy=False, readonly=True, default='New'
    )
    customer_id = fields.Many2one(
        'res.partner', string='Khách hàng', tracking=True
    )
    service_type = fields.Selection([
        ('repair', 'Sửa chữa'),
        ('consulting', 'Tư vấn'),
        ('installation', 'Lắp đặt'),
    ], string='Loại dịch vụ', required=True, tracking=True)
    description = fields.Text(string='Mô tả')
    request_date = fields.Datetime(
        string='Ngày yêu cầu', default=fields.Datetime.now, tracking=True
    )
    deadline = fields.Datetime(string='Deadline', tracking=True)
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('submitted', 'Đã gửi'),
        ('approved', 'Đã duyệt'),
        ('done', 'Hoàn thành'),
        ('cancelled', 'Đã hủy'),
    ], string='Trạng thái', default='draft', tracking=True)
    assigned_to = fields.Many2one(
        'res.users', string='Người phụ trách', tracking=True
    )
    amount_estimate = fields.Float(string='Chi phí dự kiến', tracking=True)
    note = fields.Text(string='Ghi chú')

    # ── Sequence ─────────────────────────────────────────────
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'service.request'
                ) or 'New'
        return super().create(vals_list)

    # ── Workflow Actions ──────────────────────────────────────
    def action_submit(self):
        """Draft → Submitted. Bắt buộc phải có khách hàng."""
        for rec in self:
            if not rec.customer_id:
                raise ValidationError(
                    'Vui lòng chọn Khách hàng trước khi gửi yêu cầu!'
                )
            rec.state = 'submitted'
            # Gửi email thông báo
            template = self.env.ref(
                'service_request_management.email_template_submit',
                raise_if_not_found=False
            )
            if template:
                template.send_mail(rec.id, force_send=True)

    def action_approve(self):
        """Submitted → Approved. Bắt buộc phải có người phụ trách."""
        for rec in self:
            if not rec.assigned_to:
                raise ValidationError(
                    'Vui lòng chọn Người phụ trách trước khi duyệt!'
                )
            rec.state = 'approved'
            # Gửi email thông báo
            template = self.env.ref(
                'service_request_management.email_template_approved',
                raise_if_not_found=False
            )
            if template:
                template.send_mail(rec.id, force_send=True)

    def action_done(self):
        """Approved → Done."""
        self.write({'state': 'done'})

    def action_cancel(self):
        """Bất kỳ state → Cancelled."""
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        """Cancelled → Draft."""
        self.write({'state': 'draft'})

    # ── Cron: Nhắc deadline ───────────────────────────────────
    @api.model
    def action_send_deadline_reminder(self):
        """Gọi bởi cron job mỗi ngày.
        Gửi email nhắc những request sắp đến deadline ngày mai.
        """
        from datetime import timedelta
        today = fields.Datetime.now()
        tomorrow_start = today.replace(
            hour=0, minute=0, second=0, microsecond=0
        ) + timedelta(days=1)
        tomorrow_end = tomorrow_start + timedelta(days=1)

        records = self.search([
            ('state', 'not in', ['done', 'cancelled']),
            ('deadline', '>=', tomorrow_start),
            ('deadline', '<', tomorrow_end),
        ])
        template = self.env.ref(
            'service_request_management.email_template_deadline_reminder',
            raise_if_not_found=False
        )
        if template:
            for rec in records:
                template.send_mail(rec.id, force_send=True)
```

> **Lưu ý quan trọng:**  
> - `@api.model_create_multi` là cú pháp chuẩn Odoo 17 (thay cho `@api.model` + `create`)  
> - `self.env.ref('service_request_management.email_template_submit')` — phần `service_request_management` là **technical name** của module, kiểm tra lại trong `__manifest__.py`

---

## BƯỚC 2 — Tạo Sequence (`data/sequence.xml`)

> **Tại sao:** Cần khai báo `ir.sequence` để hàm `next_by_code('service.request')` ở bước 1 trả về mã SR0001, SR0002...

**Tạo file mới:** `data/sequence.xml`

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

> **Kết quả:** Record đầu tiên sẽ có mã `SR0001`, tiếp theo `SR0002`...

---

## BƯỚC 3 — Tạo Email Templates (`data/email_templates.xml`)

> **Tại sao:** Odoo gửi email thông qua `mail.template`. Cần định nghĩa sẵn nội dung email cho sự kiện Submit, Approved, và nhắc Deadline.

**Tạo file mới:** `data/email_templates.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>

    <!-- ① Email khi Submit -->
    <record id="email_template_submit" model="mail.template">
        <field name="name">Service Request: Submitted</field>
        <field name="model_id" ref="model_service_request"/>
        <field name="subject">[Service Request] {{ object.name }} đã được tạo</field>
        <field name="email_to">{{ object.customer_id.email }}</field>
        <field name="email_from">{{ user.email }}</field>
        <field name="body_html" type="html">
            <p>Xin chào <strong>{{ object.customer_id.name }}</strong>,</p>
            <p>Yêu cầu dịch vụ của bạn đã được tiếp nhận thành công.</p>
            <table style="width:100%; border-collapse:collapse;">
                <tr>
                    <td style="padding:4px; font-weight:bold;">Mã yêu cầu:</td>
                    <td style="padding:4px;">{{ object.name }}</td>
                </tr>
                <tr>
                    <td style="padding:4px; font-weight:bold;">Loại dịch vụ:</td>
                    <td style="padding:4px;">{{ object.service_type }}</td>
                </tr>
                <tr>
                    <td style="padding:4px; font-weight:bold;">Ngày yêu cầu:</td>
                    <td style="padding:4px;">{{ object.request_date }}</td>
                </tr>
                <tr>
                    <td style="padding:4px; font-weight:bold;">Deadline:</td>
                    <td style="padding:4px;">{{ object.deadline or 'Chưa xác định' }}</td>
                </tr>
            </table>
            <p>Trân trọng,<br/>{{ user.name }}</p>
        </field>
        <field name="auto_delete" eval="True"/>
    </record>

    <!-- ② Email khi Approved -->
    <record id="email_template_approved" model="mail.template">
        <field name="name">Service Request: Approved</field>
        <field name="model_id" ref="model_service_request"/>
        <field name="subject">[Service Request] {{ object.name }} đã được phê duyệt</field>
        <field name="email_to">{{ object.customer_id.email }}</field>
        <field name="email_from">{{ user.email }}</field>
        <field name="body_html" type="html">
            <p>Xin chào <strong>{{ object.customer_id.name }}</strong>,</p>
            <p>Yêu cầu dịch vụ <strong>{{ object.name }}</strong> đã được phê duyệt.</p>
            <table style="width:100%; border-collapse:collapse;">
                <tr>
                    <td style="padding:4px; font-weight:bold;">Người phụ trách:</td>
                    <td style="padding:4px;">{{ object.assigned_to.name }}</td>
                </tr>
                <tr>
                    <td style="padding:4px; font-weight:bold;">Deadline:</td>
                    <td style="padding:4px;">{{ object.deadline or 'Chưa xác định' }}</td>
                </tr>
                <tr>
                    <td style="padding:4px; font-weight:bold;">Chi phí dự kiến:</td>
                    <td style="padding:4px;">{{ object.amount_estimate }}</td>
                </tr>
            </table>
            <p>Trân trọng,<br/>{{ user.name }}</p>
        </field>
        <field name="auto_delete" eval="True"/>
    </record>

    <!-- ③ Email nhắc Deadline (dùng bởi Cron) -->
    <record id="email_template_deadline_reminder" model="mail.template">
        <field name="name">Service Request: Deadline Reminder</field>
        <field name="model_id" ref="model_service_request"/>
        <field name="subject">[Nhắc nhở] Yêu cầu {{ object.name }} sắp đến hạn!</field>
        <field name="email_to">{{ object.assigned_to.email or object.customer_id.email }}</field>
        <field name="email_from">{{ user.email }}</field>
        <field name="body_html" type="html">
            <p>Xin chào,</p>
            <p>Bạn có 1 yêu cầu dịch vụ sắp đến hạn vào ngày mai:</p>
            <table style="width:100%; border-collapse:collapse;">
                <tr>
                    <td style="padding:4px; font-weight:bold;">Mã yêu cầu:</td>
                    <td style="padding:4px;">{{ object.name }}</td>
                </tr>
                <tr>
                    <td style="padding:4px; font-weight:bold;">Khách hàng:</td>
                    <td style="padding:4px;">{{ object.customer_id.name }}</td>
                </tr>
                <tr>
                    <td style="padding:4px; font-weight:bold;">Deadline:</td>
                    <td style="padding:4px;">{{ object.deadline }}</td>
                </tr>
                <tr>
                    <td style="padding:4px; font-weight:bold;">Trạng thái:</td>
                    <td style="padding:4px;">{{ object.state }}</td>
                </tr>
            </table>
            <p>Vui lòng xử lý kịp thời!</p>
        </field>
        <field name="auto_delete" eval="True"/>
    </record>

</odoo>
```

---

## BƯỚC 4 — Tạo Cron Job (`data/cron.xml`)

> **Tại sao:** Scheduled action tự động gọi method `action_send_deadline_reminder()` mỗi ngày mà không cần thao tác thủ công.

**Tạo file mới:** `data/cron.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="cron_deadline_reminder" model="ir.cron">
        <field name="name">Service Request: Nhắc Deadline</field>
        <field name="model_id" ref="model_service_request"/>
        <field name="state">code</field>
        <field name="code">
model.action_send_deadline_reminder()
        </field>
        <field name="interval_number">1</field>
        <field name="interval_type">days</field>
        <field name="numbercall">-1</field>
        <field name="active" eval="True"/>
    </record>
</odoo>
```

---

## BƯỚC 5 — Tạo Views (`views/service_request_views.xml`)

> **Tại sao:** Đây là giao diện người dùng — tree list, form nhập liệu, search filter, và menu App.

**Tạo file mới:** `views/service_request_views.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>

    <!-- ① TREE VIEW -->
    <record id="view_service_request_tree" model="ir.ui.view">
        <field name="name">service.request.tree</field>
        <field name="model">service.request</field>
        <field name="arch" type="xml">
            <tree string="Yêu cầu dịch vụ" decoration-info="state=='draft'"
                  decoration-warning="state=='submitted'"
                  decoration-success="state=='done'"
                  decoration-danger="state=='cancelled'">
                <field name="name"/>
                <field name="customer_id"/>
                <field name="service_type"/>
                <field name="assigned_to"/>
                <field name="deadline"/>
                <field name="state" widget="badge"
                       decoration-info="state=='draft'"
                       decoration-warning="state=='submitted'"
                       decoration-primary="state=='approved'"
                       decoration-success="state=='done'"
                       decoration-danger="state=='cancelled'"/>
            </tree>
        </field>
    </record>

    <!-- ② FORM VIEW -->
    <record id="view_service_request_form" model="ir.ui.view">
        <field name="name">service.request.form</field>
        <field name="model">service.request</field>
        <field name="arch" type="xml">
            <form string="Yêu cầu dịch vụ">
                <header>
                    <!-- Buttons workflow -->
                    <button name="action_submit" string="Gửi yêu cầu"
                            type="object" class="btn-primary"
                            invisible="state != 'draft'"/>
                    <button name="action_approve" string="Phê duyệt"
                            type="object" class="btn-primary"
                            invisible="state != 'submitted'"
                            groups="service_request_management.group_service_request_manager"/>
                    <button name="action_done" string="Hoàn thành"
                            type="object" class="btn-success"
                            invisible="state != 'approved'"/>
                    <button name="action_cancel" string="Hủy"
                            type="object" class="btn-danger"
                            invisible="state in ('done', 'cancelled')"/>
                    <button name="action_reset_draft" string="Đặt lại nháp"
                            type="object"
                            invisible="state != 'cancelled'"/>
                    <!-- Status Bar -->
                    <field name="state" widget="statusbar"
                           statusbar_visible="draft,submitted,approved,done"/>
                </header>
                <sheet>
                    <div class="oe_title">
                        <h1>
                            <field name="name" readonly="1"/>
                        </h1>
                    </div>
                    <!-- Nhóm 1: Thông tin khách hàng & dịch vụ -->
                    <group string="Thông tin yêu cầu">
                        <group>
                            <field name="customer_id"/>
                            <field name="service_type"/>
                            <field name="request_date"/>
                        </group>
                        <group>
                            <field name="assigned_to"/>
                            <field name="deadline"/>
                            <field name="amount_estimate"/>
                        </group>
                    </group>
                    <!-- Nhóm 2: Mô tả & ghi chú -->
                    <group string="Chi tiết">
                        <field name="description" colspan="2"
                               placeholder="Mô tả yêu cầu dịch vụ..."/>
                        <field name="note" colspan="2"
                               placeholder="Ghi chú thêm..."/>
                    </group>
                </sheet>
                <!-- Chatter -->
                <div class="oe_chatter">
                    <field name="message_follower_ids"/>
                    <field name="activity_ids"/>
                    <field name="message_ids"/>
                </div>
            </form>
        </field>
    </record>

    <!-- ③ SEARCH VIEW -->
    <record id="view_service_request_search" model="ir.ui.view">
        <field name="name">service.request.search</field>
        <field name="model">service.request</field>
        <field name="arch" type="xml">
            <search string="Tìm kiếm yêu cầu">
                <field name="name" string="Mã yêu cầu"/>
                <field name="customer_id"/>
                <field name="assigned_to"/>
                <!-- Filters -->
                <filter string="Nháp" name="draft" domain="[('state','=','draft')]"/>
                <filter string="Đã gửi" name="submitted" domain="[('state','=','submitted')]"/>
                <filter string="Đã duyệt" name="approved" domain="[('state','=','approved')]"/>
                <filter string="Hoàn thành" name="done" domain="[('state','=','done')]"/>
                <separator/>
                <filter string="Của tôi" name="my_requests"
                        domain="[('assigned_to','=',uid)]"/>
                <!-- Group By -->
                <group expand="0" string="Nhóm theo">
                    <filter string="Trạng thái" name="group_state"
                            context="{'group_by': 'state'}"/>
                    <filter string="Loại dịch vụ" name="group_service_type"
                            context="{'group_by': 'service_type'}"/>
                </group>
            </search>
        </field>
    </record>

    <!-- ④ ACTION -->
    <record id="action_service_request" model="ir.actions.act_window">
        <field name="name">Yêu cầu dịch vụ</field>
        <field name="res_model">service.request</field>
        <field name="view_mode">tree,form</field>
        <field name="context">{}</field>
        <field name="help" type="html">
            <p class="o_view_nocontent_smiling_face">
                Tạo yêu cầu dịch vụ đầu tiên!
            </p>
        </field>
    </record>

    <!-- ⑤ MENU -->
    <!-- Menu gốc (App) -->
    <menuitem id="menu_service_request_root"
              name="Dịch vụ"
              sequence="10"
              web_icon="service_request_management,static/description/icon.png"
              groups="service_request_management.group_service_request_user"/>

    <!-- Menu cấp 2 -->
    <menuitem id="menu_service_request_main"
              name="Yêu cầu dịch vụ"
              parent="menu_service_request_root"
              sequence="1"
              action="action_service_request"/>
</record>

</odoo>
```

> **Lưu ý:** Phần `web_icon` trỏ đến file icon. Nếu chưa có, bỏ dòng đó hoặc tạo thư mục `static/description/` và đặt file `icon.png` vào.

---

## BƯỚC 6 — Tạo PDF Report

### 6a. Report Action (`report/report_action.xml`)

> **Tại sao:** Khai báo report để Odoo biết dùng template nào khi bấm nút "In".

**Tạo file mới:** `report/report_action.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="action_report_service_request" model="ir.actions.report">
        <field name="name">Service Request Report</field>
        <field name="model">service.request</field>
        <field name="report_type">qweb-pdf</field>
        <field name="report_name">service_request_management.report_service_request_document</field>
        <field name="report_file">service_request_management.report_service_request_document</field>
        <field name="binding_model_id" ref="model_service_request"/>
        <field name="binding_type">report</field>
    </record>
</odoo>
```

### 6b. Template QWeb (`report/service_request_report.xml`)

> **Tại sao:** Đây là nội dung HTML thực tế sẽ render thành PDF.

**Tạo file mới:** `report/service_request_report.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <template id="report_service_request_document">
        <t t-call="web.html_container">
            <t t-foreach="docs" t-as="o">
                <t t-call="web.external_layout">
                    <div class="page">
                        <!-- Tiêu đề -->
                        <div class="row">
                            <div class="col-12">
                                <h2 style="text-align:center; color:#875A7B;">
                                    PHIẾU YÊU CẦU DỊCH VỤ
                                </h2>
                                <hr/>
                            </div>
                        </div>

                        <!-- Thông tin chính -->
                        <div class="row mt-4">
                            <div class="col-6">
                                <table class="table table-borderless">
                                    <tr>
                                        <td><strong>Mã yêu cầu:</strong></td>
                                        <td><t t-esc="o.name"/></td>
                                    </tr>
                                    <tr>
                                        <td><strong>Khách hàng:</strong></td>
                                        <td><t t-esc="o.customer_id.name"/></td>
                                    </tr>
                                    <tr>
                                        <td><strong>Loại dịch vụ:</strong></td>
                                        <td>
                                            <t t-if="o.service_type == 'repair'">Sửa chữa</t>
                                            <t t-elif="o.service_type == 'consulting'">Tư vấn</t>
                                            <t t-else="">Lắp đặt</t>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td><strong>Ngày yêu cầu:</strong></td>
                                        <td>
                                            <t t-esc="o.request_date"
                                               t-options='{"widget": "datetime"}'/>
                                        </td>
                                    </tr>
                                </table>
                            </div>
                            <div class="col-6">
                                <table class="table table-borderless">
                                    <tr>
                                        <td><strong>Người phụ trách:</strong></td>
                                        <td><t t-esc="o.assigned_to.name or '---'"/></td>
                                    </tr>
                                    <tr>
                                        <td><strong>Deadline:</strong></td>
                                        <td>
                                            <t t-if="o.deadline">
                                                <t t-esc="o.deadline"
                                                   t-options='{"widget": "datetime"}'/>
                                            </t>
                                            <t t-else="">Chưa xác định</t>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td><strong>Chi phí dự kiến:</strong></td>
                                        <td>
                                            <t t-esc="o.amount_estimate"
                                               t-options='{"widget": "monetary", "display_currency": o.env.company.currency_id}'/>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td><strong>Trạng thái:</strong></td>
                                        <td><t t-esc="o.state"/></td>
                                    </tr>
                                </table>
                            </div>
                        </div>

                        <!-- Mô tả -->
                        <div class="row mt-3">
                            <div class="col-12">
                                <h5>Mô tả yêu cầu:</h5>
                                <p style="border:1px solid #dee2e6; padding:10px; min-height:80px;">
                                    <t t-esc="o.description or 'Không có mô tả.'"/>
                                </p>
                            </div>
                        </div>

                        <!-- Ghi chú -->
                        <t t-if="o.note">
                            <div class="row mt-2">
                                <div class="col-12">
                                    <h5>Ghi chú:</h5>
                                    <p style="border:1px solid #dee2e6; padding:10px;">
                                        <t t-esc="o.note"/>
                                    </p>
                                </div>
                            </div>
                        </t>

                        <!-- Chữ ký -->
                        <div class="row mt-5">
                            <div class="col-6 text-center">
                                <p><strong>Người yêu cầu</strong></p>
                                <br/><br/><br/>
                                <p>........................</p>
                            </div>
                            <div class="col-6 text-center">
                                <p><strong>Người phụ trách</strong></p>
                                <br/><br/><br/>
                                <p>........................</p>
                            </div>
                        </div>
                    </div>
                </t>
            </t>
        </t>
    </template>
</odoo>
```

---

## BƯỚC 7 — Cập nhật Manifest (`__manifest__.py`)

> **Tại sao:** Odoo chỉ load các file được khai báo trong `data`. **Thứ tự rất quan trọng** — security phải trước, email template phải trước cron.

**Mở file:** `__manifest__.py`  
**Thay toàn bộ** bằng:

```python
{
    'name': 'Service Request Management',
    'version': '17.0.1.0.0',
    'summary': 'Module quản lý yêu cầu dịch vụ nội bộ',
    'category': 'Services',
    'author': 'Zungg',
    'depends': ['base', 'mail'],
    'data': [
        # 1. Security (luôn load đầu tiên)
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'security/record_rules.xml',
        # 2. Data
        'data/sequence.xml',
        'data/email_templates.xml',
        # 3. Views
        'views/service_request_views.xml',
        # 4. Reports
        'report/report_action.xml',
        'report/service_request_report.xml',
        # 5. Cron (load cuối cùng, sau email templates)
        'data/cron.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
```

---

## BƯỚC 8 — Kiểm tra & Cài đặt

### 8.1 Restart Odoo và Update module

Chạy lệnh trong terminal (thay đường dẫn phù hợp):

```bash
# Linux/Mac
python odoo-bin -d <tên_database> -u service_request_management --stop-after-init

# Windows (PowerShell)
python odoo-bin -d <tên_database> -u service_request_management --stop-after-init
```

Hoặc vào **Settings → Apps → Tìm "Service Request" → Upgrade**.

### 8.2 Checklist kiểm tra

| # | Kiểm tra | Cách test |
|---|---|---|
| 1 | Menu "Dịch vụ" xuất hiện | Vào Apps, refresh trang |
| 2 | Tạo record → mã tự sinh SR0001 | Tạo record mới |
| 3 | Submit không có customer → lỗi | Bỏ trống customer, bấm Submit |
| 4 | Approve không có assigned_to → lỗi | Bỏ trống assigned_to, bấm Approve |
| 5 | Nút "Hủy" hiện ở mọi state | Kiểm tra từng state |
| 6 | In PDF → có nội dung | Bấm Print → Service Request Report |
| 7 | Chatter ghi lại thay đổi state | Kiểm tra tab Log notes |

---

## Các lỗi thường gặp & cách fix

| Lỗi | Nguyên nhân | Cách fix |
|---|---|---|
| `External ID not found` | `env.ref()` không tìm thấy XML ID | Kiểm tra tên module trong `env.ref('MODULE.xml_id')` |
| `ir.sequence` không tìm thấy | File `sequence.xml` chưa được load | Kiểm tra `__manifest__.py` |
| Menu không hiện | `groups=` trỏ sai XML ID | Kiểm tra `group_service_request_user` trong `res_groups.xml` |
| Report lỗi | `report_name` không khớp `id` của template | `report_name` phải là `module.template_id` |
| Thứ tự buttons sai | `invisible=` điều kiện sai | Debug bằng cách xem `state` thực tế trong form |
