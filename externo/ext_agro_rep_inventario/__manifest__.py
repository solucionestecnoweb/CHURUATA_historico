# -*- coding: utf-8 -*-
{
    'name': "Reportes Modificados de Inventario",

    'summary': """Reportes de Inventario""",

    'description': """
       Reportes Modificados de Inventario.
    """,
    'version': '13.0',
    'author': 'INM & LDR Soluciones Tecnológicas y Empresariales C.A',
    'category': 'Tools',
    'website': 'http://soluciones-tecno.com/',

    # any module necessary for this one to work correctly
    'depends': ['base','account','purchase','sale','stock','mrp'],

    # always loaded
    'data': [
        'formatos/vale_entrega.xml',
        'formatos/wizard_resumen_semanal_produccion.xml',
        'security/ir.model.access.csv',
        'formatos/reporte_resumen_semanal_produccion.xml',
        #'formatos/solicitud_ventas.xml',
        #'formatos/pedido_venta.xml',
        #'formatos/sale_order.xml',
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
