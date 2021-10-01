# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.tools import float_is_zero, float_compare, pycompat
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from base64 import encodestring

class AccountMove(models.Model):
    _inherit = 'account.move'
      

    def send_email_fxo(self):
        company = self.env.user.company_id
        if self.partner_id.email:
            if company.send_email_auto :
                template = self.env.ref('invoice_send_email.email_template_fxo_send_email', False)
                attachment_ids = []

                if self.vat_ret_id.id :
                    #PDF TICKET
                    attach = {}
                    result_pdf, type = self.env['ir.actions.report']._get_report_from_name('vat_retention.template_vat_wh_voucher').render_qweb_pdf(self.vat_ret_id.id)
                    attach['name'] = 'Comprobante de IVA.pdf' 
                    attach['type'] = 'binary'
                    attach['datas'] = encodestring(result_pdf)
                   # attach['datas_fname'] = 'Comprobante de IVA.pdf' 
                    attach['res_model'] = 'mail.compose.message'
                    attachment_id = self.env['ir.attachment'].create(attach)
                    attachment_ids.append(attachment_id.id)
                
                if self.wh_muni_id.id :
                    #PDF TICKET
                    attach = {}
                    result_pdf, type = self.env['ir.actions.report']._get_report_from_name('municipality_tax.template_wh_municipality_tax').render_qweb_pdf(self.wh_muni_id.id)
                    attach['name'] = 'Comprobante de Municipal.pdf' 
                    attach['type'] = 'binary'
                    attach['datas'] = encodestring(result_pdf)
                   # attach['datas_fname'] = 'Comprobante de IVA.pdf' 
                    attach['res_model'] = 'mail.compose.message'
                    attachment_id = self.env['ir.attachment'].create(attach)
                    attachment_ids.append(attachment_id.id)

                if self.isrl_ret_id.id :
                    #PDF TICKET
                    attach = {}
                    result_pdf, type = self.env['ir.actions.report']._get_report_from_name('isrl_retention.template_vat_isrl_voucher').render_qweb_pdf(self.isrl_ret_id.id)
                    attach['name'] = 'Comprobante de ISLR.pdf' 
                    attach['type'] = 'binary'
                    attach['datas'] = encodestring(result_pdf)
                   # attach['datas_fname'] = 'Comprobante de IVA.pdf' 
                    attach['res_model'] = 'mail.compose.message'
                    attachment_id = self.env['ir.attachment'].create(attach)
                    attachment_ids.append(attachment_id.id)


                mail = template.send_mail(self.id, force_send=True,email_values={'attachment_ids': attachment_ids}) #envia mail
                if mail:
                    self.message_post(body=_("Enviado email al Cliente: %s"%self.partner_id.name))
                    self.state_dte_partner = 'sent'
                    print('Correo Enviado a '+ str(self.partner_id.email))
