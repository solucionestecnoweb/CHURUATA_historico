# -*- coding: utf-8 -*-
{
    'name': "conciliacion automatica de comprobantes iva y municipal",

    'summary': """Conciliacion automatica de comprobantes iva y municipal""",

    'description': """
       Conciliacion automatica en status publicados en los comprobantes iva y municipal  
       al publicar una factura
    """,
    'version': '3.0',
    'author': 'INM & LDR Soluciones Tecnológicas y Empresariales C.A',
    'category': 'Tools',

    # any module necessary for this one to work correctly
    'depends': ['base','account','account_accountant','municipality_tax','vat_retention','isrl_retention'],

    # always loaded
    'data': [
        #'view/vista_view.xml'
    ],
    'application': True,
}
