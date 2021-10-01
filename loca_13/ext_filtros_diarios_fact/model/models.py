# -*- coding: utf-8 -*-

import logging
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


_logger = logging.getLogger('__name__')

class AccountMove(models.Model):
    _inherit = 'account.move'    

    @api.depends('type')
    def _compute_invoice_filter_type_doc(self):

        ejecuta="no"
        if self.type=="in_invoice":
            tipo_doc="fc"
            typo="purchase"
            ejecuta="si"
        if self.type=="in_refund":
            tipo_doc="nc"
            typo="purchase"
            ejecuta="si"
        if self.type=="in_receipt":
            tipo_doc="nb"
            typo="purchase"
            ejecuta="si"

        if self.type=="out_invoice":
            tipo_doc="fc"
            typo="sale"
            ejecuta="si"
        if self.type=="out_refund":
            tipo_doc="nc"
            typo="sale"
            ejecuta="si"
        if self.type=="out_receipt":
            tipo_doc="nb"
            typo="sale"
            ejecuta="si"
        
        if ejecuta=="si":
            busca_diarios = self.env['account.journal'].search([('tipo_doc','=',tipo_doc),('type','=',typo)])
            for det in busca_diarios:
                file=det.id
        else:
            busca_diarios = self.env['account.journal'].search([('type','=','general')])
            for det in busca_diarios:
                file=det.id
        self.invoice_filter_type_doc= file

    invoice_filter_type_doc = fields.Char(compute='_compute_invoice_filter_type_doc',
        help="Technical field used to have a dynamic domain on journal / taxes in the form view.")

    #journal_id = fields.Many2one('account.journal', string='Journal', required=True, default=invoice_filter_type_doc)


    @api.model
    def _get_default_journal(self):
        ''' Get the default journal.
        It could either be passed through the context using the 'default_journal_id' key containing its id,
        either be determined by the default type.
        '''
        move_type = self._context.get('default_type', 'entry')
        journal_type = 'general'
        if move_type in self.get_sale_types(include_receipts=True):
            journal_type = 'sale'
        elif move_type in self.get_purchase_types(include_receipts=True):
            journal_type = 'purchase'

        if self._context.get('default_journal_id'):
            journal = self.env['account.journal'].browse(self._context['default_journal_id'])

            if move_type != 'entry' and journal.type != journal_type:
                raise UserError(_("Cannot create an invoice of type %s with a journal having %s as type.") % (move_type, journal.type))
        else:
            company_id = self._context.get('force_company', self._context.get('default_company_id', self.env.company.id))
            domain = [('company_id', '=', company_id), ('type', '=', journal_type)]

            journal = None
            if self._context.get('default_currency_id'):
                currency_domain = domain + [('currency_id', '=', self._context['default_currency_id'])]
                journal = self.env['account.journal'].search(currency_domain, limit=1)

            if not journal:
                journal = self.env['account.journal'].search(domain, limit=1)

            if not journal:
                error_msg = _('Please define an accounting miscellaneous journal in your company')
                if journal_type == 'sale':
                    error_msg = _('Please define an accounting sale journal in your company')
                elif journal_type == 'purchase':
                    error_msg = _('Please define an accounting purchase journal in your company')
                raise UserError(error_msg)
        #raise UserError(_('move_type = %s')%move_type)
        # CODINO NUEVO***************************
        journal_aux=journal
        ejecuta="no"

        if move_type=="in_invoice":
            tipo_doc="fc"
            typo="purchase"
            ejecuta="si"
        if move_type=="in_refund":
            tipo_doc="nc"
            typo="purchase"
            ejecuta="si"
        if move_type=="in_receipt":
            tipo_doc="nb"
            typo="purchase"
            ejecuta="si"

        if move_type=="out_invoice":
            tipo_doc="fc"
            typo="sale"
            ejecuta="si"
        if move_type=="out_refund":
            tipo_doc="nc"
            typo="sale"
            ejecuta="si"
        if move_type=="out_receipt":
            tipo_doc="nb"
            typo="sale"
            ejecuta="si"

        if ejecuta=="si":
            diario = self.env['account.journal'].search([('tipo_doc','=',tipo_doc),('type','=',typo)])
        if move_type=="entry":
            diario=journal
        #raise UserError(_('journal = %s')%diario)
        # ****** FIN CODINO NUEVO***************************
        return diario

    journal_id = fields.Many2one('account.journal', string='Journal', required=True, readonly=True,
        states={'draft': [('readonly', False)]},
        domain="[('company_id', '=', company_id)]",
        default=_get_default_journal)