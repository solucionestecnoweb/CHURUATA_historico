# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from datetime import timedelta, date, datetime
from odoo.exceptions import UserError
#Moneda..
class CurrencyRate(models.Model):
    _inherit = "res.currency.rate"

    hora = fields.Datetime('Fecha y Hora', default=lambda self: fields.datetime.today(), required=True)
    #name = fields.Datetime('Fecha y Hora', default=lambda self: fields.datetime.today(), required=True)
    rate_real = fields.Float(digits=(12, 2), help='se introduce la tasa real del mercado')
    rate = fields.Float(digits=(12, 20), help='The rate of the currency to the currency of rate 1')
    _sql_constraints = [('unique_name_per_day', 'CHECK(1=1)', 'Only one currency rate per day allowed!')]

    @api.onchange('rate_real', 'hora')
    def fecha_y_hora(self):
        hoy = datetime.now()
        tasa_real=0.000000000000000000000000000000001
        if self.rate_real:
            tasa_real=self.rate_real
        rate = (1 /tasa_real)
        #raise UserError(_("Rate=%s")%rate)
        self.rate = rate
        lista_tasa = self.env['res.currency.rate'].search([('name','=',hoy)],order='id asc')
        for det in lista_tasa:
            lista_tasa.write({
                'name': (datetime.now() - timedelta(days=(1))),
                })
        self.convercion_precio_product()
        #self.name=datetime.now() - timedelta(days=(1))

    def convercion_precio_product(self):
        lista_product = self.env['product.template'].search([('moneda_divisa_venta', '=', self.currency_id.id)],order='id asc')
        if lista_product:
            for cor in lista_product:
                precio=cor.list_price2*self.rate_real
                cor.list_price=precio

class Currency(models.Model):
    _inherit = "res.currency"

    rate_real = fields.Float(compute='_compute_tasa_real', digits=(12, 2), help='se introduce la tasa real del mercado')
    rate = fields.Float(compute='_compute_current_rate', string='Current Rate', digits=(12, 20),
                        help='The rate of the currency to the currency of rate 1.')
    rate_rounding = fields.Float(digits=(12, 9), help='la tasa inversa del mercado')

    @api.depends('rate_ids.rate_real')
    def _compute_tasa_real(self):
        lista_tasa = self.env['res.currency.rate'].search([('currency_id', '=', self.id)],order='id asc')
        if lista_tasa:
            for tasa in lista_tasa:
                tasa_actual=tasa.rate_real
                tasa_actual_inv=tasa.rate
        else:
            tasa_actual=1
            tasa_actual_inv=1
        self.rate_real=tasa_actual
        self.rate=tasa_actual_inv
        self.convercion_precio_product2()

    def convercion_precio_product2(self):
        lista_product = self.env['product.template'].search([('moneda_divisa_venta', '=', self.id)],order='id asc')
        if lista_product:
            for cor in lista_product:
                precio=cor.list_price2*self.rate_real
                cor.list_price=precio