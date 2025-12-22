{
    'name': 'Concrete Order - ZPL Printer',
    'version': '19.0.1.0.0',
    'category': 'Concrete',
    'summary': 'ZPL thermal printer integration for concrete delivery tickets',
    'description': '''
ZPL Printer Integration for Concrete Delivery
==============================================
Professional thermal printer support:
* Configure ZPL printers (Zebra, compatible brands)
* Auto-print delivery tickets
* Network and USB printer support
* Custom label templates
* Print queue management
    ''',
    'author': 'Gemy',
    'license': 'LGPL-3',
    'depends': [
        'concrete_order',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/zpl_printer_views.xml',
        'views/concrete_delivery_ticket_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
