# -*- coding: utf-8 -*-
{
    'name': "Extencion Terminal Punto de Venta para odoo sh",

    'summary': """Extencion Terminal Punto de Venta para odoo sh""",

    'description': """
       Extencion Terminal Punto de Venta para odoo sh
       Colaborador: Ing. Darrell Sojo
    """,
    'version': '1.0',
    'author': 'INM&LDR Soluciones Tecnologicas',
    'category': 'Extension Módulo Terminal Punto de Venta para odoo sh',

    # any module necessary for this one to work correctly
    'depends': ['base','point_of_sale','l10n_ve_fiscal_requirements','account','vat_retention','ext_extension_tpdv'],

    # always loaded
    'data': [
    'vista_pos_order_inherit_sh.xml',
    ],
    'application': True,
}
