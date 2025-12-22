{
    'name': 'Concrete Mixer Delivery Point',
    'version': '19.0.1.0.0',
    'category': 'Concrete/Delivery',
    'summary': 'Fast Point Interface for Concrete Mixer Deliveries',
    'description': '''
Concrete Mixer Delivery Point
==============================
Simplified interface for concrete delivery operations:
* Quick access to pending delivery tickets
* Barcode scanning for fast retrieval
* Large buttons and displays for operators
* Real-time delivery status updates
* Session management for operators
    ''',
    'author': 'Gemy',
    'website': 'https://www.example.com',
    'license': 'LGPL-3',
    'depends': ['concrete_order', 'concrete_order_stock_out'],
    'data': [
        'wizard/concrete_delivery_wizard_views.xml',
        'views/concrete_delivery_cmdp_views.xml',
        'views/menu_views.xml',
        'security/ir.model.access.csv',
    ],
    'assets': {
        'web.assets_backend': [
            'concrete_order_cmdp/static/src/js/concrete_delivery_cmdp.js',
            'concrete_order_cmdp/static/src/xml/concrete_delivery_cmdp.xml',
            'concrete_order_cmdp/static/src/scss/concrete_delivery_cmdp.scss',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'icon': '/concrete_order_cmdp/static/description/icon.png'
}
