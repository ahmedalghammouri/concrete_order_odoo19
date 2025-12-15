from odoo import models, fields


class ExcelFieldMapping(models.Model):
    _name = 'excel.field.mapping'
    _description = 'Excel Field Mapping'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    template_id = fields.Many2one('excel.template', string='Template', required=True, ondelete='cascade')
    field_name = fields.Selection([
        ('name', 'Ticket No.'),
        ('ticket_serial_no', 'Serial No.'),
        ('delivery_date', 'Date'),
        ('delivery_time', 'Time'),
        ('customer_id', 'Customer'),
        ('customer_order_no', 'Customer Order No.'),
        ('enquiry_form_no', 'Enquiry Form No.'),
        ('delivery_to', 'Delivered To'),
        ('site_no', 'Site No.'),
        ('site_name', 'Site Name'),
        ('area', 'Area'),
        ('plant_no', 'Plant No.'),
        ('plant_name', 'Plant Name'),
        ('plant_batch_no', 'Plant Batch No.'),
        ('mix_description', 'Mix Description'),
        ('cement_type', 'Cement Type'),
        ('admixture', 'Admixture'),
        ('total_admixtures', 'Total Admixtures'),
        ('slump_value', 'Slump'),
        ('volume_m3', 'Volume (C.U.M)'),
        ('total_volume_delivered', 'Total Delivered'),
        ('driver_name_text', 'Driver Name'),
        ('vehicle_no', 'Vehicle No.'),
        ('time_ex_plant', 'Time Ex-Plant'),
        ('time_on_site', 'Time On Site'),
        ('time_start_discharge', 'Time Start Discharge'),
        ('time_finish_discharge', 'Time Finish Discharge'),
    ], string='Field', required=True)
    cell_location = fields.Char(string='Cell Location (e.g., A1)', required=True)
