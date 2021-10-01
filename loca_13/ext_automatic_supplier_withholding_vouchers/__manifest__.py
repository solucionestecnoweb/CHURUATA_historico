# -*- coding: utf-8 -*-
{
    'name': "Retencion automatica de comprobantes iva y municipal en proveedores",

    'summary': """Retencion automatica de comprobantes iva y municipal en proveedores""",

    'description': """
       Retencion automatica en status publicados en los comprobantes iva y municipal en proveedores 
       al publicar una factura
    """,
    'version': '3.0',
    'author': 'INM & LDR Soluciones Tecnológicas y Empresariales C.A',
    'category': 'Tools',

    # any module necessary for this one to work correctly
    'depends': ['base','account','account_accountant','municipality_tax','vat_retention'],

    # always loaded
    'data': [
        #'view/vista_view.xml'
    ],
    'application': True,
}
