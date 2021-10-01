# -*- coding: utf-8 -*-
{
    'name': "Foreign Trade & Logistics",

    'summary': """
        Foreign trade cost with landed cost extended""",

    'description': """
        Manage imports and logistics from supplier invoices and product
        receipts to handling container arrival at company warehouses
    """,

    'author': "Ing. Jean Paul Casis",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Operations/Inventory',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock_landed_costs'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'views/views.xml',
        # 'views/templates.xml',
        'views/stock_landed_cost.xml',
        'report/unit_cost_report.xml',
        'report/unit_cost_report_template.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
