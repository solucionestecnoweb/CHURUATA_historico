# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields,models,api,_
import datetime
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero
from datetime import datetime

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    picking_type_id = fields.Many2one('stock.picking.type')