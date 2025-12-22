from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ConcreteDeliveryWizard(models.TransientModel):
    _name = 'concrete.delivery.wizard'
    _description = 'Create Delivery Ticket Wizard'

    delivery_id = fields.Many2one('stock.picking', string='Delivery Order', required=True, readonly=True)
    sale_order_id = fields.Many2one('sale.order', string='Sale Order')
    sale_line_id = fields.Many2one('sale.order.line', string='Sale Order Line')
    location_id = fields.Many2one('stock.location', string='Source Location')
    vehicle_id = fields.Many2one('concrete.vehicle', string='Vehicle', required=True)
    driver_id = fields.Many2one('concrete.driver', string='Driver')
    mix_description = fields.Char(string='Mix Description', required=True, default='Standard Mix')
    
    @api.onchange('delivery_id')
    def _onchange_delivery_id_sale(self):
        if self.delivery_id and self.delivery_id.sale_id:
            self.sale_order_id = self.delivery_id.sale_id
            if self.delivery_id.move_ids and self.delivery_id.move_ids[0].sale_line_id:
                self.sale_line_id = self.delivery_id.move_ids[0].sale_line_id
        if self.delivery_id:
            self.location_id = self.delivery_id.location_id

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        delivery_id = self.env.context.get('delivery_id')
        if delivery_id:
            res['delivery_id'] = delivery_id
        return res
    
    @api.onchange('vehicle_id')
    def _onchange_vehicle_id(self):
        if self.vehicle_id and self.vehicle_id.driver_id:
            self.driver_id = self.vehicle_id.driver_id
    
    def action_create_ticket(self):
        self.ensure_one()
        
        # Fetch from delivery directly to ensure we have the values
        sale_order_id = False
        sale_line_id = False
        if self.delivery_id.sale_id:
            sale_order_id = self.delivery_id.sale_id.id
            if self.delivery_id.move_ids and self.delivery_id.move_ids[0].sale_line_id:
                sale_line_id = self.delivery_id.move_ids[0].sale_line_id.id
        
        vals = {
            'delivery_id': self.delivery_id.id,
            'customer_id': self.delivery_id.partner_id.id,
            'delivery_date': fields.Date.today(),
            'site_name': self.delivery_id.partner_id.name,
            'vehicle_id': self.vehicle_id.id,
            'driver_id': self.driver_id.id if self.driver_id else False,
            'mix_description': self.mix_description,
            'location_id': self.delivery_id.location_id.id if self.delivery_id.location_id else False,
        }
        
        if self.delivery_id.move_ids:
            vals['product_id'] = self.delivery_id.move_ids[0].product_id.id
            vals['volume_m3'] = self.delivery_id.move_ids[0].product_uom_qty
        
        if sale_order_id:
            vals['sale_order_id'] = sale_order_id
        if sale_line_id:
            vals['sale_line_id'] = sale_line_id
        
        ticket = self.env['concrete.delivery.ticket'].create(vals)
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'concrete.delivery.ticket',
            'res_id': ticket.id,
            'views': [(False, 'form')],
            'view_mode': 'form',
            'target': 'current',
        }
