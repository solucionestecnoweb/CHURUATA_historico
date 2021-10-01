# -*- coding: utf-8 -*-
{
    'name': "HERENCIAS Conciliacion Bancaria por referencia",

    'summary': """Conciliacion Bancaria por Referencia""",

    'description': """
       Mejorar Concialiacion Bancaria por Referencia.
    """,
    'version': '3.0',
    'author': 'INM & LDR Soluciones Tecnológicas y Empresariales C.A',
    'category': 'Tools',

    # any module necessary for this one to work correctly
    'depends': ['base','account','account_accountant'],

    # always loaded
    'data': [
        'view/vista_view.xml'
    ],
    'application': True,
}
