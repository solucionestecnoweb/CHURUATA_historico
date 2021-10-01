# -*- coding: utf-8 -*- 

from odoo import api, fields, models, _  


class Partner(models.Model):
    _inherit = 'res.partner'

    islr_agent = fields.Boolean(string='Income Withholding Agent', help="Check if the partner is an agent for income withholding")
    spn = fields.Boolean(string='Is it a society of natural persons', help='Indicates whether refers to asociety of natural persons')
    islr_exempt = fields.Boolean('Is it exempt from income withholding', help='Whether the individual is exempt from income withholding')
    #islr_historical_data = fields.One2many('islr.wh.historical.data', 'partner_id', string='ISLR historical data', help='Values to be used when computing Rate 2')
    purchase_islr_journal_id = fields.Many2one('account.journal', string='Journal ISLR of purchases')
    sale_islr_journal_id = fields.Many2one('account.journal', 'Journal ISLR of sales')



    """def copy(self, default=None):

        if default is None:
            default = {}
            default = default.copy()
            default.update({
                'islr_withholding_agent': 1,
                'spn': False,
                'islr_exempt': 0,
                #'islr_historical_data': []
            })

        return super().copy(default)"""