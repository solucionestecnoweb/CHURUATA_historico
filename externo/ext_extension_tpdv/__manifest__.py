# -*- coding: utf-8 -*-
{
    'name': "Extencion Terminal Punto de Venta",

    'summary': """Extencion Terminal Punto de Venta""",

    'description': """
       Extencion Terminal Punto de Venta
       Colaborador: Ing. Darrell Sojo
    """,
    'version': '1.0',
    'author': 'INM&LDR Soluciones Tecnologicas',
    'category': 'Extension Módulo Terminal Punto de Venta',

    # any module necessary for this one to work correctly
    'depends': ['base','point_of_sale','l10n_ve_fiscal_requirements','account','vat_retention'],

    # always loaded
    'data': [
        'vista_view.xml',
        'buttom_menu_view.xml',
        'vista_pos_paymet_inheret.xml',
        'vista_pos_order_inherit.xml',
        'pos_config_inherit.xml',
        'security/ir.model.access.csv',
        'reports/report_libro_pos.xml',
        'wizards/wizard_libro_ventas_pos.xml',
    ],
    'application': True,
}
