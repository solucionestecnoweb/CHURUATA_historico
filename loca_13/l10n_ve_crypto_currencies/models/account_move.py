# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger('__name__')

class AccountMove(models.Model):
    _inherit = 'account.move'


    aux_currency_id = fields.Many2one(
        'res.currency', 
        string='Reference currency',
        #domain="[('is_crypto', '=', 1)]",
        help='This currency is a reference for exchange.')
    crypto_total = fields.Float(string='Crypto Total', digits=(12,8), help='Total in crypto.', readonly=True)


    @api.onchange('currency_id')
    def ptr_by_default(self):
        if self.currency_id:
            ptr = self.env['res.currency'].search([('name','=','PTR')])
            if ptr:
                self.aux_currency_id = ptr.id


