# -*- coding: utf-8 -*-


import logging
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError




class ResumenAlicuota(models.Model):
    _name = 'account.move.line.resumen'

    invoice_id = fields.Many2one('account.move', ondelete='cascade')
    type=fields.Char()
    state=fields.Char()
    state_voucher_iva=fields.Char()
    total_con_iva = fields.Float(string=' Total con IVA')
    total_base = fields.Float(string='Total Base Imponible')

    base_general = fields.Float(string='Total Base General')
    base_reducida = fields.Float(string='Total Base Reducida')
    base_adicional = fields.Float(string='Total Base General + Reducida')

    total_exento = fields.Float(string='Total Excento')
    alicuota_general = fields.Float(string='Alicuota General')
    alicuota_reducida = fields.Float(string='Alicuota Reducida')
    alicuota_adicional = fields.Float(string='Alicuota General + Reducida')

    retenido_general = fields.Float(string='retenido General')
    retenido_reducida = fields.Float(string='retenido Reducida')
    retenido_adicional = fields.Float(string='retenido General + Reducida')    

    tax_id = fields.Many2one('account.tax', string='Tipo de Impuesto')
    total_valor_iva = fields.Float(string='Total IVA')

    porcentaje_ret = fields.Float(string='Porcentaje de Retencion IVA')
    total_ret_iva = fields.Float(string='Total IVA Retenido')    
    vat_ret_id = fields.Many2one('vat.retention', string='Nro de Comprobante IVA')
    nro_comprobante = fields.Char(string='Nro de Comprobante', compute="_nro_comp")
    tipo_doc = fields.Char()
    fecha_fact= fields.Date()
    fecha_comprobante= fields.Date()


    def _nro_comp(self):
        self.nro_comprobante=self.vat_ret_id.name

