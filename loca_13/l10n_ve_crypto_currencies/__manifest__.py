# -*- coding: utf-8 -*-


{
    'name': 'CryptoCurrencies',
    'version': '0.1',
    'author': 'INM & LDR Soluciones Tecnológicas y Empresariales C.A',
    'depends': [
        'base',
        'account',
        'purchase',
        'sale_management',
        'l10n_ve_fiscal_requirements',
    ],
    'data': [
        'data/cryptocurrencies_data.xml',
        'wizard/compute_cryptocurrency_view.xml',
        'views/res_currency_views.xml',
        'views/account_move_views.xml',
        'views/purchase_order_views.xml',
        'views/sale_order_views.xml',
        
    ],
    'application': False,
}
