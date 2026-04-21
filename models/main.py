from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ServiceRequest(models.Model):
    _name = 'service.request'
    _description = 'Service Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(string='Request Code', required=True, copy=False, readonly=True, default='New')
    customer_id = fields.Many2one('res.partner', string='Customer', tracking=True)
    service_type = fields.Selection([
        ('repair', 'Repair'),
        ('consulting', 'Consulting'),
        ('installation', 'Installation'),
    ], string='Service Type', required=True, tracking=True)
    description = fields.Text(string='Description')
    request_date = fields.Datetime(string='Request Date', default=fields.Datetime.now, tracking=True)
    deadline = fields.Datetime(string='Deadline', tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    assigned_to = fields.Many2one('res.users', string='Assigned To', tracking=True)
    amount_estimate = fields.Float(string='Estimated Amount', tracking=True)
    note = fields.Text(string='Note')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('service.request') or 'New'
        return super().create(vals_list)

    def action_submit(self):
        for rec in self:
            if not rec.customer_id:
                raise ValidationError('Please select a Customer before submitting!')
            rec.state = 'submitted'
            rec._send_notification('service_request_managemen.email_template_submit')

    def action_approve(self):
        for rec in self:
            if not rec.assigned_to:
                raise ValidationError('Please assign a person before approving this request!')
            rec.state = 'approved'
            rec._send_notification('service_request_managemen.email_template_approved')

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})

    def action_reopen(self):
        """ Reopen a completed request """
        for rec in self:
            rec.state = 'draft'
            rec.message_post(body="Request has been reopened for editing.")

    @api.model
    def action_send_deadline_reminder(self):
        """ Daily cron reminder logic """
        from datetime import timedelta
        today = fields.Datetime.now()
        tomorrow = today + timedelta(days=1)

        records = self.search([
            ('state', 'not in', ['done', 'cancelled']),
            ('deadline', '!=', False),
            ('deadline', '<=', tomorrow),
            ('deadline', '>', today),
        ])

        for rec in records:
            rec._send_notification('service_request_managemen.email_template_deadline_reminder')

    def _send_notification(self, template_xml_id):
        template = self.env.ref(template_xml_id, raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)
