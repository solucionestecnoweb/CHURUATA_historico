# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


_logger = logging.getLogger('__name__')

class RetentionVat(models.Model):
    """This is a main model for rentetion vat control."""
    _inherit= 'vat.retention'


    @api.model
    def create(self, vals):
        partners=vals['type']
        # NUEVO
        id_factura=vals['invoice_id']
        #del vals['partners']
        #raise UserError(_('Angel = %s')%id_factura)

        if vals.get('name', 'New') == 'New':
            _logger.info("\n\n\n vals.get.tpye %s \n\n\n", vals.get('type', 'in_invoice'))
            if partners=='in_invoice' or partners=='in_refund' or partners=='in_receipt':
                # NUEVO CODIGO
                historial = self.env['account.history.invoice'].search([('invoice_id','=',id_factura),('existe_doc_iva','=',True)])
                if historial:
                    for det_historial in historial:
                        if det_historial.nro_comprobante_iva:
                            iva_nro_comprobante=det_historial.nro_comprobante_iva
                else:
                    iva_nro_comprobante=self.env['ir.sequence'].next_by_code('purchase.vat.retention.voucher.number') or '/'
                 #FIN NUEVO CODIGO
                vals['name'] = iva_nro_comprobante
                _logger.info("\n\n\n vals[name] %s \n\n\n",vals['name'])
            else:
                vals['name']= '00000000'
        return super().create(vals)

    def get_name(self):
        '''metodo que crea el Nombre del asiento contable si la secuencia no esta creada, crea una con el
        nombre: 'l10n_ve_cuenta_retencion_iva'''

        history = self.env['account.history.invoice'].search([('invoice_id','=',self.invoice_id.id),('existe_doc_iva','=',True)])
        #raise UserError(_('history = %s')%history)
        if not history:
            #raise UserError(_('hola'))
            self.ensure_one()
            SEQUENCE_CODE = 'l10n_ve_cuenta_retencion_iva'
            company_id = 1
            IrSequence = self.env['ir.sequence'].with_context(force_company=1)
            name = IrSequence.next_by_code(SEQUENCE_CODE)

            # si aún no existe una secuencia para esta empresa, cree una
            if not name:
                IrSequence.sudo().create({
                    'prefix': 'RET_IVA/',
                    'name': 'Localización Venezolana Retenciones IVA %s' % 1,
                    'code': SEQUENCE_CODE,
                    'implementation': 'no_gap',
                    'padding': 8,
                    'number_increment': 1,
                    'company_id': 1,
                })
                name = IrSequence.next_by_code(SEQUENCE_CODE)
        else:
            for det_history in history:
                name=det_history.nro_asiento_iva
        return name



class MUnicipalityTax(models.Model):
    _inherit = 'municipality.tax'

    @api.model
    def create(self, vals):
        # NUEVO
        id_factura=vals['invoice_id']
        #raise UserError(_('TIPO yy = %s')%id_factura)

        if vals.get('name', 'New') == 'New':
            _logger.info("\n\n\n vals.get.tpye %s \n\n\n", vals.get('type', 'in_invoice'))
            #if vals.get('type', 'in_invoice') == 'in_invoice':
            #raise UserError(_('TIPO yy = %s')%vals['type'])
            if vals['type']=="in_invoice" or vals['type']=="in_refund" or vals['type']=="in_receipt":
                historial = self.env['account.history.invoice'].search([('invoice_id','=',id_factura),('existe_doc_muni','=',True)])
                if historial:
                    for det_historial in historial:
                        if det_historial.nro_comprobante_municipal:
                            muni_nro_comprobante=det_historial.nro_comprobante_municipal
                else:
                    muni_nro_comprobante=self.env['ir.sequence'].next_by_code('purchase.muni.wh.voucher.number') or '/'

                vals['name'] = muni_nro_comprobante
                _logger.info("\n\n\n vals[name] %s \n\n\n",vals['name'])
            else:
                #vals['name'] = '/'
                vals['name'] = '00000000'
        return super().create(vals)


    def get_name(self):
        '''metodo que crea el Nombre del asiento contable si la secuencia no esta creada, crea una con el
        nombre: 'l10n_ve_cuenta_retencion_iva'''

        history = self.env['account.history.invoice'].search([('invoice_id','=',self.invoice_id.id),('existe_doc_muni','=',True)])
        #raise UserError(_('history = %s')%history)
        if not history:
            self.ensure_one()
            SEQUENCE_CODE = 'l10n_ve_cuenta_retencion_municipal'
            company_id = 1
            IrSequence = self.env['ir.sequence'].with_context(force_company=1)
            name = IrSequence.next_by_code(SEQUENCE_CODE)

            # si aún no existe una secuencia para esta empresa, cree una
            if not name:
                IrSequence.sudo().create({
                    'prefix': 'RET_MUN/',
                    'name': 'Localización Venezolana Retenciones Municipales %s' % 1,
                    'code': SEQUENCE_CODE,
                    'implementation': 'no_gap',
                    'padding': 8,
                    'number_increment': 1,
                    'company_id': 1,
                })
                name = IrSequence.next_by_code(SEQUENCE_CODE)
        else:
            for det_history in history:
                name=det_history.nro_asiento_municipal
        return name

class RetentionVat(models.Model):
   
    _inherit = 'isrl.retention'

    def ejecuta(self):
        #super().action_post()
        #raise UserError(_('fact id = %s')%self.invoice_id.id)
        id_factura=self.invoice_id.id
        customer = ('out_invoice','out_refund','out_receipt')
        vendor   = ('in_invoice','in_refund','in_receipt')
        #name_asiento = self.env['ir.sequence'].next_by_code('purchase.isrl.retention.account')
        if self.invoice_id.company_id.partner_id.sale_isrl_id.id:

            self.state =  'done' 
            if self.invoice_id.type in vendor:
                historial = self.env['account.history.invoice'].search([('invoice_id','=',id_factura),('existe_doc_islr','=',True)]) #1
                if historial:
                    for det_historial in historial:
                        if det_historial.nro_comprobante_islr:
                            islr_nro_comprobante=det_historial.nro_comprobante_islr
                else:
                    islr_nro_comprobante=self.env['ir.sequence'].next_by_code('purchase.isrl.retention.voucher.number')
                #raise UserError(_('islr_nro_comprobante = %s')%islr_nro_comprobante)
                self.name=islr_nro_comprobante
            else:
                pass
            #self.move_id.action_post() # DARRELL
            history = self.env['account.history.invoice'].search([('invoice_id','=',self.invoice_id.id),('existe_doc_islr','=',True)])
            #raise UserError(_('history = %s')%history)
            if not history:
                name_asiento = self.env['ir.sequence'].next_by_code('purchase.isrl.retention.account')
            else:
                for det_history in history:
                    name_asiento=det_history.nro_asiento_islr
            #raise UserError(_('name_asiento = %s')%name_asiento)

            id_move=self.registro_movimiento_retencion(name_asiento)
            idv_move=id_move.id
            valor=self.registro_movimiento_linea_retencion(idv_move,name_asiento)
            moves= self.env['account.move'].search([('id','=',idv_move)])
            moves.filtered(lambda move: move.journal_id.post_at != 'bank_rec').post()          

            
        else :
            raise UserError("Configure el Diario en la compañia")