# -*- coding: utf -*-


from odoo import api, fields, models, _  





class Partners(models.Model):
    _inherit = 'res.partner'


    muni_wh_agent = fields.Boolean(string='Retention agent', help='True if your partner is a municipal retention agent')
    purchase_jrl_id = fields.Many2one('account.journal', string='Purchase journal')
    sale_jrl_id = fields.Many2one('account.journal', string='Sales journal')
    account_ret_muni_receivable_id = fields.Many2one('account.account', string='Cuenta Retencion Clientes')
    account_ret_muni_payable_id = fields.Many2one('account.account', string='Cuenta Retencion Proveedores')
    nit = fields.Char(string='NIT', help='Old tax identification number replaced by the current RIF')
    econ_act_license = fields.Char(string='License number', help='Economic activity license number')
    nifg = fields.Char(string='NIFG', help='Number assigned by Satrin')