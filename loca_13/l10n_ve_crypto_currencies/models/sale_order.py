# -*- coding: utf-8 -*-


import logging
from odoo import api, fields, models, _ 
from odoo.exceptions import ValidationError

_logger = logging.getLogger('__name__')


class SaleOrde(models.Model):
    _inherit = 'sale.order'


    @api.model
    def ptr_by_default(self):
        ptr = self.env['res.currency'].search([('name','=','PTR')])
        if ptr:
            return  ptr.id
        else:
            return 0

    aux_currency_id = fields.Many2one('res.currency', 
        string='Reference currency', 
        help='This currency is a reference for exchange.',
        #domain="[('is_crypto', '=', 1)]",
        default=ptr_by_default)
    crypto_total = fields.Float(string='Crypto Total', digits=(12,8), help='Total in crypto.', readonly=True)


  
