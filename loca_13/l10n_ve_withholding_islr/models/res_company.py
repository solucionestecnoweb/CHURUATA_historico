# -*- coding: utf-8 -*-


from odoo import api, fields, models, _  



class Company(models.Model):
    _inherit = 'res.company'


    automatic_income_wh = fields.Boolean(string='Automatic Income Withhold', help='When True, supplier income withholding will be check and validate automatically', default=False)
    propagate_invoice_date_to_income = fields.Boolean(
        string='Propagate Invoice date to income withholding',
        help='Propagate Invoice date to income withholding. By default is in false.', default=False)

