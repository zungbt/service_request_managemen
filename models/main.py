from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date 

class ServiceRequest(models.Model):
    _name = 'service.request'
    _description = 'Service Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'


    name = fields.Char(string='Request Code', required=True, copy=False, readonly=True, default='New')
    customer_id = fields.Many2one('res.partner', string='Customer', tracking=True)
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
    note = fields.Text(string='Note')

    request_line_ids = fields.One2many(
        'service.request.line',
        'request_id',
        string='Request Lines',
        copy=True,
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
    )

    amount_untaxed = fields.Monetary(
        string='Untaxed Amount',
        store=True,
        compute='_amount_all',
        tracking=True,
    )
    amount_tax = fields.Monetary(
        string='Taxes',
        store=True,
        compute='_amount_all',
        tracking=True,
    )
    amount_total = fields.Monetary(
        string='Total',
        store=True,
        compute='_amount_all',
        tracking=True,
    )
    @api.onchange('deadline')
    def _onchange_deadline(self):
        today = date.today()
        if self.deadline and self.deadline < fields.Datetime.now():
            return {
                'warning' : {
                    'title' : "Cảnh báo",
                    'message': " Deadline đã qua .Bạn có chắc đặt ngày này ?"
                }
            }
            


    @api.depends('request_line_ids.price_subtotal')
    def _amount_all(self):
        for rec in self:
            untaxed = sum(line.price_subtotal for line in rec.request_line_ids)
            tax = untaxed * 0.01
            rec.update({
                'amount_untaxed': untaxed,
                'amount_tax': tax,
                'amount_total': untaxed + tax,
            })

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
        """ Reopen a completed request using a wizard """
        return {
            'name': 'Reason to Reopen',
            'type': 'ir.actions.act_window',
            'res_model': 'service.request.reopen.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_request_id': self.id},
        }
    
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

            # Create a 'To Do' activity if it doesn't exist yet
            existing_activities = rec.activity_ids.filtered(lambda a: a.summary == 'Deadline Reminder')
            if not existing_activities and rec.assigned_to:
                rec.activity_schedule(
                    'mail.mail_activity_data_todo',
                    user_id=rec.assigned_to.id,
                    summary='Deadline Reminder',
                    note='This service request is nearing its deadline. Please check and complete it!'
                )

    def _send_notification(self, template_xml_id):
        template = self.env.ref(template_xml_id, raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)
