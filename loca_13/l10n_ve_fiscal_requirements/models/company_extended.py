# -*- coding: utf-8 -*-


from odoo import api, fields, models, _


class CompanyInherit(models.Model):
    _inherit = 'res.company'

    vat = fields.Char(related='partner_id.vat', string="Tax ID", readonly=False)
    confg_ret_proveedores = fields.Selection([
        ('c','La Compañia'),
        ('p','Del Proveedor'),
    ], string='Type of taxpayer', default="c")
    type_taxpayer = fields.Selection([
        ('legal','Legal'),
        ('natural','Natural'),
        ('government', 'Government'),
    ], string='Type of taxpayer')
    fiscal_printer = fields.Boolean(string='Fiscal printer')
    damaged_invo_id = fields.Many2one('account.journal', string='Journal')
    acct_id = fields.Many2one('account.journal', string='Account')