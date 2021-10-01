# -*- coding: utf-8 -*-
{
    'name': "Boton Draf o Borrador en  comprobantes iva, ISLR y municipal",

    'summary': """Boton Draf o Borrador en  comprobantes iva, ISLR y municipal""",

    'description': """
       Boton Draf o Borrador en  comprobantes iva, ISLR y municipal la cual al volver
       a publicar, este mantiene losmismos nros de comprobantes y de asientos
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
        'security/ir.model.access.csv',
        #'view/res_partner_views.xml',
        #'view/comprobantes.xml',
    ],
    'application': True,
}
