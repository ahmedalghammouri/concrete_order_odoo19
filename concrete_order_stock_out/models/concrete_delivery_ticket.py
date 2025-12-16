# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ConcreteDeliveryTicket(models.Model):
    _inherit = 'concrete.delivery.ticket'
    
    delivery_id = fields.Many2one('stock.picking', string='Delivery Order', ondelete='restrict', tracking=True, domain="[('picking_type_code', '=', 'outgoing')]")
    location_id = fields.Many2one('stock.location', string='Source Location')
    
    demand_qty = fields.Float(string='Demand Qty', compute='_compute_delivery_info', store=False)
    product_uom_name = fields.Char(string='Unit', compute='_compute_delivery_info', store=False)
    source_document = fields.Char(string='Source Document', compute='_compute_delivery_info', store=False)
    scheduled_date = fields.Datetime(string='Scheduled Date', compute='_compute_delivery_info', store=False)
    
    remaining_qty = fields.Float(string='Remaining Qty', compute='_compute_variance_info', store=False)
    variance_qty = fields.Float(string='Variance', compute='_compute_variance_info', store=False)
    variance_percent = fields.Float(string='Variance %', compute='_compute_variance_info', store=False)
    fulfillment_percent = fields.Float(string='Fulfillment %', compute='_compute_variance_info', store=False)

    def action_update_delivery(self):
        self.ensure_one()
        if self.state not in ['delivered', 'done']:
            raise UserError(_("Ticket must be in Delivered or Done state."))
        if self.volume_m3 <= 0:
            raise UserError(_("Volume must be greater than zero."))
        if not self.product_id:
            raise UserError(_("Product is required."))
        if self.delivery_id and self.delivery_id.picking_type_code == 'outgoing':
            self._update_delivery_quantity()
            self.message_post(body=_("Delivery updated: %s M³ of %s") % (self.volume_m3, self.product_id.name))
        else:
            raise UserError(_("Please select a delivery order first."))
    
    def _update_delivery_quantity(self):
        move = self.delivery_id.move_ids.filtered(lambda m: m.product_id == self.product_id)
        if not move:
            raise UserError(_("Product %s not found in delivery.") % self.product_id.name)
        
        if self.delivery_id.state == 'draft':
            self.delivery_id.action_confirm()
        if self.delivery_id.state in ['confirmed', 'waiting']:
            self.delivery_id.action_assign()
        
        if move[0].move_line_ids:
            for ml in move[0].move_line_ids:
                ml.quantity = self.volume_m3
        else:
            self.env['stock.move.line'].create({
                'move_id': move[0].id,
                'product_id': self.product_id.id,
                'product_uom_id': self.product_id.uom_id.id,
                'location_id': self.delivery_id.location_id.id,
                'location_dest_id': self.delivery_id.location_dest_id.id,
                'quantity': self.volume_m3,
                'picking_id': self.delivery_id.id,
            })
        
        demand_qty = move[0].product_uom_qty
        if self.volume_m3 > demand_qty:
            status = _("Over-delivery: +%s M³") % (self.volume_m3 - demand_qty)
        elif self.volume_m3 < demand_qty:
            status = _("Under-delivery: -%s M³") % (demand_qty - self.volume_m3)
        else:
            status = _("Exact delivery")
        
        self.delivery_id.message_post(
            body=_("Delivered: %s M³ of %s (Demand: %s M³) - %s (from ticket %s)") % 
            (self.volume_m3, self.product_id.name, demand_qty, status, self.name)
        )
    
    @api.onchange('delivery_id')
    def _onchange_delivery_id(self):
        if self.delivery_id:
            self.customer_id = self.delivery_id.partner_id
            self.location_id = self.delivery_id.location_id
            if self.delivery_id.move_ids:
                self.product_id = self.delivery_id.move_ids[0].product_id
    
    def action_view_delivery(self):
        self.ensure_one()
        return {
            'name': 'Delivery Order',
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_mode': 'form',
            'res_id': self.delivery_id.id,
        }
    
    @api.depends('delivery_id', 'product_id')
    def _compute_delivery_info(self):
        for rec in self:
            rec.demand_qty = 0.0
            rec.product_uom_name = ''
            rec.source_document = ''
            rec.scheduled_date = False
            if rec.delivery_id and rec.product_id:
                move = rec.delivery_id.move_ids.filtered(lambda m: m.product_id == rec.product_id)
                if move:
                    rec.demand_qty = move[0].product_uom_qty
                    rec.product_uom_name = move[0].product_uom.name
                else:
                    rec.product_uom_name = rec.product_id.uom_id.name if rec.product_id else ''
                rec.source_document = rec.delivery_id.origin or rec.delivery_id.name
                rec.scheduled_date = rec.delivery_id.scheduled_date
    
    @api.depends('demand_qty', 'volume_m3')
    def _compute_variance_info(self):
        for rec in self:
            rec.remaining_qty = 0.0
            rec.variance_qty = 0.0
            rec.variance_percent = 0.0
            rec.fulfillment_percent = 0.0
            if rec.demand_qty > 0 and rec.volume_m3 > 0:
                rec.remaining_qty = rec.demand_qty - rec.volume_m3
                rec.variance_qty = rec.volume_m3 - rec.demand_qty
                rec.variance_percent = rec.variance_qty / rec.demand_qty
                rec.fulfillment_percent = rec.volume_m3 / rec.demand_qty
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('delivery_id') and not vals.get('product_id'):
                delivery = self.env['stock.picking'].browse(vals['delivery_id'])
                if delivery.move_ids:
                    vals['product_id'] = delivery.move_ids[0].product_id.id
                    if not vals.get('customer_id'):
                        vals['customer_id'] = delivery.partner_id.id
                    if not vals.get('location_id'):
                        vals['location_id'] = delivery.location_id.id
        return super().create(vals_list)