class AccountMove(models.Model):
    _inherit = 'account.move'

    alicuota_line_ids = fields.One2many('account.move.line.resumen', 'invoice_id', string='Resumen')

    def action_post(self):
        super().action_post()
        self.suma_alicuota_iguales_iva()

    def button_cancel(self):
        super().button_cancel()
        self.suma_alicuota_iguales_iva()
        self.state='cancel'

    def llenar(self):
        temporal=self.env['account.move.line.resumen'].search([])
        temporal.with_context(force_delete=True).unlink()

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

            if det_m.type in ('in_invoice','in_refund','in_receipt','out_receipt','out_refund','out_invoice'):
                lista_impuesto = det_m.env['account.tax'].search([('type_tax_use','=',type_tax_use)])
                #('aliquot','not in',('general','exempt')
                base=0
                total=0
                total_impuesto=0
                total_exento=0
                alicuota_adicional=0
                alicuota_reducida=0
                alicuota_general=0
                base_general=0
                base_reducida=0
                base_adicional=0
                retenido_general=0
                retenido_reducida=0
                retenido_adicional=0
                valor_iva=0

                for det_tax in lista_impuesto:
                    tipo_alicuota=det_tax.aliquot
                    
                    #raise UserError(_('tipo_alicuota: %s')%tipo_alicuota)
                    det_lin=det_m.invoice_line_ids.search([('tax_ids','=',det_tax.id),('move_id','=',det_m.id)])
                    if det_lin:
                        for det_fac in det_lin:#USAR AQUI ACOMULADORES
                            if det_m.state!="cancel":
                                base=base+det_fac.price_subtotal
                                total=total+det_fac.price_total
                                id_impuesto=det_fac.tax_ids.id
                                total_impuesto=total_impuesto+(det_fac.price_total-det_fac.price_subtotal)
                                if tipo_alicuota=="general":
                                    alicuota_general=alicuota_general+(det_fac.price_total-det_fac.price_subtotal)
                                    base_general=base_general+det_fac.price_subtotal
                                    valor_iva=det_fac.tax_ids.amount
                                if tipo_alicuota=="exempt":
                                    total_exento=total_exento+det_fac.price_subtotal
                                if tipo_alicuota=="reduced":
                                    alicuota_reducida=alicuota_reducida+(det_fac.price_total-det_fac.price_subtotal)
                                    base_reducida=base_reducida+det_fac.price_subtotal
                                if tipo_alicuota=="additional":
                                    alicuota_adicional=alicuota_adicional+(det_fac.price_total-det_fac.price_subtotal)
                                    base_adicional=base_adicional+det_fac.price_subtotal
                        total_ret_iva=(total_impuesto*porcentaje_ret)/100
                        retenido_general=(alicuota_general*porcentaje_ret)/100
                        retenido_reducida=(alicuota_reducida*porcentaje_ret)/100
                        retenido_adicional=(alicuota_adicional*porcentaje_ret)/100
                if det_m.type=='in_refund' or det_m.type=='out_refund':
                    base=-1*base
                    total=-1*total
                    total_impuesto=-1*total_impuesto
                    alicuota_general=-1*alicuota_general
                    valor_iva=-1*valor_iva
                    total_exento=-1*total_exento
                    alicuota_reducida=-1*alicuota_reducida
                    alicuota_adicional=-1*alicuota_adicional
                    total_ret_iva=-1*total_ret_iva
                    base_adicional=-1*base_adicional
                    base_reducida=-1*base_reducida
                    base_general=-1*base_general
                    retenido_general=-1*retenido_general
                    retenido_reducida=-1*retenido_reducida
                    retenido_adicional=-1*retenido_adicional

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
                'state_voucher_iva':det_m.vat_ret_id.state,
                'tipo_doc':tipo_doc,
                'total_exento':total_exento,
                'alicuota_reducida':alicuota_reducida,
                'alicuota_adicional':alicuota_adicional,
                'alicuota_general':alicuota_general,
                'fecha_fact':det_m.date,
                'fecha_comprobante':det_m.vat_ret_id.voucher_delivery_date,
                'base_adicional':base_adicional,
                'base_reducida':base_reducida,
                'base_general':base_general,
                'retenido_general':retenido_general,
                'retenido_reducida':retenido_reducida,
                'retenido_adicional':retenido_adicional,
                }
                det_m.env['account.move.line.resumen'].create(values)


    def suma_alicuota_iguales_iva(self):
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
            # ****** AQUI VERIFICA SI LAS LINEAS DE FACTURA TIENEN ALICUOTAS *****
            verf=self.invoice_line_ids
            #raise UserError(_('verf= %s')%verf)
            for det_verf in verf:
                #raise UserError(_('det_verf.tax_ids.id= %s')%det_verf.tax_ids.id)
                if not det_verf.tax_ids.id:
                    raise UserError(_('Las Lineas de la Factura deben tener un tipo de alicuota o impuestos'))
            # ***** FIN VERIFICACION
            lista_impuesto = self.env['account.tax'].search([('type_tax_use','=',type_tax_use)])
            #('aliquot','not in',('general','exempt')
            base=0
            total=0
            total_impuesto=0
            total_exento=0
            alicuota_adicional=0
            alicuota_reducida=0
            alicuota_general=0
            base_general=0
            base_reducida=0
            base_adicional=0
            retenido_general=0
            retenido_reducida=0
            retenido_adicional=0
            valor_iva=0

            for det_tax in lista_impuesto:
                tipo_alicuota=det_tax.aliquot
                
                #raise UserError(_('tipo_alicuota: %s')%tipo_alicuota)

                det_lin=self.invoice_line_ids.search([('tax_ids','=',det_tax.id),('move_id','=',self.id)])
                if det_lin:
                    for det_fac in det_lin:#USAR AQUI ACOMULADORES
                        if self.state!="cancel":
                            base=base+det_fac.price_subtotal
                            total=total+det_fac.price_total
                            id_impuesto=det_fac.tax_ids.id
                            total_impuesto=total_impuesto+(det_fac.price_total-det_fac.price_subtotal)
                            if tipo_alicuota=="general":
                                alicuota_general=alicuota_general+(det_fac.price_total-det_fac.price_subtotal)
                                base_general=base_general+det_fac.price_subtotal
                                valor_iva=det_fac.tax_ids.amount
                            if tipo_alicuota=="exempt":
                                total_exento=total_exento+det_fac.price_subtotal
                            if tipo_alicuota=="reduced":
                                alicuota_reducida=alicuota_reducida+(det_fac.price_total-det_fac.price_subtotal)
                                base_reducida=base_reducida+det_fac.price_subtotal
                            if tipo_alicuota=="additional":
                                alicuota_adicional=alicuota_adicional+(det_fac.price_total-det_fac.price_subtotal)
                                base_adicional=base_adicional+det_fac.price_subtotal
                    total_ret_iva=(total_impuesto*porcentaje_ret)/100
                    retenido_general=(alicuota_general*porcentaje_ret)/100
                    retenido_reducida=(alicuota_reducida*porcentaje_ret)/100
                    retenido_adicional=(alicuota_adicional*porcentaje_ret)/100
            if self.type=='in_refund' or self.type=='out_refund':
                base=-1*base
                total=-1*total
                total_impuesto=-1*total_impuesto
                alicuota_general=-1*alicuota_general
                valor_iva=-1*valor_iva
                total_exento=-1*total_exento
                alicuota_reducida=-1*alicuota_reducida
                alicuota_adicional=-1*alicuota_adicional
                total_ret_iva=-1*total_ret_iva
                base_adicional=-1*base_adicional
                base_reducida=-1*base_reducida
                base_general=-1*base_general
                retenido_general=-1*retenido_general
                retenido_reducida=-1*retenido_reducida
                retenido_adicional=-1*retenido_adicional

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
            'state_voucher_iva':self.vat_ret_id.state,
            'tipo_doc':tipo_doc,
            'total_exento':total_exento,
            'alicuota_reducida':alicuota_reducida,
            'alicuota_adicional':alicuota_adicional,
            'alicuota_general':alicuota_general,
            'fecha_fact':self.date,
            'fecha_comprobante':self.vat_ret_id.voucher_delivery_date,
            'base_adicional':base_adicional,
            'base_reducida':base_reducida,
            'base_general':base_general,
            'retenido_general':retenido_general,
            'retenido_reducida':retenido_reducida,
            'retenido_adicional':retenido_adicional,
            }
            self.env['account.move.line.resumen'].create(values)

            #raise UserError(_('valor_iva= %s')%valor_iva)

    def button_draft(self):
        super().button_draft()
        for selff in self:
            temporal=selff.env['account.move.line.resumen'].search([('invoice_id','=',selff.id)])
            temporal.with_context(force_delete=True).unlink()