# -*- coding: utf-8 -*-
from odoo import models, fields

class ExcelFieldMapping(models.Model):
    _inherit = 'excel.field.mapping'

    field_name = fields.Selection(selection_add=[
        ('delivery_id', 'Delivery Order'),
        ('location_id', 'Source Location'),
        ('demand_qty', 'Demand Quantity'),
        ('source_document', 'Source Document'),
        ('scheduled_date', 'Scheduled Date'),
        ('remaining_qty', 'Remaining Quantity'),
        ('variance_qty', 'Variance'),
        ('variance_percent', 'Variance %'),
        ('fulfillment_percent', 'Fulfillment %'),
    ], ondelete={
        'delivery_id': 'cascade',
        'location_id': 'cascade',
        'demand_qty': 'cascade',
        'source_document': 'cascade',
        'scheduled_date': 'cascade',
        'remaining_qty': 'cascade',
        'variance_qty': 'cascade',
        'variance_percent': 'cascade',
        'fulfillment_percent': 'cascade',
    })
