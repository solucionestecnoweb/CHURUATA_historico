# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _

class res_company(models.Model):
    _inherit = "res.company"

    
    send_email_auto = fields.Boolean( string=u'Enviar Email Automaticamente',default=False)

    send_xml    = fields.Boolean( string=u'Incluir XML',default=False)
    send_ticket = fields.Boolean( string=u'Incluir ticket',default=False)
    send_pdf    = fields.Boolean( string=u'Incluir PDF',default=False)
    