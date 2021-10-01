from odoo import models, fields, api, _

class AccountMove(models.Model):
    _inherit = 'account.move'

    # picking_ids = fields.Many2many('stock.picking','Pickings')
    picking_ids = fields.One2many('stock.picking', 'invoice_id', string='Pickings')

    @api.onchange('picking_ids')
    def _onchange_picking_ids(self):
        for picking in self.picking_ids:
            picking.invoice_id = self.id
            picking._onchange_invoice_id()
