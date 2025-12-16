from odoo import models, fields, api, _


class ConcreteDriver(models.Model):
    _name = 'concrete.driver'
    _description = 'Concrete Mixer Driver'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='Driver Name', required=True, tracking=True, index=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', tracking=True)
    license_number = fields.Char(string='License Number', tracking=True)
    license_expiry = fields.Date(string='License Expiry', tracking=True)
    phone = fields.Char(string='Phone', tracking=True)
    email = fields.Char(string='Email')
    state = fields.Selection([
        ('active', 'Active'),
        ('on_leave', 'On Leave'),
        ('inactive', 'Inactive')
    ], string='Status', default='active', required=True, tracking=True)
    vehicle_id = fields.Many2one('concrete.vehicle', string='Assigned Vehicle', tracking=True)
    performance_rating = fields.Selection([
        ('bad', 'Bad'),
        ('fair', 'Fair'),
        ('good', 'Good'),
        ('excellent', 'Excellent')
    ], string='Performance Rating')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    ticket_count = fields.Integer(string='Tickets', compute='_compute_ticket_count')

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            self.name = self.employee_id.name
            self.phone = self.employee_id.work_phone

    def _compute_ticket_count(self):
        for record in self:
            record.ticket_count = self.env['concrete.delivery.ticket'].search_count([('driver_id', '=', record.id)])

    def action_view_tickets(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Delivery Tickets'),
            'res_model': 'concrete.delivery.ticket',
            'view_mode': 'list,form',
            'domain': [('driver_id', '=', self.id)],
            'context': {'default_driver_id': self.id}
        }
