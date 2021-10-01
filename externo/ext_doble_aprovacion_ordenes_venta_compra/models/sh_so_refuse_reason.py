# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.


from odoo import fields, models, api

class SORefuseReason(models.Model):
    _name="sh.so.refuse.reason"
    _description="Refuse Reason for Sale Order"
    
    name = fields.Char(string="Refuse Reason")

