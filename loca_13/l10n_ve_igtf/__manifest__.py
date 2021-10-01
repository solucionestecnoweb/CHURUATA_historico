{
    'name': "Localizacion Venezolana calculo de IGTF y Modulo de Anticipo",

    'summary': """Retención automática de ITF y Módulo de Anticipo""",

    'description': """
       Calcule la retención automática de itf.
       Ejecuta tambien los anticipos de pagos

    """,
    'version': '2.0',
    'author': 'INM & LDR Soluciones Tecnológicas y Empresariales C.A',
    'category': 'Tools',
    'website': 'http://soluciones-tecno.com/',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': ['vista/res_company_view.xml',
    #'security/ir.model.access.csv',
    'vista/res_partner_view.xml',
    'vista/account_payment_view.xml',
    'vista/account_move_view.xml',
    'vista/account_journal_views.xml',
    ],
    'application': True,
}
