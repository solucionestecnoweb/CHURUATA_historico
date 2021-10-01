# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Productos(models.Model):
    _inherit = 'product.template'

    producto_terminado = fields.Selection([('s','Si'),('n','No')], required=True)