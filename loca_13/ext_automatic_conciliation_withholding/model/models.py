# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api, exceptions, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger('__name__')


class RetentionVat(models.Model):
    """This is a main model for rentetion vat control."""
    _inherit = 'isrl.retention'

    def action_post(self):
        super().action_post()
        self.concilio_saldo_pendiente_isrl()


    def concilio_saldo_pendiente_isrl(self):
        id_islr=self.id
        tipo_empresa=self.type
        if tipo_empresa=="in_invoice" or tipo_empresa=="in_refund" or tipo_empresa=="in_receipt":#aqui si la empresa es un proveedor
            type_internal="payable"
        if tipo_empresa=="out_invoice" or tipo_empresa=="out_refund" or tipo_empresa=="out_receipt":# aqui si la empresa es cliente
            type_internal="receivable"
        busca_movimientos = self.env['account.move'].search([('isrl_ret_id','=',id_islr)])
        #raise UserError(_('busca_movimientos = %s')%busca_movimientos)
        for det_movimientos in busca_movimientos:
            busca_line_mov = self.env['account.move.line'].search([('move_id','=',det_movimientos.id),('account_internal_type','=',type_internal)])
            if busca_line_mov.credit==0:
                id_move_debit=busca_line_mov.id
                monto_debit=busca_line_mov.debit
            if busca_line_mov.debit==0:
                id_move_credit=busca_line_mov.id
                monto_credit=busca_line_mov.credit
        if tipo_empresa=="in_invoice" or tipo_empresa=="out_refund" or tipo_empresa=="in_receipt":
            monto=monto_debit
        if tipo_empresa=="out_invoice" or tipo_empresa=="in_refund" or tipo_empresa=="out_receipt":
            monto=monto_credit
        value = {
             'debit_move_id':id_move_debit,
             'credit_move_id':id_move_credit,
             'amount':monto,
             'max_date':self.date_move,
        }
        self.env['account.partial.reconcile'].create(value)






class AccountMove(models.Model):
    _inherit = 'vat.retention'

    def action_posted(self):
        super().action_posted()
        self.concilio_saldo_pendiente()

    def concilio_saldo_pendiente(self):
        id_retention=self.id
        tipo_empresa=self.move_id.type
        if tipo_empresa=="in_invoice" or tipo_empresa=="in_refund" or tipo_empresa=="in_receipt":#aqui si la empresa es un proveedor
            type_internal="payable"
        if tipo_empresa=="out_invoice" or tipo_empresa=="out_refund" or tipo_empresa=="out_receipt":# aqui si la empresa es cliente
            type_internal="receivable"
        busca_movimientos = self.env['account.move'].search([('vat_ret_id','=',id_retention)])
        for det_movimientos in busca_movimientos:
            busca_line_mov = self.env['account.move.line'].search([('move_id','=',det_movimientos.id),('account_internal_type','=',type_internal)])
            if busca_line_mov.credit==0:
                id_move_debit=busca_line_mov.id
                monto_debit=busca_line_mov.debit
            if busca_line_mov.debit==0:
                id_move_credit=busca_line_mov.id
                monto_credit=busca_line_mov.credit
        if tipo_empresa=="in_invoice" or tipo_empresa=="out_refund" or tipo_empresa=="in_receipt":
            monto=monto_debit
        if tipo_empresa=="out_invoice" or tipo_empresa=="in_refund" or tipo_empresa=="out_receipt":
            monto=monto_credit
        value = {
             'debit_move_id':id_move_debit,
             'credit_move_id':id_move_credit,
             'amount':monto,
             'max_date':self.accouting_date,
        }
        self.env['account.partial.reconcile'].create(value)

class MUnicipalityTax(models.Model):
    _inherit = 'municipality.tax'

    def action_post(self):
        super().action_post()
        self.concilio_saldo_pendiente_muni()



    def concilio_saldo_pendiente_muni(self):
        id_municipality=self.id
        tipo_empresa=self.invoice_id.type
        if tipo_empresa=="in_invoice" or tipo_empresa=="in_refund" or tipo_empresa=="in_receipt":#aqui si la empresa es un proveedor
            type_internal="payable"
        if tipo_empresa=="out_invoice" or tipo_empresa=="out_refund" or tipo_empresa=="out_receipt":# aqui si la empresa es cliente
            type_internal="receivable"
        busca_movimientos = self.env['account.move'].search([('wh_muni_id','=',id_municipality)])
        #raise UserError(_('busca_movimientos = %s')%busca_movimientos)
        for det_movimientos in busca_movimientos:
            busca_line_movv = self.env['account.move.line'].search([('move_id','=',det_movimientos.id),('account_internal_type','=',type_internal)])
            for busca_line_mov in busca_line_movv: #PQC
                basura=0 #PQC
            #raise UserError(_('busca_line_mov = %s')%busca_line_mov)
            if busca_line_mov.credit==0:
                id_move_debit=busca_line_mov.id
                monto_debit=busca_line_mov.debit
            if busca_line_mov.debit==0:
                id_move_credit=busca_line_mov.id
                monto_credit=busca_line_mov.credit
        if tipo_empresa=="in_invoice" or tipo_empresa=="out_refund" or tipo_empresa=="in_receipt":
            monto=monto_debit
        if tipo_empresa=="out_invoice" or tipo_empresa=="in_refund" or tipo_empresa=="out_receipt":
            monto=monto_credit
        value = {
             'debit_move_id':id_move_debit,
             'credit_move_id':id_move_credit,
             'amount':monto,
             'max_date':self.transaction_date,
        }
        self.env['account.partial.reconcile'].create(value)