# -*- coding: utf-8 -*-
{
    'name': "Prestamo a empleados",

    'summary': """Prestamo a empleados""",

    'description': """
       Prestamo a empleados.
    """,
    'version': '13.0',
    'author': 'INM & LDR Soluciones Tecnológicas y Empresariales C.A',
    'category': 'Tools',
    'website': 'http://soluciones-tecno.com/',

    # any module necessary for this one to work correctly
    'depends': ['hr','hr_payroll'],

    # always loaded
    'data': [
    'views/prestamo_view.xml',
    #'views/hr_payslip_view.xml',
    'security/ir.model.access.csv',
    ],
    'application': True,
    'active':False,
    'auto_install': False,
}
