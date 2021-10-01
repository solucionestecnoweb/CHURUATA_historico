# -*- coding: utf-8 -*-


from datetime import datetime
from odoo import api, models, fields, _



class Partner(models.Model):
    _inherit = 'res.partner'



    registration_date = fields.Date(string='Registrarion Date', required="True", default=datetime.now())
    
