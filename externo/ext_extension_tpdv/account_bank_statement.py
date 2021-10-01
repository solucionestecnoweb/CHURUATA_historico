# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models



class AccountBankStatementLineInheret(models.Model):

    _inherit = "pos.payment"
    x_nro_ref = fields.Char(size=50,string='Nro Referencia Banco')
    code = fields.Char()
    nro_caja = fields.Char()

class PosPaymentMethodInheret(models.Model):

    _inherit = "pos.payment.method"

    type = fields.Selection([
        ('bank', 'Banco'),
        ('cash', 'Efectivo')])

class PosOrderInheret(models.Model):

    _inherit = "pos.order"

    x_chek_credi=fields.Char()
    nro_fact_seniat=fields.Integer(default=0)
    nro_fact_seniat_aux=fields.Integer()

    nro_nc_seniat=fields.Integer()
    nro_nc_seniat_aux=fields.Integer()