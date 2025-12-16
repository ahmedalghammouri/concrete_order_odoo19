# -*- coding: utf-8 -*-
from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    ticket_count = fields.Integer(compute='_compute_ticket_data')
    total_volume_delivered = fields.Float(compute='_compute_ticket_data', string='Total Volume Delivered')
    total_volume_display = fields.Char(compute='_compute_ticket_data', string='Volume Display')

    def _compute_ticket_data(self):
        for picking in self:
            tickets = self.env['concrete.delivery.ticket'].search([('delivery_id', '=', picking.id)])
            picking.ticket_count = len(tickets)
            picking.total_volume_delivered = sum(tickets.mapped('volume_m3'))
            picking.total_volume_display = f"{picking.total_volume_delivered:.2f} M³"

    def action_view_delivery_tickets(self):
        self.ensure_one()
        context = {
            'default_customer_id': self.partner_id.id,
            'default_delivery_id': self.id,
            'create': True
        }
        return {
            'name': 'Delivery Tickets',
            'type': 'ir.actions.act_window',
            'res_model': 'concrete.delivery.ticket',
            'view_mode': 'list,form',
            'domain': [('delivery_id', '=', self.id)],
            'context': context
        }
