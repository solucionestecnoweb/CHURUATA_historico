# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ResCompany(models.Model):
    _inherit = 'res.company'

    url_redirect = fields.Char(string="URL to Redirect in PoS", default="http://localhost/fiscal_13/cargar.php")  

    def get_url_redirect(self):
        return self.url_redirect