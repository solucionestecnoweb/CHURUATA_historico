# -*- coding: utf-8 -*-
{
    'name': ' VE Plantilla de cheques Localizacion Venezolana',
    'version': '1.0',
    'category': 'Accounting/Accounting',
    'summary': 'Impresion de cheques Venezuela',
    'description': """
Este módulo permite imprimir sus pagos en papel de cheque preimpreso.
Puede configurar la salida (diseño, información de apéndices, etc.) en la configuración de la empresa y administrar el
numeración de cheques (si usa cheques preimpresos sin números) en la configuración del diario.
    """,
    'author': 'INM & LDR Soluciones Tecnológicas y Empresariales C.A',
    'website': 'https://www.odoo.com/page/accounting',
    'depends' : ['account_check_printing'],
    'data': [
        'data/ve_check_printing.xml',
        'report/print_check.xml',
        'report/print_check_top.xml',
        'report/print_check_middle.xml',
        'report/print_check_bottom.xml',
        'vista/view.xml'
    ],
    'installable': True,
    'auto_install': True,
}
