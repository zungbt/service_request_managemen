from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_service_vip = fields.Boolean(string="VIP Service Customer", default=False)
    service_request_count = fields.Integer(string="Service Requests", compute="_compute_service_request_count")

    def _compute_service_request_count(self):
        for partner in self:
            # Đếm số lượng request có customer_id là partner hiện tại
            partner.service_request_count = self.env['service.request'].search_count([('customer_id', '=', partner.id)])

    def action_view_service_requests(self):
        """Action được gọi khi bấm vào Smart Button trên form Khách hàng"""
        return {
            'name': 'Service Requests',
            'type': 'ir.actions.act_window',
            'res_model': 'service.request',
            'view_mode': 'tree,form',
            'domain': [('customer_id', '=', self.id)],
            'context': {'default_customer_id': self.id},
        }
