# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions

class AccountBankSatatement(models.Model):
	_inherit = "account.bank.statement.line"
	validador = fields.Boolean(value=False)



class AccountBankStatementLine(models.Model):

	_inherit = "account.bank.statement"
	_decription = "Conciliacion Bancaria por referencia"

	def button_organizar_ref(self):
		lista = self.env['account.bank.statement.line'].search([('statement_id','=',self.id)])

		for line in lista:
			#line.write({'name':"",'partner_id':""})
			verifica=line.validador
			monto=line.amount
			val_ref=line.ref
			descripcion=line.name
			var=descripcion+" Nro Ref:"+val_ref	
			var_move_line=self.env['account.move.line'].search([('ref','=',line.ref),('balance','=',monto)])
			id_partner=var_move_line.payment_id.partner_id.id
			if verifica==False:
				line.write({'name':var,'partner_id':id_partner,'validador':True})
