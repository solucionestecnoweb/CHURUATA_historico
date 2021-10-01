# -*- coding: utf-8 -*-

import logging
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


_logger = logging.getLogger('__name__')

class AccountMove(models.Model):
    _inherit = 'account.move'

    isrl_ret_id = fields.Many2one('isrl.retention', string='ISLR', copy=False, help='ISLR')

    # Main Function
    def action_post(self):
        super().action_post()
        bann=0
        bann=self.verifica_exento_islr()
        if bann>0:
            self.create_retention()
            self.unifica_alicuota_iguales_islr()

    def unifica_alicuota_iguales_islr(self):
        lista_impuesto = self.env['islr.rates'].search([('code','!=','000')])
        #raise UserError(_('lista_impuesto = %s')%lista_impuesto)
        for det_tax in lista_impuesto:
            #raise UserError(_('det_tax.id = %s')%det_tax.id)
            lista_mov_line = self.env['isrl.retention.invoice.line'].search([('retention_id','=',self.isrl_ret_id.id),('code','=',det_tax.code)])
            #raise UserError(_('lista_mov_line = %s')%lista_mov_line)
            #amount_untaxed=0
            base=0
            #amount_vat_ret=0
            retention=0
            #retention_amount=0
            sustraendo=0
            total=0
            if lista_mov_line:
                for det_mov_line in lista_mov_line:                
                    base=base+det_mov_line.base
                    retention=retention+det_mov_line.retention
                    sustraendo=det_mov_line.sustraendo
                    #total=total+det_mov_line.total

                    nombre=det_mov_line.name.id
                    #raise UserError(_('nombre1 = %s')%nombre)
                    retention_id=det_mov_line.retention_id.id
                    cantidad=det_mov_line.cantidad
                    code=det_mov_line.code
                #raise UserError(_('nombre2 = %s')%nombre)
                total=retention-sustraendo
                lista_mov_line.unlink()
                islr_obj = self.env['isrl.retention.invoice.line']
                values={
                'name':nombre,
                'retention_id':retention_id,
                'cantidad':cantidad,
                'code':code,
                'base':base,
                'retention':retention,
                'sustraendo':sustraendo,
                'total':total,
                }
                islr_obj.create(values)
        #lista_mov = self.env['isrl.retention'].search([('id','=',self.isrl_ret_id.id)])
        #lista_mov.write({'vat_retentioned':7777})

    def create_retention(self):
        active=False
        if self.type in ('in_invoice','out_invoice','in_refund','out_refund','in_receipt','out_receipt'):#darrell
            if self.isrl_ret_id.id:
                pass
            else:
                if self.company_id.confg_ret_proveedores=="c":
                    if self.company_id.partner_id.ret_agent_isrl:
                        active=True
                if self.company_id.confg_ret_proveedores=="p":
                    if self.partner_id.ret_agent_isrl:
                        active=True

                if active==True:
                    if self.partner_id.people_type :
                        self.isrl_ret_id = self.env['isrl.retention'].create({
                            'invoice_id': self.id,
                            'partner_id': self.partner_id.id,
                            'move_id':self.id,
                            'invoice_number':self.invoice_number,
                            'date_move':self.date,
                            'date_isrl':self.date,
                        })
                        for item in self.invoice_line_ids:
                            if item.concept_isrl_id:
                                for rate in item.concept_isrl_id.rate_ids:
                                    #raise UserError(_('item.price_subtotal=%s ')%rate.min)
                                    if self.partner_id.people_type == rate.people_type and  self.conv_div_nac(item.price_subtotal) > rate.min  :
                                        base = item.price_subtotal * (rate.subtotal / 100)
                                        subtotal =  base * (rate.retention_percentage / 100)
                                        #raise UserError(_('base = %s')%base)
                                        self.vat_isrl_line_id = self.env['isrl.retention.invoice.line'].create({
                                            'name': item.concept_isrl_id.id,
                                            'code':rate.code,
                                            'retention_id': self.isrl_ret_id.id,
                                            'cantidad': rate.retention_percentage,
                                            'base': self.conv_div_nac(base),
                                            'retention': self.conv_div_nac(subtotal),
                                            'sustraendo': rate.subtract,
                                            'total': self.conv_div_nac(subtotal - rate.subtract), # AQUI
                                        })
                    else :
                        raise UserError("the Partner does not have identified the type of person.")

        if self.type =='in_invoice' or self.type =='in_refund' or self.type =='in_receipt':
            if active==True:
                self.isrl_ret_id.action_post()


    def conv_div_nac(self,valor):
        self.currency_id.id
        fecha_contable_doc=self.date
        monto_factura=self.amount_total
        valor_aux=0
        #raise UserError(_('moneda compañia: %s')%self.company_id.currency_id.id)
        if self.currency_id.id!=self.company_id.currency_id.id:
            tasa= self.env['res.currency.rate'].search([('currency_id','=',self.currency_id.id),('name','<=',self.date)],order="name asc")
            for det_tasa in tasa:
                if fecha_contable_doc>=det_tasa.name:
                    valor_aux=det_tasa.rate
            rate=round(1/valor_aux,2)  # LANTA
            #rate=round(valor_aux,2)  # ODOO SH
            resultado=valor*rate
        else:
            resultado=valor
        return resultado

    def verifica_exento_islr(self):
        acum=0
        #raise UserError(_('self = %s')%self.id)
        puntero_move_line = self.env['account.move.line'].search([('move_id','=',self.id),('account_internal_type','=','other')])
        for det_puntero in puntero_move_line:
            if det_puntero.product_id.product_tmpl_id.concept_isrl_id.id:
                acum=acum+1
        #raise UserError(_('acum: %s ')%acum)
        return acum
