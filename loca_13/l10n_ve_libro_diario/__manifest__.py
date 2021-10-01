# -*- coding: utf-8 -*-
{
    'name': "Reporte del Libro diario",

    'summary': """Reporte del Libro diario""",

    'description': """
       Reporte del Libro diario.
    """,
    'version': '13.0',
    'author': 'INM & LDR Soluciones Tecnológicas y Empresariales C.A',
    'category': 'Tools',
    'website': 'http://soluciones-tecno.com/',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
        'report/reporte_view.xml',
        'wizard/wizard.xml'
    ],
    'application': True,
    'active':False,
    'auto_install': False,
}
