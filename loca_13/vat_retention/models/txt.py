# # -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from odoo import models, fields, api, _, tools
from odoo.exceptions import UserError
import openerp.addons.decimal_precision as dp
import logging

import io
from io import BytesIO
from io import StringIO

import xlsxwriter
import shutil
import base64
import csv

import urllib.request

import requests

_logger = logging.getLogger(__name__)

def rif_format(valor):
    if valor:
        return valor.replace('-','')
    return '0'

def tipo_format(valor):
    if valor and valor=='in_refund':
        return '03'
    return '01'

def float_format(valor):
    if valor:
        result = '{:,.2f}'.format(valor)
        #_logger.info('Result 1: %s' % result)
        result = result.replace(',','')
        #_logger.info('Result 2: %s' % result)
        return result
    return valor

class BsoftContratoReport2(models.TransientModel):
    _name = 'snc.wizard.retencioniva'
    _description = 'Generar archivo TXT de retenciones de IVA'

    delimiter = '\t'
    quotechar = "'"
    date_from = fields.Date(string='Fecha de Llegada', default=lambda *a:datetime.now().strftime('%Y-%m-%d'))
    date_to = fields.Date(string='Fecha de Salida', default=lambda *a:(datetime.now() + timedelta(days=(1))).strftime('%Y-%m-%d'))
    file_data = fields.Binary('Archivo TXT', filters=None, help="")
    file_name = fields.Char('txt_generacion.txt', size=256, required=False, help="",)

    def show_view(self, name, model, id_xml, res_id=None, view_mode='tree,form', nodestroy=True, target='new'):
        context = self._context
        mod_obj = self.env['ir.model.data']
        view_obj = self.env['ir.ui.view']
        module = ""
        view_id = self.env.ref(id_xml).id
        if view_id:
            view = view_obj.browse(view_id)
            view_mode = view.type
        ctx = context.copy()
        ctx.update({'active_model': model})
        res = {'name': name,
                'view_type': 'form',
                'view_mode': view_mode,
                'view_id': view_id,
                'res_model': model,
                'res_id': res_id,
                'nodestroy': nodestroy,
                'target': target,
                'type': 'ir.actions.act_window',
                'context': ctx,
                }
        return res

    def action_generate_txt(self):

        dominio = [('manual','=',True),('invoice_id.type','in',('in_invoice', 'in_refund')),('invoice_id.amount_retiva','!=',0.00)]

        if self.date_from:
            dominio.append(('invoice_id.date','>=',self.date_from))

        if self.date_to:
            dominio.append(('invoice_id.date','<=',self.date_to))

        rec_ids = self.env['account.invoice.tax'].search(dominio).ids
        rec_cursor = self.env['account.invoice.tax'].browse(rec_ids)

        company = self.env['res.company']._company_default_get('account.invoice')
        rif = rif_format(company.vat)


        self.file_name = 'txt_generacion.txt'


        with open("direccion/en el servido/hasta/txt_generacion.txt", "w") as file:

            for rec in rec_cursor:
                periodo = '%s'%(rec.invoice_id.date)
                periodo = periodo.replace('-', '')
                periodo = periodo[0:6]
                exento = abs(rec.total_factura-rec.base_imponible-rec.impuesto_iva-rec.amount)
                total = rec.base_imponible+rec.impuesto_iva+exento
                por_iva = rec.impuesto_iva/rec.base_imponible*100
                fecha = rec.invoice_id.date_invoice
                su_rif = rif_format(rec.invoice_id.partner_id.vat)
                refer = rec.invoice_id.refund_invoice_id.number if rec.tipo=='in_refund' and rec.invoice_id.refund_invoice_id else '0'
                total2 = str(total)
                base_imponible = str(rec.base_imponible)
                amount = str(rec.amount)

                refer = str(refer)
                number_retiva = str(rec.number_retiva)
                exento = str(exento)
                por_iva = str(por_iva)
                fecha = str(fecha)
                invoice_sequence = str(rec.invoice_id.invoice_sequence)


                file.write(rif + "\t")
                file.write(periodo + "\t")
                file.write(fecha + "\t")

                file.write('C' + "\t")
                file.write(rec.tipo + "\t")
                file.write(su_rif + "\t")


                file.write(rec.invoice_id.number + "\t")
                file.write(invoice_sequence + "\t")
                file.write(total2 + "\t")

                file.write(base_imponible + "\t")
                file.write(amount + "\t")
                file.write(refer + "\t")

                file.write(number_retiva + "\t")
                file.write(exento + "\t")
                file.write(por_iva + "\t")

                file.write('0' + "\n")




        self.write({'file_data': base64.encodestring(open("direccion/en el servido/hasta/txt_generacion.txt", "rb").read()),
                    'file_name': "Retenciones de IVA desde %s hasta %s.txt"%(self.date_from,self.date_to),
                    })

        return self.show_view('Arcivo Generado', self._name, 'carpetamodulo.modelodelavista', self.id)

