# -*- coding: utf-8 -*-
{
    'name': "Formatos de Factura, NC, ND de forma Libre",

    'summary': """Formatos de Factura, NC, ND de forma Libre""",

    'description': """
       Formatos de Factura, NC, ND de forma Libre.
    """,
    'version': '13.0',
    'author': 'INM & LDR Soluciones Tecnológicas y Empresariales C.A',
    'category': 'Tools',
    'website': 'http://soluciones-tecno.com/',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
        'formatos/factura_libre.xml',
        'formatos/nota_entrega.xml',
        'formatos/account_move_view.xml',
    	#'security/ir.model.access.csv',
        #'resumen_iva/reporte_view.xml',
        #'resumen_iva/wizard.xml',
        #'resumen_municipal/wizard.xml',
        #'resumen_municipal/reporte_view.xml',
        #'resumen_islr/wizard.xml',
        #'resumen_islr/reporte_view.xml',
    ],
    'application': True,
    'active':False,
    'auto_install': False,
}
