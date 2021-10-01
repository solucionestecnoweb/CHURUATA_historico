# -*- coding: utf-8 -*-
{
    'name': "Filtro en los diariosen modulo de factura",

    'summary': """Filtro en los diariosen modulo de factura""",

    'description': """
       Filtro en los diariosen modulo de factura
    """,
    'version': '3.0',
    'author': 'INM & LDR Soluciones Tecnológicas y Empresariales C.A',
    'category': 'Tools',

    # any module necessary for this one to work correctly
    'depends': ['base','account','account_accountant','libro_ventas','libro_compras'],

    # always loaded
    'data': [
        'view/vista_view.xml'
    ],
    'application': True,
}
