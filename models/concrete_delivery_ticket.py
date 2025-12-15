from odoo import models, fields, api
import json
import os
from datetime import datetime


class ConcreteDeliveryTicket(models.Model):
    _name = 'concrete.delivery.ticket'
    _description = 'Specialized Projects Ready Mix Concrete Delivery Ticket'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Ticket No.',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('concrete.delivery.ticket')
    )
    ticket_serial_no = fields.Char(string='Serial No.', default='90394511')
    delivery_date = fields.Date(string='Date', default=fields.Date.context_today)
    delivery_time = fields.Float(string='Time')
    customer_id = fields.Many2one('res.partner', string='Customer', domain=[('is_company', '=', True)])
    customer_order_no = fields.Char(string='Customer Order No.')
    enquiry_form_no = fields.Char(string='Enquiry Form No.')
    delivery_to = fields.Char(string='Delivered To', default='Faysaleya')
    site_no = fields.Char(string='Site No.', default='4113253')
    site_name = fields.Char(string='Site Name', default='Y5AD5YAE')
    area = fields.Char(string='Area', default='AREA')
    plant_no = fields.Char(string='Plant No.', default='002')
    plant_name = fields.Char(string='Plant Name', default='SPC Ready Mix Concrete')
    plant_batch_no = fields.Char(string='Plant Batch No.', default='002')
    mix_description = fields.Char(string='Mix Description', default='4500 PSI, 20 Cyl Str, SRC, 150±40 mm')
    cement_type = fields.Char(string='Cement Type/Category', default='M63')
    admixture = fields.Char(string='Admixture', default='1')
    total_admixtures = fields.Char(string='Total Admixtures', default='2')
    slump_value = fields.Char(string='Slump (mm)')
    volume_m3 = fields.Float(string='Volume (C.U.M)', default=11.0)
    total_volume_delivered = fields.Float(string='Total Delivered this Load', default=11.0)
    quantity_delivered = fields.Float(string='Batched Quantities (KGs)')
    batch_size = fields.Float(string='Batch Size (m³)')
    driver_id = fields.Many2one('hr.employee', string='Driver Name', domain=[('job_title', '=', 'Mixer Driver')])
    driver_name_text = fields.Char(string='Driver Name Text', default='Ganesh Bhandari - 9184')
    vehicle_no = fields.Char(string='Vehicle No.', default='M063')
    trailer_no = fields.Char(string='Trailer No.')
    pump_status = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Pump')
    time_ex_plant = fields.Datetime(string='Time Ex-Plant')
    time_on_site = fields.Datetime(string='Time On Site')
    time_start_discharge = fields.Datetime(string='Time Start Discharge')
    time_finish_discharge = fields.Datetime(string='Time Finish Discharge')
    time_returned_plant = fields.Datetime(string='Time Returned Plant')
    total_time_taken = fields.Float(string='Total Time (Hours)', compute='_compute_total_time', store=True)
    water_added = fields.Text(
        string='Water Added Note',
        default="Additional water added to this concrete mix will reduce its strength..."
    )
    driver_performance = fields.Selection(
        [('bad', 'Bad'), ('fair', 'Fair'), ('good', 'Good')],
        string="Driver's Performance"
    )
    customer_signature_date = fields.Date(string='Customer Signature Date')
    signature_plant = fields.Char(string='Plant Signatory')
    signature_customer = fields.Char(string='Customer Signatory')
    signature_supervisor = fields.Char(string='Site Supervisor Signatory')
    max_unloading_time = fields.Char(string='Max Unloading Time', default='6 mins')
    delivery_note = fields.Text(
        string='Delivery Note/Warning',
        default="The time allowed for unloading this vehicle is 6 mins..."
    )
    template_id = fields.Many2one('excel.template', string='Excel Template')
    generated_document_id = fields.Many2one('documents.document', string='Generated Document', readonly=True)

    @api.depends('time_ex_plant', 'time_returned_plant')
    def _compute_total_time(self):
        for record in self:
            if record.time_ex_plant and record.time_returned_plant:
                delta = record.time_returned_plant - record.time_ex_plant
                record.total_time_taken = delta.total_seconds() / 3600
            else:
                record.total_time_taken = 0.0

    def action_generate_excel(self):
        self.ensure_one()
        if not self.template_id or not self.template_id.document_id:
            return {'type': 'ir.actions.client', 'tag': 'display_notification', 'params': {
                'message': 'Please select an Excel template first.', 'type': 'warning', 'sticky': False}}
        
        folder = self.env['documents.document'].search([('name', 'ilike', 'Delivery Tickets'), ('type', '=', 'folder')], limit=1)
        if not folder:
            folder = self.env['documents.document'].create({'name': 'Delivery Tickets', 'type': 'folder'})
        
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
        
        # log_dir = r'C:\Users\ODOO\Documents\ODOO 19\odoo\custom\concrete_order\temp'
        # os.makedirs(log_dir, exist_ok=True)
        # timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        # log_file = os.path.join(log_dir, f'{self.name}_{timestamp}.log')
        
        # with open(log_file, 'w', encoding='utf-8') as f:
        #     f.write(f'=== BEFORE TEMPLATE ({self.name}) ===\n')
        #     f.write(json.dumps(json.loads(template_doc.spreadsheet_data or '{}'), indent=2))
        #     f.write('\n\n=== AFTER TEMPLATE ===\n')
        #     f.write(json.dumps(data, indent=2))
        
        existing_doc = self.env['documents.document'].search([
            ('name', '=', self.name),
            ('folder_id', '=', folder.id),
            ('res_model', '=', self._name),
            ('res_id', '=', self.id)
        ], limit=1)
        
        if existing_doc:
            existing_doc.write({'spreadsheet_data': json.dumps(data)})
            self.generated_document_id = existing_doc
            message = f'Document "{self.name}" updated in Delivery Tickets folder.'
        else:
            doc = self.env['documents.document'].create({
                'name': self.name,
                'folder_id': folder.id,
                'res_model': self._name,
                'res_id': self.id,
                'mimetype': 'application/o-spreadsheet',
                'handler': 'spreadsheet',
                'spreadsheet_data': json.dumps(data),
            })
            self.generated_document_id = doc
            message = f'Document "{self.name}" created in Delivery Tickets folder.'
        
        self.env['bus.bus']._sendone(self.env.user.partner_id, 'simple_notification', {
            'type': 'success',
            'message': message,
            'sticky': False
        })
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current'
        }

    def action_open_generated_document(self):
        self.ensure_one()
        if not self.generated_document_id:
            return {'type': 'ir.actions.client', 'tag': 'display_notification', 'params': {
                'message': 'No document generated yet. Please generate Excel first.', 'type': 'warning', 'sticky': False}}
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/odoo/documents/spreadsheet/{self.generated_document_id.id}',
            'target': 'new'
        }

    def action_print_document(self):
        self.ensure_one()
        if not self.generated_document_id:
            return {'type': 'ir.actions.client', 'tag': 'display_notification', 'params': {
                'message': 'No document generated yet. Please generate Excel first.', 'type': 'warning', 'sticky': False}}
        
        return {
            'type': 'ir.actions.client',
            'tag': 'action_print_spreadsheet',
            'params': {'spreadsheet_id': self.generated_document_id.id}
        }
