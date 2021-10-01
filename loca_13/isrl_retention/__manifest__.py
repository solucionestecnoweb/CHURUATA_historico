# -*- coding: utf-8 -*-

{
        'name': 'ISLR Retention for Venezuela',
        'version': '0.1',
        'author': 'INM & LDR Soluciones Tecnológicas y Empresariales C.A',
        'summary': 'ISLR Retention',
        'description': """This model do the retention about taxes in Venezuela.""",
        'category': 'Accounting/Accounting',
        'website': '',
        'images': [],
        'depends': [
            'account',
            'account_accountant',
            'base',
            'l10n_ve_fiscal_requirements',
            'l10n_ve_withholding_islr',
            'vat_retention',
            'product'
            ],
        'data': [
            'security/ir.model.access.csv',
            'data/vat_retention_data.xml',
            'views/retention_vat_views.xml',
            'views/menu_vat_retention.xml',
            'views/partner_views.xml',
            'views/account_move_views.xml',
            'wizards/xml_views.xml',
            'wizards/arc.xml',
            'report/vat_isrl_voucher.xml',
            ],
        'installable': True,
        'application': True,
        'auto_install': False,
                      
}
