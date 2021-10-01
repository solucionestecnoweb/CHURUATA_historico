# -*- coding: utf-8 -*-
{
    'name': "Doble Aprobacion Ordenes de Venta y Compra",

    'summary': """Doble Aprobacion Ordenes de Venta y Compra""",

    'description': """
       Doble Aprobacion Ordenes de Venta y Compra.
    """,
    'version': '13.0',
    'author': 'INM & LDR Soluciones Tecnológicas y Empresariales C.A',
    'category': 'Tools',
    'website': 'http://soluciones-tecno.com/',

    # any module necessary for this one to work correctly
    'depends': ['sale','sale_management'],

    # always loaded
    'data': [
    'views/sale_order.xml',
    'views/sale_order_approval.xml',
    'views/sale_config_approval.xml',
    'views/purchase_order.xml',
    'views/purchase_config_approval.xml',
    'views/purchase_order_approval.xml',
    'security/ir.model.access.csv',
    ],
    'application': True,
    'active':False,
    'auto_install': False,
}
