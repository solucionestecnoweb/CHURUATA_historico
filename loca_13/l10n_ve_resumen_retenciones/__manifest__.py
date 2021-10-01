# -*- coding: utf-8 -*-
{
    'name': "Reportes de reumen  de retenciones",

    'summary': """Reportes de resumen de retenciones""",

    'description': """
       Reportes de resumenes de retenciones IVA, Municipal e ISLR.
    """,
    'version': '13.0',
    'author': 'INM & LDR Soluciones Tecnológicas y Empresariales C.A',
    'category': 'Tools',
    'website': 'http://soluciones-tecno.com/',

    # any module necessary for this one to work correctly
    'depends': ['base','account','municipality_tax','vat_retention','isrl_retention','libro_resumen_alicuota'],

    # always loaded
    'data': [
    	'security/ir.model.access.csv',
        'resumen_iva/reporte_view.xml',
        'resumen_iva/wizard.xml',
        'resumen_municipal/wizard.xml',
        'resumen_municipal/reporte_view.xml',
        'resumen_islr/wizard.xml',
        'resumen_islr/reporte_view.xml',
    ],
    'application': True,
    'active':False,
    'auto_install': False,
}
