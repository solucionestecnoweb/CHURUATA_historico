# -*- coding: utf-8 -*-

{
        'name': 'VAT Retention for Venezuela',
        'version': '0.1',
        'author': 'INM & LDR Soluciones Tecnológicas y Empresariales C.A',
        'summary': 'VAT Retention',
        'description': """This model do the retention about taxes in Venezuela.""",
        'category': 'Accounting/Accounting',
        'website': '',
        'images': [],
        'depends': [
            'account',
            'account_accountant',
            'base',
            'l10n_ve_fiscal_requirements',
            ],
        'data': [
            'security/ir.model.access.csv',
            'data/vat_retention_data.xml',
            'views/retention_vat_views.xml',
            'views/menu_vat_retention.xml',
            'views/partner_views.xml',
            'views/account_move_views.xml',
            'views/account_journal_views.xml',
            'wizard/wizard_generar_txt_view.xml',
            'report/vat_wh_voucher.xml',
            ],
        'installable': True,
        'application': True,
        'auto_install': False,
                      
}
