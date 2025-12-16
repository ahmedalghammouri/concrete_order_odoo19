{
    'name': 'Concrete Order - Sale Integration',
    'version': '19.0.1.0.0',
    'category': 'Concrete/Sales',
    'summary': 'Integration between Concrete Delivery Tickets and Sale Orders',
    'author': 'Your Company',
    'website': 'https://www.example.com',
    'license': 'LGPL-3',
    'depends': ['concrete_order', 'concrete_order_stock_out', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/concrete_delivery_ticket_views.xml',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
