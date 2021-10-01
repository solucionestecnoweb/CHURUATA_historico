# -*- coding: utf-8 -*-


from odoo import api, fields, models, _




class Partners(models.Model):
    _inherit = 'res.partner'

    ret_agent_isrl= fields.Boolean(string='Retention agent ISLR', help='True if your partner is retention agent')
    sale_isrl_id = fields.Many2one('account.journal', string='Journal')
    account_isrl_receivable_id = fields.Many2one('account.account', string='Cuenta ISLR Retencion a Cobrar (Clientes)')
    account_isrl_payable_id = fields.Many2one('account.account', string='Cuenta ISLR Retencion a Pagar (Proveedores)')
    #firma = fields.Binary(string='Firma y Sello')
    