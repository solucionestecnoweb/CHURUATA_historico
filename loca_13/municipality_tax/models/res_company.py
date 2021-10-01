# -*- coding: utf-8 -*-


from odoo import api, fields, models, _ 





class Company(models.Model):
    _inherit = 'res.company'


    nit = fields.Char(string='NIT', help='Old tax identification number replaced by the current RIF')
    econ_act_license = fields.Char(string='License number', help='Economic activity license number', required=True)
    nifg = fields.Char(string='NIFG', help='Number assigned by Satrin', required=True)