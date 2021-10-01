# -*- coding: utf-8 -*-
{
    'name': "Archivo txt iva proveedores seniat",

    'summary': """Archivo txt iva proveedores seniat""",

    'description': """
       Archivo txt iva proveedores seniat
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
        'libro_resumen_alicuota',
    ],

    # always loaded
    'data': [
        'wizard/wizard_generar_txt_view.xml',
    ],
    'application': True,
}
