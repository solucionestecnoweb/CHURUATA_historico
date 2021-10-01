# -*- coding: utf-8 -*-


from odoo import api, fields, models, _ 


class Purchase(models.Model):
    _inherit = 'purchase.order'


    aux_currency_id = fields.Many2one('res.currency', string='Reference currency', help='This currency is a reference for exchange.')
    crypto_total = fields.Float(string='Crypto Total', digits=(12,8), help='Total in crypto.', readonly=True)

    @api.onchange('currency_id')
    def _ptr_by_default(self):
        if self.currency_id:
            ptr = self.env['res.currency'].search([('name','=','PTR')])
            if ptr:
                self.aux_currency_id = ptr.id
