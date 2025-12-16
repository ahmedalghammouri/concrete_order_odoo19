{
    'name': 'Concrete Order - Stock Integration',
    'version': '19.0.1.0.0',
    'category': 'Concrete/Delivery',
    'summary': 'Integration between Concrete Delivery Tickets and Stock Delivery Orders',
    'author': 'Your Company',
    'website': 'https://www.example.com',
    'license': 'LGPL-3',
    'depends': ['concrete_order', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/concrete_delivery_ticket_views.xml',
        'views/stock_picking_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
