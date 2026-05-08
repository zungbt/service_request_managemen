from odoo import models, fields, api
from odoo.exceptions import UserError

# class LaptopInventory(models.Model):
#     _name = 'laptop.inventory'
#     _description = 'Service Laptop Inventory'
#     _inherit = ['mail.thread', 'mail.activity.mixin']
#     _order = 'id desc'
#     #name/order/quantity/price/target ? => done 
#     name = fields.Char(string='Name', required=True, tracking=True)
#     quantity = fields.Integer(string="Số lượng", default=0, tracking=True)
#     buy_in_price = fields.Float(string="Giá nhập", tracking=True)
#     sale_price_default = fields.Float(string="Giá bán dự kiến", tracking=True)
#     active = fields.Boolean(string='Active',default=True)

#     @api.onchange('buy_in_price')
#     def _onchange_buy_in_price(self):
#         if self.buy_in_price:
#             # giá vốn + 10%
#             self.sale_price_default = self.buy_in_price * 1.1
#     #archine
#     def toggle_active(self):
#         for rec in self:
#             rec.active = not rec.active


class LaptopSale(models.Model):

    _name = 'laptop.sale'
    _description = 'Laptop Sales Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'
    #đủ chưa ? => done 
    name = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, default='New')
    partner_id = fields.Many2one('res.partner', string='Khách hàng', required=True, tracking=True)
    date_order = fields.Datetime(string='Ngày bán', default=fields.Datetime.now, tracking=True)
    
    sale_line_ids = fields.One2many('laptop.sale.line', 'sale_id', string='Order Lines')
    
    amount_total = fields.Float(string='Tổng cộng tiền', compute='_compute_totals', store=True, tracking=True)
    margin_total = fields.Float(string='Tổng lợi nhuận', compute='_compute_totals', store=True, tracking=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', readonly=True, tracking=True)
    #func => done ? 
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('laptop.sale') or 'New'
        return super(LaptopSale, self).create(vals)

    @api.depends('sale_line_ids.price_subtotal', 'sale_line_ids.margin_subtotal')
    def _compute_totals(self):
        for order in self:
            order.amount_total = sum(order.sale_line_ids.mapped('price_subtotal'))
            order.margin_total = sum(order.sale_line_ids.mapped('margin_subtotal'))
    def action_confirm(self):
        for order in self:
            if not order.sale_line_ids:
                raise UserError("Vui lòng thêm ít nhất một dòng máy để bán!")

            # Validate stock availability
            for line in order.sale_line_ids:
                qty_available = line.product_id.qty_available
                if qty_available < line.quantity:
                    raise UserError(
                        f"Máy {line.product_id.name} không đủ hàng "
                        f"(Hiện có: {qty_available})!"
                    )
                if line.price_unit < line.product_id.standard_price:
                    raise UserError(
                        f"Giá bán {line.product_id.name} ({line.price_unit:,.0f}) "
                        f"thấp hơn giá vốn ({line.product_id.standard_price:,.0f})!"
                    )

            # Create delivery picking
            picking_type = self.env['stock.picking.type'].search([
                ('code', '=', 'outgoing'),
                ('company_id', '=', self.env.company.id),
            ], limit=1)
            if not picking_type:
                raise UserError("Không tìm thấy loại phiếu xuất kho!")

            src_location = picking_type.default_location_src_id
            dest_location = (picking_type.default_location_dest_id
                             or self.env.ref('stock.stock_location_customers'))

            picking = self.env['stock.picking'].create({
                'picking_type_id': picking_type.id,
                'location_id': src_location.id,
                'location_dest_id': dest_location.id,
                'partner_id': order.partner_id.id,
                'origin': order.name,
            })

            for line in order.sale_line_ids:
                self.env['stock.move'].create({
                    'name': line.product_id.name,
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.quantity,
                    'product_uom': line.product_id.uom_id.id,
                    'location_id': src_location.id,
                    'location_dest_id': dest_location.id,
                    'picking_id': picking.id,
                    'company_id': self.env.company.id,
                })

            picking.action_confirm()
            picking.action_assign()
            picking.button_validate()

            order.state = 'confirmed'
            order.message_post(body="Đơn hàng đã được xác nhận. Kho đã cập nhật.")

    def action_cancel(self):
        for order in self:
            if order.state == 'confirmed':
                pickings = self.env['stock.picking'].search([
                    ('origin', '=', order.name),
                    ('state', '=', 'done'),
                ])
                pickings.action_cancel()
            order.state = 'cancelled'
            order.message_post(body="Đơn hàng đã bị hủy. Hàng đã được hoàn kho.")

    def action_draft(self):
        for order in self:
            order.state = 'draft'

class LaptopSaleLine(models.Model):
    _name = 'laptop.sale.line'
    _description = 'Laptop Sale Line'
    # Đủ => done 
    sale_id = fields.Many2one('laptop.sale', string='Order Reference', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Laptop', required=True, domain=[('categ_id.name', '=', 'Laptops')])
    quantity = fields.Integer(string='Số lượng', default=1)
    price_unit = fields.Float(string='Đơn giá')
    
    price_subtotal = fields.Float(string='Thành tiền', compute='_compute_line_totals', store=True)
    margin_subtotal = fields.Float(string='Lợi nhuận dòng', compute='_compute_line_totals', store=True)
    
    @api.depends('quantity', 'price_unit', 'product_id.standard_price')
    def _compute_line_totals(self):
        for line in self:
            line.price_subtotal = line.quantity * line.price_unit
            if line.product_id:
                line.margin_subtotal = (line.price_unit - line.product_id.standard_price) * line.quantity
            else:
                line.margin_subtotal = 0

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.price_unit = self.product_id.lst_price
