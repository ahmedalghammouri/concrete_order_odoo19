from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json

class ConcreteDeliveryCMDP(models.Model):
    _name = 'concrete.delivery.cmdp'
    _description = 'Concrete Mixer Delivery Point Session'
    _inherit = ['mail.thread']
    _order = 'create_date desc'

    name = fields.Char(string='Session', compute='_compute_name', store=True)
    user_id = fields.Many2one('res.users', string='Operator', default=lambda self: self.env.user, required=True, tracking=True)
    state = fields.Selection([('open', 'Open'), ('closed', 'Closed')], default='open', string='Status', tracking=True)
    delivery_ids = fields.One2many('concrete.delivery.ticket', 'cmdp_session_id', string='Deliveries')
    delivery_count = fields.Integer(compute='_compute_delivery_count', string='Total Deliveries')
    start_date = fields.Datetime(string='Start Date', default=fields.Datetime.now, readonly=True)
    end_date = fields.Datetime(string='End Date', readonly=True)
    total_volume = fields.Float(string='Total Volume (M³)', compute='_compute_totals', store=True)
    completed_count = fields.Integer(string='Completed', compute='_compute_totals', store=True)
    
    @api.depends('user_id', 'create_date')
    def _compute_name(self):
        for rec in self:
            rec.name = f"{rec.user_id.name} - {fields.Datetime.now().strftime('%Y-%m-%d %H:%M')}" if rec.user_id else 'New Session'
    
    @api.depends('delivery_ids')
    def _compute_delivery_count(self):
        for rec in self:
            rec.delivery_count = len(rec.delivery_ids)
    
    @api.depends('delivery_ids.volume_m3', 'delivery_ids.state')
    def _compute_totals(self):
        for rec in self:
            rec.total_volume = sum(rec.delivery_ids.mapped('volume_m3'))
            rec.completed_count = len(rec.delivery_ids.filtered(lambda d: d.state == 'done'))
    
    def action_close_session(self):
        self.write({'state': 'closed', 'end_date': fields.Datetime.now()})
        self.message_post(body=f"Session closed. Processed {self.delivery_count} deliveries, {self.completed_count} completed.")
    
    def action_reopen_session(self):
        self.write({'state': 'open', 'end_date': False})
    
    def action_view_deliveries(self):
        return {
            'type': 'ir.actions.act_window',
            'name': f'Deliveries - {self.name}',
            'res_model': 'concrete.delivery.ticket',
            'view_mode': 'list,form',
            'domain': [('cmdp_session_id', '=', self.id)],
            'context': {'default_cmdp_session_id': self.id}
        }

class ConcreteDeliveryTicket(models.Model):
    _inherit = 'concrete.delivery.ticket'
    
    cmdp_session_id = fields.Many2one('concrete.delivery.cmdp', string='CMDP Session', ondelete='set null', tracking=True)
    barcode = fields.Char(string='Barcode', compute='_compute_barcode', store=True, index=True)
    
    @api.depends('name')
    def _compute_barcode(self):
        for rec in self:
            rec.barcode = rec.name
    
    @api.model
    def create(self, vals):
        # Auto-assign to open session if accessed from CMDP interface
        if self.env.context.get('from_cmdp_interface'):
            open_session = self.env['concrete.delivery.cmdp'].search([('user_id', '=', self.env.uid), ('state', '=', 'open')], limit=1)
            if open_session:
                vals['cmdp_session_id'] = open_session.id
        return super().create(vals)
    
    def action_quick_dispatch(self):
        """Quick dispatch from CMDP interface"""
        self.ensure_one()
        if self.state == 'draft':
            self.action_confirm()
        if self.state == 'confirmed':
            self.action_in_transit()
        return {'type': 'ir.actions.client', 'tag': 'display_notification', 'params': {'type': 'success', 'message': f'{self.name} dispatched!', 'next': {'type': 'ir.actions.act_window_close'}}}
    
    def action_quick_complete(self):
        """Quick complete from CMDP interface"""
        self.ensure_one()
        if self.state in ['in_transit', 'delivered']:
            self.action_done()
        return {'type': 'ir.actions.client', 'tag': 'display_notification', 'params': {'type': 'success', 'message': f'{self.name} completed!', 'next': {'type': 'ir.actions.act_window_close'}}}
    
    def action_quick_deliver(self):
        """Mark as delivered from CMDP interface"""
        self.ensure_one()
        if self.state == 'in_transit':
            self.action_delivered()
        return True
    
    @api.model
    def action_scan_barcode(self, barcode):
        """Scan barcode to find delivery ticket"""
        # Try exact match first
        ticket = self.search([('barcode', '=', barcode), ('state', 'in', ['draft', 'confirmed', 'in_transit', 'delivered'])], limit=1)
        if not ticket:
            # Try name match
            ticket = self.search([('name', '=', barcode), ('state', 'in', ['draft', 'confirmed', 'in_transit', 'delivered'])], limit=1)
        if not ticket:
            raise UserError(_("No pending delivery ticket found with barcode: %s") % barcode)
        return ticket.read(['id', 'name', 'delivery_date', 'customer_id', 'site_name', 'vehicle_id', 'driver_id', 'volume_m3', 'mix_description', 'state', 'barcode', 'time_ex_plant', 'time_on_site'])[0]
    
    @api.model
    def get_pending_deliveries(self):
        """Get all pending deliveries for CMDP interface"""
        tickets = self.search([('state', 'in', ['draft', 'confirmed', 'in_transit'])], order='delivery_date desc, id desc', limit=100)
        return tickets.read(['id', 'name', 'delivery_date', 'customer_id', 'site_name', 'vehicle_id', 'driver_id', 'volume_m3', 'mix_description', 'state', 'barcode', 'time_ex_plant', 'time_on_site', 'create_date', 'write_date'])
    
    @api.model
    def get_analytics_data(self):
        """Get analytics data for dashboard"""
        today = fields.Date.today()
        
        # Today's completed
        completed_today = self.search_count([('state', '=', 'done'), ('delivery_date', '=', today)])
        
        # In progress
        in_progress = self.search_count([('state', 'in', ['draft', 'confirmed', 'in_transit'])])
        
        # Total volume today
        completed_tickets = self.search([('state', '=', 'done'), ('delivery_date', '=', today)])
        total_volume = sum(completed_tickets.mapped('volume_m3'))
        
        # State counts
        draft_count = self.search_count([('state', '=', 'draft')])
        confirmed_count = self.search_count([('state', '=', 'confirmed')])
        in_transit_count = self.search_count([('state', '=', 'in_transit')])
        
        return {
            'completed_today': completed_today,
            'in_progress': in_progress,
            'total_volume_today': total_volume,
            'draft_count': draft_count,
            'confirmed_count': confirmed_count,
            'in_transit_count': in_transit_count,
        }
