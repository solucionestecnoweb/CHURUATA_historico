# -*- coding: utf-8 -*-


import logging
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError




class PosConfig(models.Model):
    _inherit = 'pos.order'

    nb_caja_comp=fields.Char(string="Registro de Máquina Fiscal",compute='_compute_nb_caja')
    nb_caja=fields.Char(string="Registro de nombre de la caja")
    status_impresora = fields.Char(default="no")
    tipo = fields.Char(default="venta")
    tasa_dia = fields.Float(compute="_compute_tasa")


    def _compute_tasa(self):
        tasa=0
        for selff in self:
            #lista_tasa = selff.env['res.currency.rate'].search([('currency_id', '=', self.env.company.currency_secundaria_id.id),('hora','<=',selff.date_order)],order='id ASC') # para isneiker
            lista_tasa = selff.env['res.currency.rate'].search([('hora','<=',selff.date_order)],order='id ASC')
            if lista_tasa:
                for det in lista_tasa:
                    tasa=det.rate
            selff.tasa_dia=tasa


    def _compute_nb_caja(self):
        self.nb_caja_comp=self.session_id.config_id.nb_identificador_caja
        self.nb_caja=self.nb_caja_comp

    """def refund(self):
        super().refund()
        self.nro_fact_seniat=0"""

class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    status_impresora=fields.Char(related='order_id.status_impresora')
    tipo = fields.Char(related='order_id.tipo')
