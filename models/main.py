from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ServiceRequest(models.Model):
    _name = 'service.request'
    _description = 'Service Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

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

