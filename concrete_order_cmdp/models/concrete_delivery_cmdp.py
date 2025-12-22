from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ConcreteDeliveryTicket(models.Model):
    _inherit = 'concrete.delivery.ticket'
    
    barcode = fields.Char(string='Barcode', compute='_compute_barcode', store=True, index=True)
    
    @api.depends('name')
    def _compute_barcode(self):
        for rec in self:
            rec.barcode = rec.name
    
    def action_quick_dispatch(self):
        self.ensure_one()
        if self.state == 'draft':
            self.action_confirm()
        if self.state == 'confirmed':
            self.action_in_transit()
        return True
    
    def action_quick_complete(self):
        self.ensure_one()
        if self.state in ['in_transit', 'delivered']:
            if self.delivery_id:
                self.action_update_delivery()
            self.action_done()
        return True
    
    def action_quick_deliver(self):
        self.ensure_one()
        if self.state == 'in_transit':
            self.action_delivered()
        return True
    
    @api.model
    def action_scan_barcode(self, barcode):
        ticket = self.search([('barcode', '=', barcode), ('state', 'in', ['draft', 'confirmed', 'in_transit', 'delivered'])], limit=1)
        if not ticket:
            ticket = self.search([('name', '=', barcode), ('state', 'in', ['draft', 'confirmed', 'in_transit', 'delivered'])], limit=1)
        if not ticket:
            raise UserError(_("No pending delivery ticket found with barcode: %s") % barcode)
        return ticket.read(['id', 'name', 'delivery_date', 'customer_id', 'site_name', 'vehicle_id', 'driver_id', 'volume_m3', 'mix_description', 'state', 'barcode', 'time_ex_plant', 'time_on_site', 'delivery_id'])[0]
    
    @api.model
    def get_pending_deliveries(self):
        tickets = self.search([('state', 'in', ['draft', 'confirmed', 'in_transit'])], order='delivery_date desc, id desc', limit=100)
        return tickets.read(['id', 'name', 'delivery_date', 'customer_id', 'site_name', 'vehicle_id', 'driver_id', 'volume_m3', 'mix_description', 'state', 'barcode', 'time_ex_plant', 'time_on_site', 'create_date', 'write_date', 'delivery_id'])
    
    @api.model
    def get_delivery_orders(self):
        pickings = self.env['stock.picking'].search([
            ('picking_type_code', '=', 'outgoing'),
            ('state', 'in', ['assigned', 'confirmed', 'waiting'])
        ], order='scheduled_date asc', limit=50)
        
        result = []
        for picking in pickings:
            # Filter out pickings with weighable products
            has_non_weighable = False
            for move in picking.move_ids:
                if move.product_id and not move.product_id.is_weighable:
                    has_non_weighable = True
                    break
            
            # Skip this picking if it doesn't have non-weighable products
            if not has_non_weighable:
                continue
            
            ticket = self.search([('delivery_id', '=', picking.id), ('state', '!=', 'cancel')], limit=1)
            
            # Determine status
            if ticket and ticket.state == 'done':
                status = 'validated'
            elif ticket:
                status = 'has_ticket'
            else:
                status = 'no_ticket'
            
            result.append({
                'id': picking.id,
                'name': picking.name,
                'partner_id': [picking.partner_id.id, picking.partner_id.name] if picking.partner_id else False,
                'scheduled_date': picking.scheduled_date.isoformat() if picking.scheduled_date else False,
                'origin': picking.origin,
                'state': picking.state,
                'status': status,
                'ticket_id': ticket.id if ticket else False,
            })
        return result
    
    @api.model
    def create_from_delivery(self, delivery_id):
        delivery = self.env['stock.picking'].browse(delivery_id)
        if not delivery:
            raise UserError(_("Delivery order not found"))
        
        existing = self.search([('delivery_id', '=', delivery_id), ('state', '!=', 'cancel')], limit=1)
        if existing:
            return existing.read(['id', 'name', 'delivery_date', 'customer_id', 'site_name', 'vehicle_id', 'driver_id', 'volume_m3', 'mix_description', 'state', 'barcode', 'delivery_id'])[0]
        
        # Open wizard to select vehicle
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Delivery Ticket',
            'res_model': 'concrete.delivery.wizard',
            'view_mode': 'form',
            'views': [(False, 'form')],
            'target': 'new',
            'context': {'default_delivery_id': delivery_id}
        }
    
    @api.model
    def get_fleet_queue(self):
        tickets = self.search([
            ('state', 'in', ['draft', 'confirmed', 'in_transit']),
            ('vehicle_id', '!=', False)
        ], order='time_ex_plant asc, create_date asc', limit=50)
        
        queue = []
        for idx, ticket in enumerate(tickets):
            wait_time = 0
            if ticket.time_ex_plant:
                wait_time = int((fields.Datetime.now() - ticket.time_ex_plant).total_seconds() / 60)
            elif ticket.create_date:
                wait_time = int((fields.Datetime.now() - ticket.create_date).total_seconds() / 60)
            
            queue.append({
                'id': ticket.id,
                'position': idx + 1,
                'name': ticket.name,
                'vehicle': ticket.vehicle_id.license_plate if ticket.vehicle_id else 'N/A',
                'driver': ticket.driver_id.name if ticket.driver_id else 'N/A',
                'state': ticket.state,
                'wait_time': wait_time,
                'estimated_wait': (idx + 1) * 15,
                'is_urgent': wait_time > 45,
                'customer': ticket.customer_id.name if ticket.customer_id else '',
                'volume': ticket.volume_m3,
            })
        return queue
