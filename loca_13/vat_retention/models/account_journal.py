# -*- coding: utf-8 -*-


import logging
from datetime import datetime, date
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError




class Partners(models.Model):
    _inherit = 'account.journal'

    tipo_doc = fields.Selection([('nc', 'Nota de Credito'),('nb', 'Nota de Debito'),('fc','Factura')])