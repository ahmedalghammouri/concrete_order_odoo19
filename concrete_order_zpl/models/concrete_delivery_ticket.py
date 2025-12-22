# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ConcreteDeliveryTicket(models.Model):
    _inherit = 'concrete.delivery.ticket'
    
    printer_id = fields.Many2one('concrete.zpl.printer', string='Printer', default=lambda self: self.env['concrete.zpl.printer'].search([('is_default', '=', True)], limit=1))
    
    def action_print_ticket(self):
        self.ensure_one()
        if not self.printer_id:
            raise UserError(_("Please select a printer first."))
        
        zpl_code = self._generate_ticket_zpl()
        
        job = self.env['concrete.zpl.print.job'].create({
            'name': f'Ticket {self.name}',
            'printer_id': self.printer_id.id,
            'ticket_id': self.id,
            'print_type': 'ticket',
            'zpl_code': zpl_code,
        })
        
        job.action_print()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Ticket printed successfully!'),
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_print_label(self):
        self.ensure_one()
        if not self.printer_id:
            raise UserError(_("Please select a printer first."))
        
        zpl_code = self._generate_label_zpl()
        
        job = self.env['concrete.zpl.print.job'].create({
            'name': f'Label {self.name}',
            'printer_id': self.printer_id.id,
            'ticket_id': self.id,
            'print_type': 'label',
            'zpl_code': zpl_code,
        })
        
        job.action_print()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Label printed successfully!'),
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_print_barcode(self):
        self.ensure_one()
        if not self.printer_id:
            raise UserError(_("Please select a printer first."))
        
        zpl_code = self._generate_barcode_zpl()
        
        job = self.env['concrete.zpl.print.job'].create({
            'name': f'Barcode {self.name}',
            'printer_id': self.printer_id.id,
            'ticket_id': self.id,
            'print_type': 'barcode',
            'zpl_code': zpl_code,
        })
        
        job.action_print()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Barcode printed successfully!'),
                'type': 'success',
                'sticky': False,
            }
        }
    
    def _generate_ticket_zpl(self):
        self.ensure_one()
        
        zpl = "^XA\n"
        zpl += "^CF0,60\n"
        zpl += "^FO30,20^GB740,0,4^FS\n"
        zpl += "^FO30,20^GB0,580,4^FS\n"
        zpl += "^FO770,20^GB0,580,4^FS\n"
        zpl += "^FO30,600^GB740,0,4^FS\n"
        zpl += "^FO50,40^A0N,55,55^FDCONCRETE DELIVERY TICKET^FS\n"
        zpl += "^FO30,105^GB740,0,3^FS\n"
        zpl += f"^FO60,125^A0N,45,45^FDTicket: {self.name}^FS\n"
        zpl += "^FO30,180^GB740,0,2^FS\n"
        zpl += f"^FO60,195^A0N,28,28^FDCustomer: {self.customer_id.name or ''}^FS\n"
        zpl += f"^FO60,230^A0N,28,28^FDSite: {self.site_name or ''}^FS\n"
        zpl += "^FO30,265^GB740,0,2^FS\n"
        zpl += f"^FO60,280^A0N,28,28^FDProduct: {self.product_id.name or ''}^FS\n"
        zpl += f"^FO60,315^A0N,28,28^FDMix: {self.mix_description or ''}^FS\n"
        zpl += "^FO30,350^GB740,0,2^FS\n"
        zpl += f"^FO60,365^A0N,40,40^FDVolume: {self.volume_m3} M3^FS\n"
        zpl += "^FO30,415^GB740,0,2^FS\n"
        zpl += f"^FO60,430^A0N,28,28^FDVehicle: {self.vehicle_plate or ''}^FS\n"
        zpl += f"^FO60,465^A0N,28,28^FDDriver: {self.driver_name or ''}^FS\n"
        zpl += "^FO30,500^GB740,0,2^FS\n"
        zpl += f"^FO60,515^A0N,28,28^FDDate: {self.delivery_date}^FS\n"
        zpl += f"^FO60,550^A0N,28,28^FDTime: {self.delivery_time or ''}^FS\n"
        zpl += "^XZ"
        
        return zpl
    
    def _generate_label_zpl(self):
        self.ensure_one()
        
        zpl = "^XA\n"
        zpl += "^CF0,40\n"
        zpl += "^FO20,15^GB760,0,4^FS\n"
        zpl += "^FO20,15^GB0,520,4^FS\n"
        zpl += "^FO780,15^GB0,520,4^FS\n"
        zpl += "^FO20,535^GB760,0,4^FS\n"
        zpl += "^FO40,30^A0N,50,50^FDCONCRETE LABEL^FS\n"
        zpl += "^FO20,90^GB760,0,3^FS\n"
        zpl += f"^FO40,105^A0N,38,38^FD{self.name}^FS\n"
        zpl += "^FO20,150^GB760,0,2^FS\n"
        zpl += f"^FO40,160^A0N,26,26^FDCustomer: {self.customer_id.name or ''}^FS\n"
        zpl += f"^FO40,190^A0N,26,26^FDSite: {self.site_name or ''}^FS\n"
        zpl += "^FO20,220^GB760,0,2^FS\n"
        zpl += f"^FO40,230^A0N,26,26^FDProduct: {self.product_id.name or ''}^FS\n"
        zpl += f"^FO40,260^A0N,32,32^FDVolume: {self.volume_m3} M3^FS\n"
        zpl += "^FO20,300^GB760,0,2^FS\n"
        zpl += f"^FO40,310^A0N,24,24^FDVehicle: {self.vehicle_plate or ''}^FS\n"
        zpl += f"^FO40,340^A0N,24,24^FDDate: {self.delivery_date}^FS\n"
        zpl += "^FO20,375^GB760,0,2^FS\n"
        zpl += f"^FO120,395^BY3^BCN,100,Y,N,N^FD{self.name}^FS\n"
        zpl += "^XZ"
        
        return zpl
    
    def _generate_barcode_zpl(self):
        self.ensure_one()
        
        zpl = "^XA\n"
        zpl += "^CF0,30\n"
        zpl += "^FO30,15^GB740,0,4^FS\n"
        zpl += "^FO30,15^GB0,500,4^FS\n"
        zpl += "^FO770,15^GB0,500,4^FS\n"
        zpl += "^FO30,515^GB740,0,4^FS\n"
        zpl += "^FO50,30^A0N,45,45^FDCONCRETE DELIVERY^FS\n"
        zpl += f"^FO50,80^A0N,32,32^FDTicket: {self.name}^FS\n"
        zpl += "^FO30,120^GB740,0,2^FS\n"
        zpl += f"^FO50,135^A0N,28,28^FDCustomer: {self.customer_id.name or ''}^FS\n"
        zpl += f"^FO50,170^A0N,28,28^FDSite: {self.site_name or ''}^FS\n"
        zpl += f"^FO50,205^A0N,32,32^FDVolume: {self.volume_m3} M3^FS\n"
        zpl += "^FO30,245^GB740,0,2^FS\n"
        zpl += f"^FO50,255^A0N,26,26^FDVehicle: {self.vehicle_plate or ''} - {self.driver_name or ''}^FS\n"
        zpl += "^FO30,290^GB740,0,2^FS\n"
        zpl += f"^FO120,320^BY4^BCN,160,Y,N,N^FD{self.name}^FS\n"
        zpl += "^XZ"
        
        return zpl
