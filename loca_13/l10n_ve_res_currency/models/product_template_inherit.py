# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class Productos(models.Model):
    _inherit = 'product.template'

    list_price2 = fields.Float(string="Precio de Venta en Divisas")
    list_price_comp = fields.Float(string="Precio Computado", compute='_compute_monto')
    moneda_divisa_venta = fields.Many2one("res.currency", string="Moneda del precio de venta en divisas",digits=(12, 2))#,required=True
    habilita_precio_div = fields.Boolean(default=False)

    @api.onchange('list_price2','moneda_divisa_venta','habilita_precio_div')
    def _compute_monto(self):
        if self.habilita_precio_div==True:
            if self.moneda_divisa_venta:
                lista_tasa = self.env['res.currency.rate'].search([('currency_id', '=', self.moneda_divisa_venta.id)],order='id ASC')
                if lista_tasa:
                    for det in lista_tasa:
                        precio_actualizado=det.rate_real*self.list_price2
                        self.list_price_comp=precio_actualizado
                        self.list_price=precio_actualizado
                else:
                    raise ValidationError(_('Debe colocar Una tasa de conversion para esta moneda. Vaya a contabilidad-->configuracion-->Monedas y coloque la tasa'))
            if self.list_price2>0 and not self.moneda_divisa_venta:
                 raise ValidationError(_('Debe seleccionar una moneda de divisa'))
        if self.habilita_precio_div!=True:
            self.list_price_comp=0