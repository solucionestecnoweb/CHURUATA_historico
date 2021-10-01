# -*- coding: utf-8 -*-
{
    'name': "Incluir Firma Digitalizada en comprobantes iva, ISLR y municipal",

    'summary': """Incluir Firma Digitalizada en comprobantes iva, ISLR y municipal""",

    'description': """
       Incluir Firma Digitalizada en los comprobantes iva, ISLR y municipal
    """,
    'version': '3.0',
    'author': 'INM & LDR Soluciones Tecnológicas y Empresariales C.A',
    'category': 'Tools',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account',
        'account_accountant',
        'municipality_tax',
        'vat_retention',
        'isrl_retention',
    ],

    # always loaded
    'data': [
        'view/res_partner_views.xml',
        'view/comprobantes.xml',
    ],
    'application': True,
}
