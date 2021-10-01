# -*- coding: utf-8 -*-


from odoo import api, fields, models, _




class Partners(models.Model):
    _inherit = 'res.partner'

    ret_agent = fields.Boolean(string='Retention agent', help='True if your partner is retention agent')
    purchase_jrl_id = fields.Many2one('account.journal', string='Purchase journal')
    sale_jrl_id = fields.Many2one('account.journal', string='Sales journal')
    ret_jrl_id = fields.Many2one('account.journal', string='Diario de Retenciones')
    account_ret_receivable_id = fields.Many2one('account.account', string='Cuenta Retencion a Cobrar (Clientes)')
    account_ret_payable_id = fields.Many2one('account.account', string='Cuenta Retencion a Pagar (Proveedores)')
    doc_type = fields.Selection([('v','V'),('e','E'),('j','J'),('g','G'),('p','P'),('c','C')], required=True)
    #doc_type = fields.Selection([('V','V'),('E','E'),('J','J'),('G','G'),('P','P'),('c','C')], required=True)