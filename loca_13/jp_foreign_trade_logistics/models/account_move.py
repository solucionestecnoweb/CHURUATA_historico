from odoo import models, fields, api, _

class AccountMove(models.Model):
    _inherit = 'account.move'

    # landed_amount_signed = fields.Monetary(string='Landed Amount Signed', currency_field='company_currency_id')
    vendor_landed_cost_id = fields.Many2one('stock.landed.cost', string='Stock Landed Cost')
    expenses_landed_cost_id = fields.Many2one('stock.landed.cost', string='Stock Landed Cost')

    # @api.depends(
    #     'line_ids.debit',
    #     'line_ids.credit',
    #     'line_ids.currency_id',
    #     'line_ids.amount_currency',
    #     'line_ids.amount_residual',
    #     'line_ids.amount_residual_currency',
    #     'line_ids.payment_id.state')
    # def _compute_amount(self):
    #     res = super(AccountMove, self)._compute_amount()
    #     if self.currency_id != self.company_currency_id:
    #         for inv in self:
    #             foreign_amount_total = inv.amount_total
    #             inv.landed_amount_signed = foreign_amount_total
    #     return res