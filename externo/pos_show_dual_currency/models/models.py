from odoo import fields, models
class PosConfig(models.Model):
    _inherit = "pos.config"

    show_dual_currency = fields.Boolean(
        "Show dual currency", help="Show Other Currency in POS", default=True
    )

    rate_company = fields.Float(string='Rate', related='currency_id.rate')

    show_currency = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env['res.currency'].search([('name', '=', 'USD')], limit=1))

    show_currency_rate = fields.Float(string='Rate', related='show_currency.rate')

    show_currency_rate_real = fields.Float(string='Rate', related='show_currency.rate_real')# darrell

    show_currency_symbol = fields.Char(related='show_currency.symbol')

    show_currency_position = fields.Selection([('after', 'After'),
                      ('before', 'Before'),
                      ],related='show_currency.position')

    default_location_src_id = fields.Many2one(
        "stock.location", related="picking_type_id.default_location_src_id"
    )
