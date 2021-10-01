# -*- coding: utf-8 -*-
{
    'name': "Enviar Email de Forma Automatica",

    'summary': """
       Enviar un en email de forma automatica al momento de validar una factura """,
    
    'description': """
        Enviar un en email de forma automatica al momento de validar una factura y podemos configura que documento podemos poner en el adjunto """,

    'author': "FLEXXOONE",
    'website': "http://www.flexxoone.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
       
         'views/email_template.xml',
         'views/res_parnet_mail.xml',
         'views/account_move.xml'
        
    ],
    # only loaded in demonstration mode
    
}