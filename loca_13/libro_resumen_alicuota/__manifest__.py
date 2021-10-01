# -*- coding: utf-8 -*-
{
    'name': "Modulo de resumen totales por alicuotas en las lineas de la factura",

    'summary': """Modulo de resumen totales por alicuotas en las lineas de la factura""",

    'description': """
       Modulo de resumen totales por alicuotas en las lineas de la factura
    """,
    'version': '3.0',
    'author': 'INM & LDR Soluciones Tecnológicas y Empresariales C.A',
    'category': 'Tools',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account',
        'account_accountant',
        'vat_retention',
        #'isrl_retention',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'view/account_move_view.xml',
        #'view/comprobantes.xml',
    ],
    'application': True,
}
