# -*- coding: utf-8 -*-

import logging
import json
from odoo.tools import float_is_zero, float_compare, safe_eval, date_utils, email_split, email_escape_char, email_re

from odoo import fields, models, api, exceptions, _
from odoo.exceptions import UserError, ValidationError


_logger = logging.getLogger('__name__')


class AccountMove(models.Model):
    """This model add fields need in the invoice for accounting in Venezuela."""
    _inherit = 'account.move'

    invoice_payments_widget = fields.Text(groups="account.group_account_invoice",
        compute='_compute_payments_widget_reconciled_info')

    @api.depends('type', 'line_ids.amount_residual')
    def _compute_payments_widget_reconciled_info(self):
        for move in self:
            if move.state != 'posted' or not move.is_invoice(include_receipts=True):
                move.invoice_payments_widget = json.dumps(False)
                continue
            reconciled_vals = move._get_reconciled_info_JSON_values()
            if reconciled_vals:
                info = {
                    'title': _('Aplicado'),
                    'outstanding': False,
                    'content': reconciled_vals,
                }
                move.invoice_payments_widget = json.dumps(info, default=date_utils.json_default)
            else:
                move.invoice_payments_widget = json.dumps(False)
            #raise UserError(_(' valor=%s')%move.invoice_payments_widget)


    def funcion_numeracion_fac(self):
        if self.type=="in_invoice":
            busca_correlativos = self.env['account.move'].search([('invoice_number','=',self.invoice_number_pro),('id','!=',self.id),('partner_id','=',self.partner_id.id)])
            for det_corr in busca_correlativos:
                if det_corr.invoice_number:
                    raise UserError(_(' El valor :%s ya se uso en otro documento de este proveedor')%det_corr.invoice_number)

            """busca_correlativos2 = self.env['account.move'].search([('invoice_ctrl_number','=',self.invoice_ctrl_number_pro),('id','!=',self.id)])
            for det_corr2 in busca_correlativos2:
                if det_corr2.invoice_ctrl_number:
                    raise UserError(_(' El nro de control :%s ya se uso en otro documento')%det_corr2.invoice_ctrl_number)"""
            
            self.invoice_number=self.invoice_number_pro
            self.invoice_ctrl_number=self.invoice_ctrl_number_pro
            partners='pro' # aqui si es un proveedor

        if self.type=="in_refund" or self.type=="in_receipt":
            busca_correlativos = self.env['account.move'].search([('invoice_number','=',self.refuld_number_pro),('id','!=',self.id),('partner_id','=',self.partner_id.id)])
            for det_corr in busca_correlativos:
                if det_corr.invoice_number:
                    raise UserError(_(' El valor :%s ya se uso en otro documento de este proveedor')%det_corr.invoice_number)

            busca_correlativos2 = self.env['account.move'].search([('invoice_ctrl_number','=',self.refund_ctrl_number_pro),('id','!=',self.id)])
            for det_corr2 in busca_correlativos2:
                if det_corr2.invoice_ctrl_number:
                    raise UserError(_(' El nro de control :%s ya se uso en otro documento')%det_corr2.invoice_ctrl_number)
                    
            self.invoice_number=self.refuld_number_pro
            self.invoice_ctrl_number=self.refund_ctrl_number_pro
            partners='cli' # aqui si es un cliente

        if self.type=="out_invoice":
            if self.nr_manual==False:
                busca_correlativos = self.env['account.move'].search([('invoice_ctrl_number','=',self.invoice_ctrl_number),('id','!=',self.id)])
                #if self.invoice_number_cli:
                if busca_correlativos or not self.invoice_ctrl_number:
                    self.invoice_number_cli=self.get_invoice_number_cli()
                    self.invoice_number=self.invoice_number_cli #self.get_invoice_number_cli()
                    self.invoice_ctrl_number_cli=self.get_invoice_ctrl_number_unico()
                    self.invoice_ctrl_number=self.invoice_ctrl_number_cli #self.get_invoice_ctrl_number_cli()
                else:
                    self.invoice_number=self.invoice_number_cli
                    self.invoice_ctrl_number=self.invoice_ctrl_number_cli
                    
            else:
                self.invoice_number=self.invoice_number_cli
                self.invoice_ctrl_number=self.invoice_ctrl_number_cli

        if self.type=="out_refund":
            if self.nr_manual==False:
                busca_correlativos = self.env['account.move'].search([('invoice_ctrl_number','=',self.invoice_ctrl_number),('id','!=',self.id)])
                if busca_correlativos or not self.invoice_ctrl_number:
                    self.refuld_number_cli=self.get_refuld_number_cli()
                    self.invoice_number=self.refuld_number_cli #self.get_refuld_number_cli()
                    self.refund_ctrl_number_cli=self.get_invoice_ctrl_number_unico()
                    self.invoice_ctrl_number=self.refund_ctrl_number_cli #self.get_refuld_ctrl_number_cli()
                else:
                    self.invoice_number=self.refuld_number_cli
                    self.invoice_ctrl_number=self.refund_ctrl_number_cli
            else:
                self.invoice_number=self.refuld_number_cli
                self.invoice_ctrl_number=self.refund_ctrl_number_cli

        if self.type=="out_receipt":
            if self.nr_manual==False:
                busca_correlativos = self.env['account.move'].search([('invoice_ctrl_number','=',self.invoice_ctrl_number),('id','!=',self.id)])
                if busca_correlativos or not self.invoice_ctrl_number:
                    self.refuld_number_cli=self.get_refuld_number_pro()
                    self.invoice_number=self.refuld_number_cli #self.get_refuld_number_cli()
                    self.refund_ctrl_number_cli=self.get_invoice_ctrl_number_unico()
                    self.invoice_ctrl_number=self.refund_ctrl_number_cli #self.get_refuld_ctrl_number_cli()
                else:
                    self.invoice_number=self.refuld_number_cli
                    self.invoice_ctrl_number=self.refund_ctrl_number_cli  
            else:
                self.invoice_number=self.refuld_number_cli
                self.invoice_ctrl_number=self.refund_ctrl_number_cli
        

    def get_invoice_ctrl_number_unico(self):
        '''metodo que crea el Nombre del asiento contable si la secuencia no esta creada, crea una con el
        nombre: 'l10n_ve_cuenta_retencion_iva'''

        self.ensure_one()
        SEQUENCE_CODE = 'l10n_ve_nro_control_unico_formato_libre'
        company_id = 1
        IrSequence = self.env['ir.sequence'].with_context(force_company=1)
        name = IrSequence.next_by_code(SEQUENCE_CODE)

        # si aún no existe una secuencia para esta empresa, cree una
        if not name:
            IrSequence.sudo().create({
                'prefix': '00-',
                'name': 'Localización Venezolana nro control Unico Factura Forma Libre %s' % 1,
                'code': SEQUENCE_CODE,
                'implementation': 'no_gap',
                'padding': 4,
                'number_increment': 1,
                'company_id': 1,
            })
            name = IrSequence.next_by_code(SEQUENCE_CODE)
        #self.invoice_number_cli=name
        return name