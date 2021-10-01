# -*- coding: utf-8 -*-


import logging
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError




class PosConfig(models.Model):
    _inherit = 'pos.config'

    reg_maquina=fields.Char(string="Registro de Máquina Fiscal")
    nb_identificador_caja=fields.Char(string="Nombre de identificador caja")
    ordenes_impr=fields.Boolean(default=True)