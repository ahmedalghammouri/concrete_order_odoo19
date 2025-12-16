from odoo import models, fields, api


class ExcelTemplate(models.Model):
    _name = 'excel.template'
    _description = 'Excel Template'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Template Name', required=True)
    document_id = fields.Many2one('spreadsheet.template', string='Excel File', required=True)
    file = fields.Binary(compute='_compute_file', string='File Content')
    filename = fields.Char(related='document_id.name', string='Filename')
    mapping_ids = fields.One2many('excel.field.mapping', 'template_id', string='Field Mappings')
    is_default = fields.Boolean(string='Default Template', default=False)

    @api.depends('document_id')
    def _compute_file(self):
        for record in self:
            if record.document_id:
                record.file = record.document_id.spreadsheet_binary_data
            else:
                record.file = False

    def write(self, vals):
        if vals.get('is_default'):
            self.search([('id', '!=', self.id), ('is_default', '=', True)]).write({'is_default': False})
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            if record.is_default:
                self.search([('id', '!=', record.id), ('is_default', '=', True)]).write({'is_default': False})
        return records
