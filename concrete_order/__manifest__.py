{
    'name': 'Concrete Order Management',
    'version': '19.0.1.0.0',
    'category': 'Operations',
    'summary': 'Specialized Projects Ready Mix Concrete Delivery Ticket Management',
    'description': """
        Concrete Delivery Ticket Management System
        ==========================================
        * Manage concrete delivery tickets
        * Excel template integration
        * Field mapping for data export
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['base', 'mail', 'hr', 'documents', 'documents_spreadsheet'],
    'data': [
        'security/concrete_order_security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/concrete_vehicle_views.xml',
        'views/concrete_driver_views.xml',
        'views/concrete_delivery_ticket_views.xml',
        'views/excel_template_views.xml',
        'views/excel_field_mapping_views.xml',
        'views/menu_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'concrete_order/static/src/js/print_spreadsheet.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3'
}
