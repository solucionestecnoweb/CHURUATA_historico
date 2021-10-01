# -*- coding: utf-8 -*-

{
    'name': "Resumen compra ventas e iva articulo 72",

    'summary': """
        Resumen compra ventas e iva articulo 72
        """,

    'description': """
        Resumen compra ventas e iva articulo 72
    """,

    'author': 'INM & LDR Soluciones Tecnológicas y Empresariales C.A',
    'category': 'Tools',
    'website': 'http://soluciones-tecno.com/',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Contabilidad',
    'version': '0.1',

    # any module necessary for this one to work correctly
     "depends" : ['base','account','libro_resumen_alicuota','vat_retention'],

    # always loaded
    'data': [
        'views/wizard_resumen.xml',
        'security/ir.model.access.csv',
        ],  
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
}
