from odoo import models, fields, api


class ServiceRequestLine(models.Model):
    _name = 'service.request.line'
    _description = 'Service Request Line'

    request_id = fields.Many2one(
        'service.request',
        string='Service Request',
        ondelete='cascade',
        required=True,
    )

    product_id = fields.Many2one(
        'product.product',
        string='Product',
        domain=[('type', '=', 'service')],
    )

    service_type = fields.Selection([
        ('repair', 'Repair'),
        ('consulting', 'Consulting'),
        ('installation', 'Installation'),
    ], string='Service Type', required=True, default='installation')

    name = fields.Text(string='Description')

    quantity = fields.Float(string='Quantity', default=1.0, digits='Product Unit of Measure')

    price_unit = fields.Float(string='Unit Price', digits='Product Price', default=0.0)

    discount = fields.Float(string='Discount (%)', default=0.0)

    currency_id = fields.Many2one(
        related='request_id.currency_id',
        store=True,
        string='Currency',
        readonly=True,
    )

    price_subtotal = fields.Monetary(
        compute='_compute_amount',
        string='Subtotal',
        store=True,
    )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.get_product_multiline_description_sale()
            self.price_unit = self.product_id.lst_price
        else:
            self.price_unit = 0.0

    @api.depends('quantity', 'price_unit', 'discount')
    def _compute_amount(self):
        for line in self:
            line.price_subtotal = line.quantity * line.price_unit * (1 - line.discount / 100)
