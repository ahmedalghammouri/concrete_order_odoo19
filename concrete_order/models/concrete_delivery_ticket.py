from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import json


class ConcreteDeliveryTicket(models.Model):
    _name = 'concrete.delivery.ticket'
    _description = 'Concrete Delivery Ticket'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'delivery_date desc, id desc'
    _rec_name = 'name'

    # Basic Information
    name = fields.Char(string='Ticket No.', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    ticket_serial_no = fields.Char(string='Serial No.', tracking=True, copy=False)
    delivery_date = fields.Date(string='Date', default=fields.Date.context_today, required=True, tracking=True, index=True)
    delivery_time = fields.Float(string='Time')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], string='Status', default='draft', required=True, tracking=True, copy=False, index=True)
    
    # Customer & Site Information
    customer_id = fields.Many2one('res.partner', string='Customer', domain=[('is_company', '=', True)], required=True, tracking=True, index=True)
    customer_phone = fields.Char(related='customer_id.phone', string='Customer Phone', readonly=True)
    customer_email = fields.Char(related='customer_id.email', string='Customer Email', readonly=True)
    customer_order_no = fields.Char(string='Customer Order No.')
    enquiry_form_no = fields.Char(string='Enquiry Form No.')
    delivery_to = fields.Char(string='Delivered To')
    site_no = fields.Char(string='Site No.')
    site_name = fields.Char(string='Site Name', required=True, tracking=True)
    area = fields.Char(string='Area')
    delivery_address = fields.Text(string='Delivery Address', compute='_compute_delivery_address', store=True)
    
    # Plant Information
    plant_no = fields.Char(string='Plant No.')
    plant_name = fields.Char(string='Plant Name')
    plant_batch_no = fields.Char(string='Plant Batch No.')
    
    # Mix Details
    product_id = fields.Many2one('product.product', string='Concrete Product', domain=[('type', '=', 'consu')])
    mix_description = fields.Char(string='Mix Description', required=True)
    cement_type = fields.Char(string='Cement Type/Category')
    admixture = fields.Char(string='Admixture')
    total_admixtures = fields.Char(string='Total Admixtures')
    slump_value = fields.Char(string='Slump (mm)')
    
    # Volume & Quantity
    volume_m3 = fields.Float(string='Volume (M³)', required=True, tracking=True)
    total_volume_delivered = fields.Float(string='Total Delivered this Load', compute='_compute_total_volume', store=True)
    quantity_delivered = fields.Float(string='Batched Quantities (KGs)')
    batch_size = fields.Float(string='Batch Size (m³)')
    product_uom_id = fields.Many2one('uom.uom', string='Unit of Measure', default=lambda self: self.env.ref('uom.product_uom_cubic_meter', raise_if_not_found=False))
    
    # Driver & Vehicle
    driver_id = fields.Many2one('concrete.driver', string='Driver', tracking=True, index=True)
    driver_name = fields.Char(related='driver_id.name', string='Driver Name', readonly=True, store=True)
    driver_phone = fields.Char(related='driver_id.phone', string='Driver Phone', readonly=True)
    vehicle_id = fields.Many2one('concrete.vehicle', string='Vehicle', required=True, tracking=True, index=True)
    vehicle_plate = fields.Char(related='vehicle_id.license_plate', string='License Plate', readonly=True, store=True)
    vehicle_capacity = fields.Float(related='vehicle_id.capacity_m3', string='Vehicle Capacity', readonly=True)
    driver_performance = fields.Selection([('bad', 'Bad'), ('fair', 'Fair'), ('good', 'Good'), ('excellent', 'Excellent')], string="Driver's Performance")
    
    # Time Tracking
    time_ex_plant = fields.Datetime(string='Time Ex-Plant')
    time_on_site = fields.Datetime(string='Time On Site')
    time_start_discharge = fields.Datetime(string='Time Start Discharge')
    time_finish_discharge = fields.Datetime(string='Time Finish Discharge')
    time_returned_plant = fields.Datetime(string='Time Returned Plant')
    total_time_taken = fields.Float(string='Total Time (Hours)', compute='_compute_total_time', store=True)
    discharge_duration = fields.Float(string='Discharge Duration (Hours)', compute='_compute_discharge_duration', store=True)
    is_delayed = fields.Boolean(string='Delayed', compute='_compute_is_delayed', store=True)
    max_unloading_time = fields.Float(string='Max Unloading Time (Hours)', default=0.1)
    
    # Notes & Signatures
    water_added = fields.Text(string='Water Added Note')
    delivery_note = fields.Text(string='Delivery Note/Warning')
    customer_signature_date = fields.Date(string='Customer Signature Date')
    signature_plant = fields.Binary(string='Plant Signature', attachment=True)
    signature_customer = fields.Binary(string='Customer Signature', attachment=True)
    signature_supervisor = fields.Binary(string='Site Supervisor Signature', attachment=True)
    
    # Document & Template
    template_id = fields.Many2one('excel.template', string='Excel Template', default=lambda self: self.env['excel.template'].search([('is_default', '=', True)], limit=1))
    generated_document_id = fields.Many2one('documents.document', string='Generated Document', readonly=True, copy=False)
    
    # Company & User
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, required=True)
    user_id = fields.Many2one('res.users', string='Responsible', default=lambda self: self.env.user, tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('concrete.delivery.ticket.sequence') or _('New')
        return super().create(vals_list)

    @api.depends('site_name', 'area', 'delivery_to')
    def _compute_delivery_address(self):
        for record in self:
            parts = [record.delivery_to, record.site_name, record.area]
            record.delivery_address = ', '.join(filter(None, parts))

    @api.depends('volume_m3', 'batch_size')
    def _compute_total_volume(self):
        for record in self:
            record.total_volume_delivered = record.volume_m3 or 0.0

    @api.depends('time_ex_plant', 'time_returned_plant')
    def _compute_total_time(self):
        for record in self:
            if record.time_ex_plant and record.time_returned_plant:
                if record.time_returned_plant < record.time_ex_plant:
                    record.total_time_taken = 0.0
                else:
                    delta = record.time_returned_plant - record.time_ex_plant
                    record.total_time_taken = delta.total_seconds() / 3600
            else:
                record.total_time_taken = 0.0

    @api.depends('time_start_discharge', 'time_finish_discharge')
    def _compute_discharge_duration(self):
        for record in self:
            if record.time_start_discharge and record.time_finish_discharge:
                if record.time_finish_discharge > record.time_start_discharge:
                    delta = record.time_finish_discharge - record.time_start_discharge
                    record.discharge_duration = delta.total_seconds() / 3600
                else:
                    record.discharge_duration = 0.0
            else:
                record.discharge_duration = 0.0

    @api.depends('discharge_duration', 'max_unloading_time')
    def _compute_is_delayed(self):
        for record in self:
            record.is_delayed = record.discharge_duration > record.max_unloading_time if record.max_unloading_time else False

    @api.constrains('volume_m3')
    def _check_volume(self):
        for record in self:
            if record.volume_m3 <= 0:
                raise ValidationError(_('Volume must be greater than zero.'))

    @api.constrains('time_ex_plant', 'time_returned_plant')
    def _check_time_sequence(self):
        for record in self:
            if record.time_ex_plant and record.time_returned_plant:
                if record.time_returned_plant < record.time_ex_plant:
                    raise ValidationError(_('Return time cannot be before departure time.'))

    @api.onchange('driver_id')
    def _onchange_driver_id(self):
        if self.driver_id and self.driver_id.vehicle_id:
            self.vehicle_id = self.driver_id.vehicle_id

    @api.onchange('vehicle_id')
    def _onchange_vehicle_id(self):
        if self.vehicle_id and self.vehicle_id.driver_id:
            self.driver_id = self.vehicle_id.driver_id

    def action_confirm(self):
        self.write({'state': 'confirmed', 'time_ex_plant': fields.Datetime.now()})

    def action_in_transit(self):
        self.write({'state': 'in_transit'})

    def action_delivered(self):
        self.write({'state': 'delivered', 'time_on_site': fields.Datetime.now()})

    def action_done(self):
        if not self.time_returned_plant:
            self.time_returned_plant = fields.Datetime.now()
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_generate_excel(self):
        self.ensure_one()
        if not self.template_id or not self.template_id.document_id:
            raise UserError(_('Please select an Excel template first.'))
        
        folder = self.env['documents.document'].search([('name', '=', 'Delivery Tickets'), ('type', '=', 'folder')], limit=1)
        if not folder:
            folder = self.env['documents.document'].create({'name': 'Delivery Tickets', 'type': 'folder', 'company_id': self.company_id.id})
        
        try:
            template_doc = self.template_id.document_id
            data = json.loads(template_doc.spreadsheet_data or '{}')
            
            if self.template_id.mapping_ids and data.get('sheets'):
                sheet = data['sheets'][0]
                if 'cells' not in sheet:
                    sheet['cells'] = {}
                
                for mapping in self.template_id.mapping_ids:
                    value = self[mapping.field_name]
                    if hasattr(value, 'name'):
                        value = value.name
                    sheet['cells'][mapping.cell_location] = str(value or '')
        except Exception as e:
            raise UserError(_('Error processing template: %s') % str(e))
        
        existing_doc = self.env['documents.document'].search([('name', '=', self.name), ('folder_id', '=', folder.id), ('res_model', '=', self._name), ('res_id', '=', self.id)], limit=1)
        
        if existing_doc:
            existing_doc.write({'spreadsheet_data': json.dumps(data)})
            self.generated_document_id = existing_doc
            message = _('Document "%s" updated successfully.', self.name)
        else:
            doc = self.env['documents.document'].create({
                'name': self.name,
                'folder_id': folder.id,
                'res_model': self._name,
                'res_id': self.id,
                'mimetype': 'application/o-spreadsheet',
                'handler': 'spreadsheet',
                'spreadsheet_data': json.dumps(data),
                'company_id': self.company_id.id,
            })
            self.generated_document_id = doc
            message = _('Document "%s" created successfully.', self.name)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {'type': 'success', 'message': message, 'next': {'type': 'ir.actions.act_window_close'}}
        }

    def action_open_generated_document(self):
        self.ensure_one()
        if not self.generated_document_id:
            raise UserError(_('No document generated yet. Please generate Excel first.'))
        return {'type': 'ir.actions.act_url', 'url': f'/odoo/documents/spreadsheet/{self.generated_document_id.id}', 'target': 'new'}

    def action_print_document(self):
        self.ensure_one()
        if not self.generated_document_id:
            raise UserError(_('No document generated yet. Please generate Excel first.'))
        return {'type': 'ir.actions.client', 'tag': 'action_print_spreadsheet', 'params': {'spreadsheet_id': self.generated_document_id.id}}

