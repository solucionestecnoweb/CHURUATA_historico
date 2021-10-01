# -*- coding: utf-8 -*-

import logging
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


_logger = logging.getLogger('__name__')

"""class AccountMoveReversal(models.TransientModel):
   
    _name = 'account.move.reversal'
    _description = 'Account Move Reversal'


    def reverse_moves(self):
        super().reverse_moves()
        raise UserError(_(' DArrell Sojo y Angel sojo'))"""


class AccountMove(models.Model):
    _inherit = 'account.move'    

       
    def button_draft(self):
        super().button_draft()
        #lista_account_move = self.env['account.move'].search([('|',('vat_ret_id','=',self.vat_ret_id.id),('wh_muni_id','=',self.wh_muni_id.id)),('type','=','entry')])
        lista_account_move = self.env['account.move'].search([('vat_ret_id','=',self.vat_ret_id.id),('type','=','entry')])
        #raise UserError(_('lista_account_move = %s')%lista_account_move)
        if self.vat_ret_id.id:
            if lista_account_move:
                for det_move in lista_account_move:
                    nro_asiento_iva=det_move.name
                    nro_comprobante_iva=det_move.vat_ret_id.name
                    nro_asiento_muni=det_move.name
                    nro_comprobante_muni=det_move.wh_muni_id.name
                    id_asiento=det_move.id
                    #raise UserError(_('id_asiento= %s')%id_asiento)
                history=self.env['account.history.invoice']
                campos={
                    'nro_asiento_iva':nro_asiento_iva,
                    'nro_comprobante_iva':nro_comprobante_iva,
                    'invoice_id':self.id,
                    'existe_doc_iva':True,
                    }
                history.create(campos)

            vat_line = self.env['vat.retention.invoice.line'].search([('retention_id','=',self.vat_ret_id.id)])
            vat_line.unlink()
            lista_vat = self.env['vat.retention'].search([('id','=',self.vat_ret_id.id)])
            lista_vat.unlink()
            if lista_account_move:
                asiento_vat = self.env['account.move'].search([('id','=',id_asiento)])
                asiento_vat.write({
                    'state':"draft",
                    })
                asiento_vat.with_context(force_delete=True).unlink()

        lista_account_move2 = self.env['account.move'].search([('wh_muni_id','=',self.wh_muni_id.id),('type','=','entry')])
        #raise UserError(_('lista_account_move2 = %s')%self.wh_muni_id.id)
        if self.wh_muni_id.id:
            if lista_account_move2:
                for det_move2 in lista_account_move2:
                    nro_asiento_muni=det_move2.name
                    nro_comprobante_muni=det_move2.wh_muni_id.name
                    id_asiento=det_move2.id
                    #raise UserError(_('id_asiento= %s')%id_asiento)
                history2=self.env['account.history.invoice']
                campos2={
                    'nro_asiento_municipal':nro_asiento_muni,
                    'nro_comprobante_municipal':nro_comprobante_muni,
                    'invoice_id':self.id,
                    'existe_doc_muni':True,
                    }
                history2.create(campos2)            

            muni_line = self.env['municipality.tax.line'].search([('municipality_tax_id','=',self.wh_muni_id.id)])
            muni_line.unlink()
            lista_muni = self.env['municipality.tax'].search([('id','=',self.wh_muni_id.id)])
            lista_muni.unlink()
            if lista_account_move2:
                asiento_muni = self.env['account.move'].search([('id','=',id_asiento)])
                asiento_muni.write({
                    'state':"draft",
                    })
                
                asiento_muni.with_context(force_delete=True).unlink()

        lista_account_move3 = self.env['account.move'].search([('isrl_ret_id','=',self.isrl_ret_id.id),('type','=','entry')])
        if self.isrl_ret_id.id:
            if lista_account_move3:
                for det_move3 in lista_account_move3:
                    nro_asiento_islr=det_move3.name
                    nro_comprobante_isrl=det_move3.isrl_ret_id.name
                    id_asiento=det_move3.id
                    #raise UserError(_('id_asiento= %s')%id_asiento)
                history3=self.env['account.history.invoice']
                campos3={
                    'nro_asiento_islr':nro_asiento_islr,
                    'nro_comprobante_islr':nro_comprobante_isrl,
                    'invoice_id':self.id,
                    'existe_doc_islr':True,
                    }
                history3.create(campos3)            

            islr_line = self.env['isrl.retention.invoice.line'].search([('retention_id','=',self.isrl_ret_id.id)])
            islr_line.unlink()
            lista_islr = self.env['isrl.retention'].search([('id','=',self.isrl_ret_id.id)])
            lista_islr.unlink()
            if lista_account_move3:
                asiento_islr = self.env['account.move'].search([('id','=',id_asiento)])
                asiento_islr.write({
                    'state':"draft",
                    })
                
                asiento_islr.with_context(force_delete=True).unlink()