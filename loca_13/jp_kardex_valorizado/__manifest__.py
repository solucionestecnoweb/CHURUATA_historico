# -*- encoding: utf-8 -*-
{
    'name': 'Kardex Valorizado',
    'version': '1.0',
    'author': 'Ing. Jose Blanco',
    'website': 'gregoriocode.com',
    'category': 'account',
    'depends': ['product','stock','account','mrp','purchase_stock','sale_stock','stock_account',"stock"],
    'description': """KARDEX VALORIZADO""",
    'demo': [],
    'data': [
        'security/ir.model.access.csv',
        'views/account_move.xml',
        'views/stock_picking_views.xml',
        'views/stock_inventory.xml',
        'views/stock_valuation_layer.xml',
        'wizard/make_kardex_view.xml',
        'views/product.xml',
        'data/tipo.xml',
    ],
    'auto_install': False,
    'installable': True
}