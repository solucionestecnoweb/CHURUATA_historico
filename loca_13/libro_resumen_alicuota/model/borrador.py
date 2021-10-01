# -*- coding: utf-8 -*-


import logging
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError




class ResumenAlicuota(models.Model):
    _name = 'account.move.line.resumen'

    invoice_id = fields.Many2one('account.move')
    type=fields.Char()
    state=fields.Char()
    total_con_iva = fields.Float(string=' Total con IVA')
    total_base = fields.Float(string='Total Base Imponible')
    tax_id = fields.Many2one('account.tax', string='Tipo de Impuesto')
    total_valor_iva = fields.Float(string='Total IVA')

    porcentaje_ret = fields.Float(string='Porcentaje de Retencion IVA')
    total_ret_iva = fields.Float(string='Total IVA Retenido')    
    vat_ret_id = fields.Many2one('vat.retention', string='Nro de Comprobante IVA')
    nro_comprobante = fields.Char(string='Nro de Comprobante')
    tipo_doc = fields.Char()

class AccountMove(models.Model):
    _inherit = 'account.move'

    alicuota_line_ids = fields.One2many('account.move.line.resumen', 'invoice_id', string='Resumen')

    def action_post(self):
        super().action_post()
        self.suma_alicuota_iguales_iva('no')

    def button_cancel(self):
        super().button_cancel()
        self.suma_alicuota_iguales_iva('no')
        self.state='cancel'

    def llenar(self):
        movimientos = self.env['account.move'].search([('type','!=','entry'),('state','=','posted')])
        for det_m in movimientos:
            if det_m.type=='in_invoice' or det_m.type=='in_refund' or det_m.type=='in_receipt':
                type_tax_use='purchase'
                porcentaje_ret=det_m.company_id.partner_id.vat_retention_rate
            if det_m.type=='out_invoice' or det_m.type=='out_refund' or det_m.type=='out_receipt':
                type_tax_use='sale'
                porcentaje_ret=det_m.partner_id.vat_retention_rate
            if det_m.type=='in_invoice' or det_m.type=='out_invoice':
                tipo_doc="01"
            if det_m.type=='in_refund' or det_m.type=='out_refund':
                tipo_doc="03"
            if det_m.type=='in_receipt' or det_m.type=='out_receipt':
                tipo_doc="02"
            lista_impuesto = det_m.env['account.tax'].search([('type_tax_use','=',type_tax_use)])
            for det_tax in lista_impuesto:
                base=0
                total=0
                total_impuesto=0
                valor_iva=0
                det_lin=det_m.invoice_line_ids.search([('tax_ids','=',det_tax.id),('move_id','=',det_m.id)])
                if det_lin:
                    for det_fac in det_lin:#USAR AQUI ACOMULADORES
                        if det_m.state!="cancel":
                            base=base+det_fac.price_subtotal
                            total=total+det_fac.price_total
                            id_impuesto=det_fac.tax_ids.id
                            total_impuesto=total_impuesto+(det_fac.price_total-det_fac.price_subtotal)
                            valor_iva=det_fac.tax_ids.amount
                    total_ret_iva=(total_impuesto*porcentaje_ret)/100
                    values={
                    'total_con_iva':total,
                    'total_base':base,
                    'total_valor_iva':total_impuesto,
                    'tax_id':det_fac.tax_ids.id,
                    'invoice_id':det_m.id,
                    'vat_ret_id':det_m.vat_ret_id.id,
                    'nro_comprobante':det_m.vat_ret_id.name,
                    'porcentaje_ret':porcentaje_ret,
                    'total_ret_iva':total_ret_iva,
                    'type':det_m.type,
                    'state':det_m.state,
                    'tipo_doc':tipo_doc,
                    }
                    det_m.env['account.move.line.resumen'].create(values)


    def suma_alicuota_iguales_iva(self,gen_exe):
        #raise UserError(_('xxx = %s')%self.vat_ret_id)
        if self.type=='in_invoice' or self.type=='in_refund' or self.type=='in_receipt':
            type_tax_use='purchase'
            porcentaje_ret=self.company_id.partner_id.vat_retention_rate
        if self.type=='out_invoice' or self.type=='out_refund' or self.type=='out_receipt':
            type_tax_use='sale'
            porcentaje_ret=self.partner_id.vat_retention_rate
        if self.type=='in_invoice' or self.type=='out_invoice':
            tipo_doc="01"
        if self.type=='in_refund' or self.type=='out_refund':
            tipo_doc="03"
        if self.type=='in_receipt' or self.type=='out_receipt':
            tipo_doc="02"

        if self.type in ('in_invoice','in_refund','in_receipt','out_receipt','out_refund','out_invoice'):
            if gen_exe=="no":
                lista_impuesto = self.env['account.tax'].search([('type_tax_use','=',type_tax_use),('aliquot','not in',('general','exempt'))])
            else:
                lista_impuesto=self.env['account.tax'].search([('type_tax_use','=',type_tax_use),('aliquot','in',('general','exempt'))])

            if lista_impuesto:
                for det_tax in lista_impuesto:
                    base=0
                    total=0
                    total_impuesto=0
                    valor_iva=0
                    #raise UserError(_('self.invoice_line_ids')%self.invoice_line_ids.id)
                    if gen_exe=='no':
                        det_lin=self.invoice_line_ids.search([('tax_ids','=',det_tax.id),('move_id','=',self.id)])
                    if gen_exe=='si':
                        det_lin=self.invoice_line_ids.search([('tax_ids','in',('5','6')),('move_id','=',self.id)])
                    if det_lin:
                        for det_fac in det_lin:#USAR AQUI ACOMULADORES
                            if self.state!="cancel":
                                base=base+det_fac.price_subtotal
                                total=total+det_fac.price_total
                                id_impuesto=det_fac.tax_ids.id
                                total_impuesto=total_impuesto+(det_fac.price_total-det_fac.price_subtotal)
                                valor_iva=det_fac.tax_ids.amount
                        total_ret_iva=(total_impuesto*porcentaje_ret)/100
                        values={
                        'total_con_iva':total,
                        'total_base':base,
                        'total_valor_iva':total_impuesto,
                        'tax_id':det_fac.tax_ids.id,
                        'invoice_id':self.id,
                        'vat_ret_id':self.vat_ret_id.id,
                        'nro_comprobante':self.vat_ret_id.name,
                        'porcentaje_ret':porcentaje_ret,
                        'total_ret_iva':total_ret_iva,
                        'type':self.type,
                        'state':self.state,
                        'tipo_doc':tipo_doc,
                        }
                        self.env['account.move.line.resumen'].create(values)

            if gen_exe=='no':
                self.suma_alicuota_iguales_iva('si')
                """cur_tax=self.env['account.tax'].search([('type_tax_use','=',type_tax_use),,('aliquot','in',('general','exempt'))])
                for det_taxx in cur_tax:
                    x
                cursor=self.env['account.move.line.resumen'].search([('type_tax_use','=',type_tax_use)])
                #raise UserError(_('valor_iva= %s')%valor_iva)"""

    def button_draft(self):
        super().button_draft()
        temporal=self.env['account.move.line.resumen'].search([('invoice_id','=',self.id)])
        temporal.with_context(force_delete=True).unlink()