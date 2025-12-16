from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ConcreteVehicle(models.Model):
    _name = 'concrete.vehicle'
    _description = 'Concrete Mixer Vehicle'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='Vehicle', compute='_compute_vehicle_name', store=True)
    license_plate = fields.Char(string='License Plate', required=True, tracking=True, index=True)
    model_id = fields.Many2one('concrete.vehicle.model', string='Model', tracking=True)
    vin_sn = fields.Char(string='Chassis Number', tracking=True)
    driver_id = fields.Many2one('concrete.driver', string='Current Driver', tracking=True)
    state = fields.Selection([
        ('active', 'Active'),
        ('maintenance', 'Maintenance'),
        ('inactive', 'Inactive')
    ], string='Status', default='active', required=True, tracking=True)
    capacity_m3 = fields.Float(string='Capacity (M³)', tracking=True)
    trailer_plate = fields.Char(string='Trailer Plate')
    has_pump = fields.Boolean(string='Has Pump')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    ticket_count = fields.Integer(string='Tickets', compute='_compute_ticket_count')

    _sql_constraints = [
        ('license_plate_unique', 'unique(license_plate)', 'License plate must be unique!')
    ]

    @api.depends('model_id', 'license_plate')
    def _compute_vehicle_name(self):
        for record in self:
            if record.model_id and record.license_plate:
                record.name = f'{record.model_id.name} / {record.license_plate}'
            elif record.license_plate:
                record.name = record.license_plate
            else:
                record.name = _('New Vehicle')

    def _compute_ticket_count(self):
        for record in self:
            record.ticket_count = self.env['concrete.delivery.ticket'].search_count([('vehicle_id', '=', record.id)])

    def action_view_tickets(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Delivery Tickets'),
            'res_model': 'concrete.delivery.ticket',
            'view_mode': 'list,form',
            'domain': [('vehicle_id', '=', self.id)],
            'context': {'default_vehicle_id': self.id}
        }


class ConcreteVehicleModel(models.Model):
    _name = 'concrete.vehicle.model'
    _description = 'Concrete Vehicle Model'
    _order = 'name'

    name = fields.Char(string='Model', required=True)
    brand_id = fields.Many2one('concrete.vehicle.brand', string='Brand')
    vehicle_type = fields.Selection([
        ('mixer', 'Concrete Mixer'),
        ('pump', 'Concrete Pump'),
        ('mixer_pump', 'Mixer with Pump')
    ], string='Type', default='mixer', required=True)
    capacity_m3 = fields.Float(string='Default Capacity (M³)')

    _sql_constraints = [
        ('name_brand_unique', 'unique(name, brand_id)', 'Model name must be unique per brand!')
    ]


class ConcreteVehicleBrand(models.Model):
    _name = 'concrete.vehicle.brand'
    _description = 'Concrete Vehicle Brand'
    _order = 'name'

    name = fields.Char(string='Brand', required=True)

    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Brand name must be unique!')
    ]
