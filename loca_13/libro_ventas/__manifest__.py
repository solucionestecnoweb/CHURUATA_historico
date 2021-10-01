# -*- coding: utf-8 -*-

{
    'name': "libro_ventas",

    'summary': """
        Libro de Ventas
        """,

    'description': """
        Libro de ventas
    """,

    'author': "Softw & Hardw Solutions SSH",
    'website': "https://solutionssh.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Contabilidad',
    'version': '0.1',

    # any module necessary for this one to work correctly
     "depends" : ['base','account','libro_resumen_alicuota'],

    # always loaded
    'data': [
        'views/wizard_libro_ventas.xml',
        'reports/report_factura_clientes.xml',
        'security/ir.model.access.csv',
        ],  
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
}
