# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
# 
#################################################################################
from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    wk_display_stock = fields.Boolean('Display stock in POS', default=True)
    wk_stock_type = fields.Selection(
        [('available_qty', 'Available Quantity(On hand)'), ('forecasted_qty', 'Forecasted Quantity'),
         ('virtual_qty', 'Quantity on Hand - Outgoing Qty')], string='Stock Type', default='available_qty')
    wk_continous_sale = fields.Boolean('Allow Order When Out-of-Stock')
    wk_deny_val = fields.Integer('Deny order when product stock is lower than ')
    wk_error_msg = fields.Char(string='Custom message', default="Product out of stock")
    wk_hide_out_of_stock = fields.Boolean(string="Hide Out of Stock products", default=True)
