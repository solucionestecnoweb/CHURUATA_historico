# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, api


_logger = logging.getLogger('__name__')

class Company(models.Model):

    _inherit = 'res.company'

    
    def _get_country(self):
        country = self.env['res.country'].search([('id', '=', '238')], limit=1)
        if country.id:
            return country.id



    country_id = fields.Many2one('res.country', string="Country", default=_get_country)
    municipality_id = fields.Many2one('res.country.state.municipality', 'Municipality')
    parish_id = fields.Many2one('res.country.state.municipality.parish', 'Parish')

    @api.model
    def _address_fields(self):
        address_fields = set(super(res_partner, self)._address_fields())
        address_fields.add('municipality_id')
        address_fields.add('parish_id')
        return list(address_fields)

