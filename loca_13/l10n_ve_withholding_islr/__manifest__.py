# -*- coding: utf-8 -*-

{
    'name': 'Automatically Calculation Income Withholding (ISLR)',
    'author': 'INM & LDR Soluciones Tecnológicas y Empresariales C.A',
    'summary': 'ISLR Venezuela',
    'description': """This model do the retention about taxes in Venezuela.""",
    'category': 'Accounting/Accounting',
    'website': '',
    'images': [],
    'depends': [
        'account',
        #'account_accountant',
        #'base',
        'vat_retention',
        'l10n_ve_fiscal_requirements',
        ],
    'data': [
        'data/islr_concept_data.xml',
        'data/islr_retention_rate.xml',
        'security/ir.model.access.csv',
        #'views/res_company_views.xml',
        'views/res_partner_views.xml',
        'views/product_template_views.xml',
        'views/islr_wh_doc_views.xml',
        'views/islr_concept_views.xml',
        ],
    'installable': True,
    'application': True,
    'auto_install': True,
}