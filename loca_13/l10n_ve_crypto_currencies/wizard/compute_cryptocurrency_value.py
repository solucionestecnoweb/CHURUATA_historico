# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger('__name__')



FIAT_CURRENCY = [
    ('usd','USD'),
    ('euro', 'EURO'),
    ('ves','VES'),
]

class ComputeCryptoCurrencyValue(models.TransientModel):
    _name = 'compute.crypto.value'

    @api.model
    def _ptr_by_default(self):
        ptr = self.env['res.currency'].search([('name','=','PTR')])
        if ptr:
            return  ptr.id
        else:
            return 0

    fiat_currency = fields.Selection(selection=FIAT_CURRENCY, default='ves', required=True)
    value1 = fields.Float(string="Value", required=True)
    crypto_id = fields.Many2one(
        'res.currency',
        #domain="[('is_crypto', '=', 1)]",
        string='Cryptocurrency',
        required=True,
        default=_ptr_by_default)
    tasa = fields.Float(string='Tasa', required=True)
    result = fields.Float(string='Result', digits=(12,8), readonly=True)
    id_record = fields.Char(string='id_record')
    act_model = fields.Char(string='model', help='technical use')
    flag1 = fields.Boolean(string='flag1', help='technical use')



    def compute_value(self):
        """Compute the value in cryptocurrencies."""
        result = 0.00000000
        if self.value1 and self.tasa:
            result = (self.value1 * 1) / self.tasa 
            self.result = result
            if not self.flag1:
                self.id_record = self.env.context.get('active_id')
                self.act_model = self.env.context.get('active_model')
                self.flag1 = True
            return {
                'view_mode': 'form',
                'res_model': 'compute.crypto.value',
                'res_id': self.id,
                'view_id': False,
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context': {"default_act_model":self.act_model,  "default_result": result, "default_id_record": self.id_record,},
            }
        else:
            raise UserError("You need set all values first.")


    def add_crypto_value_invoice(self):
        model = self.act_model

        if model == 'account.move':
            invoice = self.env['account.move'].search([('id', '=', self.id_record)])
            if invoice:
                invoice.write({'crypto_total': self.result, 'aux_currency_id': self.crypto_id})
        
        if model == 'sale.order':
            sale_order = self.env['sale.order'].search([('id', '=', self.id_record)])
            if sale_order:
                sale_order.write({'crypto_total': self.result, 'aux_currency_id': self.crypto_id})

        if model == 'purchase.order':
            purchase_order = self.env['purchase.order'].search([('id', '=', self.id_record)])
            if purchase_order:
                purchase_order.write({'crypto_total': self.result, 'aux_currency_id': self.crypto_id})
