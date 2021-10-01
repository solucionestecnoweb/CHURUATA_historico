# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
from datetime import datetime, timedelta
import base64
from io import StringIO
from odoo import api, fields, models
from datetime import date
from odoo.tools.float_utils import float_round
from odoo.exceptions import Warning

class ReporteProducto(models.TransientModel):
    _name = "stock.move.report.venezuela"

    date_from = fields.Date(string='Date From', default=lambda *a:datetime.now().strftime('%Y-%m-%d'))
    date_to = fields.Date('Date To', default=lambda *a:(datetime.now() + timedelta(days=(1))).strftime('%Y-%m-%d'))
    product = fields.Many2one(comodel_name='product.product', string='product')
    move_id = fields.Many2many(comodel_name='stock.move.line', string='Movimientos')
    

    def print_facturas(self):
        self.move_id =  self.env['stock.move.line'].search([
            ('product_id','=',self.product.id)
        ])
        return self.env.ref('libro_inventario.movimientos_producto_libro').report_action(self)
