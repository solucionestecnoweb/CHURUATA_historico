# -*- coding: utf-8 -*-

{

    'name': 'Venezuelan Fiscal Requirements',
    'summary': 'Fields for company information for Venezuela',
    'description': """ This model add fields that need a lot of companies in Venezuela.""",
    'author': 'INM & LDR Soluciones Tecnológicas y Empresariales C.A',
    'depends': [
        'account',
        'account_accountant',
        'base',
        'base_vat',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/tax_unit_data.xml',
        'views/partner_inherit_views.xml',
        'views/company_inherit_views.xml',
        'views/account_inherit_views.xml',
        'views/account_journal_views.xml',
        'views/account_tax_views.xml',
        'views/tax_unit_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,

}