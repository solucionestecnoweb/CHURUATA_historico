from odoo import api, fields, models, _




class Partners(models.Model):
    _inherit = 'res.partner'

    account_anti_receivable_id = fields.Many2one('account.account', string='Cuenta Anticipo a Cobrar (Clientes)')
    account_anti_payable_id = fields.Many2one('account.account', string='Cuenta Anticipo a Pagar (Proveedores)')