# -*- coding: utf-8 -*-

from odoo import api, fields, models, _ 



class Currency(models.Model):
    _inherit = 'res.currency'


    is_crypto = fields.Boolean(string='Cripto currency', help='Set true this field if you have a cryptocurrency')
    rounding = fields.Float(string='Rounding Factor', digits=(12, 8), default=0.01)


    @api.onchange('is_crypto')
    def _rounding_true(self):
        if self.is_crypto:
            self.rounding = 0.00000001
        else:
            self.rounding = 0.01


