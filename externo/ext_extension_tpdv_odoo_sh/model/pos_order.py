# -*- coding: utf-8 -*-


import logging
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError




class PosConfig(models.Model):
    _inherit = 'pos.order'

    url_nota_credito=fields.Char(string="Imprimir Nota de Credito",readonly="True")
    id_order_afectado=fields.Char()
    link=fields.Char(compute='_compute_link')

    #@api.depends('state')
    @api.onchange('state')
    def _compute_link(self):
        valor_url='http://localhost/fiscal_13/nota_credito.php'
        for selff in self:
            selff.link=valor_url+'?id_order_afectado='+str(selff.id_order_afectado)+'&order_nc='+str(selff.id)
            selff.url_nota_credito=selff.link

class PosMakePayment(models.TransientModel):
    _inherit = 'pos.make.payment'

    def check(self):
        res = super(PosMakePayment, self).check()
        ordenes = self.env['pos.order'].browse(self.env.context.get('active_id', False))
        pos_reference=ordenes.pos_reference
        actualiza=self.env['pos.order'].search([('pos_reference','=',pos_reference),('amount_total','>','0')])
        for det in actualiza:
            id_order_org=det.id
        ordenes.id_order_afectado=id_order_org
        ordenes.tipo="devolucion"

        #raise UserError(_('pos_reference= %s')%ordenes.pos_reference)