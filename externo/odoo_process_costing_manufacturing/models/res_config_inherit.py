# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    porcentaje_ganancia = fields.Float(related='company_id.porcentaje_ganancia')

class Company(models.Model):
    _inherit = 'res.company'

    porcentaje_ganancia = fields.Float(required=True)