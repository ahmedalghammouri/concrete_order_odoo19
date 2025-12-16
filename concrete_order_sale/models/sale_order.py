# -*- coding: utf-8 -*-
from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    ticket_count = fields.Integer(compute='_compute_ticket_data')
    total_volume_delivered = fields.Float(compute='_compute_ticket_data', string='Total Volume Delivered')
    total_volume_display = fields.Char(compute='_compute_ticket_data', string='Volume Display')

    def _compute_ticket_data(self):
        for order in self:
            tickets = self.env['concrete.delivery.ticket'].search([('sale_order_id', '=', order.id)])
            order.ticket_count = len(tickets)
            order.total_volume_delivered = sum(tickets.mapped('volume_m3'))
            order.total_volume_display = f"{order.total_volume_delivered:.2f} M³"

    def action_view_delivery_tickets(self):
        self.ensure_one()
        context = {
            'default_customer_id': self.partner_id.id,
            'default_sale_order_id': self.id,
            'create': True
        }
        return {
            'name': 'Delivery Tickets',
            'type': 'ir.actions.act_window',
            'res_model': 'concrete.delivery.ticket',
            'view_mode': 'list,form',
            'domain': [('sale_order_id', '=', self.id)],
            'context': context
        }
