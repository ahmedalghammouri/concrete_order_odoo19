# -*- coding: utf-8 -*-
from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    ticket_ids = fields.One2many('concrete.delivery.ticket', 'sale_line_id', string='Delivery Tickets')
    total_delivered_volume = fields.Float(string='Total Delivered (M³)', compute='_compute_total_delivered_volume', store=True)
    
    @api.depends('ticket_ids.volume_m3', 'ticket_ids.state')
    def _compute_total_delivered_volume(self):
        for line in self:
            done_tickets = line.ticket_ids.filtered(lambda t: t.state == 'done')
            line.total_delivered_volume = sum(done_tickets.mapped('volume_m3'))
