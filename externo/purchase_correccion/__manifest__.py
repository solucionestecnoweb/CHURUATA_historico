# -*- coding: utf-8 -*-
{
    'name': "correccion_crm",

    'summary': """correccion_crm""",

    'description': """
       correccion_crm.
    """,
    'version': '13.0',
    'author': 'INM & LDR Soluciones Tecnológicas y Empresariales C.A',
    'category': 'Tools',
    'website': 'http://soluciones-tecno.com/',

    # any module necessary for this one to work correctly
    'depends': ['purchase','purchase_stock'],

    # always loaded
    'data': [
    'views/purchase_view.xml',
    #'views/prestamo_view.xml',
    #'views/hr_payslip_view.xml',
    #'security/ir.model.access.csv',
    ],
    'application': True,
    'active':False,
    'auto_install': False,
}
