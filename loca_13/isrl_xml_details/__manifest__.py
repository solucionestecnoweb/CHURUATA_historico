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
            'product',
            'isrl_retention'
            ],
        'data': [
            'security/ir.model.access.csv',
            'views/retention_details.xml',
            ],
        'installable': True,
        'application': True,
        'auto_install': False,
                      
}
