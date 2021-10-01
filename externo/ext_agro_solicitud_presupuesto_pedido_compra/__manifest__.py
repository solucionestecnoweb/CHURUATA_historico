# -*- coding: utf-8 -*-
{
    'name': "solicitudes de presupuestos y pedidos de compra y ventas",

    'summary': """solicitudes de presupuestos y pedidos de compra y ventas""",

    'description': """
       solicitudes de presupuestos y pedidos de compra y ventas.
    """,
    'version': '13.0',
    'author': 'INM & LDR Soluciones Tecnológicas y Empresariales C.A',
    'category': 'Tools',
    'website': 'http://soluciones-tecno.com/',

    # any module necessary for this one to work correctly
    'depends': ['base','account','purchase','sale','ext_personalizacion_lanta'],

    # always loaded
    'data': [
        'formatos/solicitud_compras.xml',
        'formatos/pedido_compras.xml',
        'formatos/purchase_order.xml',
        'formatos/solicitud_ventas.xml',
        'formatos/pedido_venta.xml',
        'formatos/sale_order.xml',
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
