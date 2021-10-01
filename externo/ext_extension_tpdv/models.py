# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models
from odoo.exceptions import ValidationError

class Datospersonales(models.Model):
	_inherit = 'account.tax'# aqui con la instruccion _inherit le decimos a odoo que en la tabla datos.per se hara una inclucion o herencia
	#tipo_tasa=fields.Selection([('0', 'Exento'), ('1', 'Tasa GRAL'), ('2', 'Tasa REDU'),('3', 'Tasa ADIC')], string='Tipo de Tasa') # campo a incluir que es la cedula
	tipe_taxe = fields.Integer(string='Tipo de Tasa', compute='_compute_tipo_tasa')
	tipo_tasa = fields.Integer(string='Tipo de Tasa')

	#@api.depends('aliquot')
	@api.onchange('aliquot')
	def _compute_tipo_tasa(self):
		for selff in self:
			if selff.aliquot=="exempt":
				selff.tipo_tasa=0
				selff.tipe_taxe=0
			if selff.aliquot=="general":
				selff.tipo_tasa=1
				selff.tipe_taxe=1
			if selff.aliquot=="reduced":
				selff.tipo_tasa=2
				selff.tipe_taxe=2
			if selff.aliquot=="additional":
				selff.tipo_tasa=3
				selff.tipe_taxe=3
			if selff.aliquot=="no_tax_credit":
				selff.tipo_tasa=4
				selff.tipe_taxe=4
			if not  selff.aliquot:
				selff.tipo_tasa=100
				selff.tipe_taxe=100
