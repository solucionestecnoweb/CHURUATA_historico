# -*- coding: utf-8 -*-
{
    'name': "Exclución de factura en los libros de ventas y compras",

    'summary': """Exclución de factura en los libros de ventas y compras""",

    'description': """
       Exclución de factura en los libros de ventas y compras.
    """,
    'version': '1.0',
    'author': 'INM & LDR Soluciones Tecnológicas y Empresariales C.A',
    'category': 'Tools',

    # any module necessary for this one to work correctly
    'depends': ['base',
    'account',
    'libro_ventas',
    'libro_compras',
    'libro_resumen_alicuota',
    'l10n_ve_fiscal_requirements',
    ],

    # always loaded
    'data': [
    'view/vista_view.xml',
    ],
    'application': True,
}
