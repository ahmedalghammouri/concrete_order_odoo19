# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ConcreteDeliveryTicket(models.Model):
    _inherit = 'concrete.delivery.ticket'
    
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', ondelete='restrict', tracking=True)
    sale_line_id = fields.Many2one('sale.order.line', string='Sale Order Line', ondelete='restrict', tracking=True)
    
    @api.onchange('delivery_id')
    def _onchange_delivery_id_sale(self):
        if self.delivery_id and self.delivery_id.sale_id:
            self.sale_order_id = self.delivery_id.sale_id
            if self.delivery_id.move_ids and self.delivery_id.move_ids[0].sale_line_id:
                self.sale_line_id = self.delivery_id.move_ids[0].sale_line_id
    
    @api.onchange('sale_order_id')
    def _onchange_sale_order_id(self):
        if self.sale_order_id:
            self.customer_id = self.sale_order_id.partner_id
            if self.sale_order_id.order_line:
                self.product_id = self.sale_order_id.order_line[0].product_id
                self.sale_line_id = self.sale_order_id.order_line[0]
    
    @api.onchange('sale_line_id')
    def _onchange_sale_line_id(self):
        if self.sale_line_id:
            self.product_id = self.sale_line_id.product_id
            self.volume_m3 = self.sale_line_id.product_uom_qty
    
    def action_view_sale_order(self):
        self.ensure_one()
        return {
            'name': 'Sale Order',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': self.sale_order_id.id,
        }
