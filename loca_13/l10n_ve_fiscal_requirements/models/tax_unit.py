# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp



class TaxUnit(models.Model):
    """ This model add Tax Unit for Venezuela."""
    _name = 'tax.unit'

    name = fields.Char(string='Reference Number', required=True, help='Gazette number')
    date = fields.Date(string='Date', required=True, help='Gazetter publication date')
    tax_unit_amount = fields.Float(string='Amount', digits=dp.get_precision('Bs per UT'), required=True)
