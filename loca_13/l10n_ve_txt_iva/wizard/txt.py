# # -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from odoo import models, fields, api, _, tools
from odoo.exceptions import UserError, ValidationError
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

"""def rif_format(valor):
    if valor:
        return valor.replace('-','')
    return '0'"""

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

def float_format2(valor):
	#valor=self.base_tax
	if valor:
		result = '{:,.2f}'.format(valor)
		#result = result.replace(',','*')
		#esult = result.replace('.',',')
		#result = result.replace('*','.')
		result = result.replace(',','')
	else:
		result="0.00"
	return result

def completar_cero(campo,digitos):
    valor=len(campo)
    campo=str(campo)
    nro_ceros=digitos-valor+1
    for i in range(1,nro_ceros,1):
        campo=" "+campo
    return campo

def formato_periodo(valor):
        fecha = str(valor)
        fecha_aux=fecha
        ano=fecha_aux[0:4]
        mes=fecha[5:7]
        dia=fecha[8:10]  
        resultado=ano+mes
        return resultado

def rif_format(aux,aux_type):
    nro_doc=aux
    tipo_doc=aux_type
    nro_doc=nro_doc.replace('V','')
    nro_doc=nro_doc.replace('v','')
    nro_doc=nro_doc.replace('E','')
    nro_doc=nro_doc.replace('e','')
    nro_doc=nro_doc.replace('G','')
    nro_doc=nro_doc.replace('g','')
    nro_doc=nro_doc.replace('J','')
    nro_doc=nro_doc.replace('j','')
    nro_doc=nro_doc.replace('P','')
    nro_doc=nro_doc.replace('p','')
    nro_doc=nro_doc.replace('-','')
    if tipo_doc=="v":
        tipo_doc="V"
    if tipo_doc=="e":
        tipo_doc="E"
    if tipo_doc=="g":
        tipo_doc="G"
    if tipo_doc=="j":
        tipo_doc="J"
    if tipo_doc=="p":
        tipo_doc="P"
    if tipo_doc=="c":
        tipo_doc="C"
    resultado=str(tipo_doc)+str(nro_doc)
    return resultado
    #raise UserError(_('cedula: %s')%resultado)

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

        #dominio = (('id','=',True),('invoice_id.type','in',('in_invoice', 'in_refund')),('invoice_id.amount_tax','!=',0.00))

        #if self.date_from:
        #    dominio.append(('create_date','>=',self.date_from))

        #if self.date_to:
        #    dominio.append(('create_date','<=',self.date_to))

        #rec_ids = self.env['account.move'].search(dominio).ids
        #rec_cursor = self.env['account.move.line.resumen'].search([('fecha_fact','>=',self.date_from),('fecha_fact','<=',self.date_to),('type','in',('in_invoice','in_refund','in_receipt')),('state','=','posted'),])
        ret_cursor = self.env['account.move'].search([('date','>=',self.date_from),('date','<=',self.date_to),('type','in',('in_invoice','in_refund','in_receipt')),('state','=','posted'),],order="date asc")
        #_logger.info("\n\n\n {} \n\n\n".format(self.rec_cursor))
        #raise UserError(_(' id retencion:%s')%rec_cursor.vat_ret_id.id) 

        self.file_name = 'txt_generacion.txt'
        retiva = self.env['vat.retention']
        retiva = str(retiva.name)

        ruta="C:/Odoo 13.0e/server/odoo/LocalizacionV13/l10n_ve_txt_iva/wizard/txt_generacion.txt"
        #ruta="/mnt/extra-addons/l10n_ve_txt_iva/wizard/txt_generacion.txt"
        #ruta="/home/odoo/src/user/LocalizacionV13/l10n_ve_txt_iva/wizard/txt_generacion.txt"
        #ruta="/home/odoo/src/txt_generacion.txt"
        #raise UserError(_('mama = %s')%rec.type)

        with open(ruta, "w") as file:

            for ret in ret_cursor:
                if ret.vat_ret_id:
                    if ret.vat_ret_id.state=="posted":
                    	if ret.type=="in_invoice":
                    		trans='01'
                    	if ret.type=="in_refund":
                    		trans='03'
                    	if ret.type=='in_receipt':
                    		trans='02'

                    	acum_exemto=0
                    	
                    	busca_exento = self.env['vat.retention.invoice.line'].search([('retention_id','=',ret.vat_ret_id.id)])
                    	for det in busca_exento:
                    		if det.tax_id.aliquot=="exempt":
                    			acum_exemto=acum_exemto+det.amount_untaxed

                    	rec_cursor = self.env['vat.retention.invoice.line'].search([('retention_id','=',ret.vat_ret_id.id)])
                    	for rec in rec_cursor:

                    		if rec.tax_id.aliquot!="exempt":
		                        rif_compania=rif_format(rec.invoice_id.company_id.vat,rec.invoice_id.company_id.partner_id.doc_type)
		                        file.write(rif_compania + "\t")#1

		                        periodo=formato_periodo(self.date_to)
		                        file.write(periodo + "\t")#2

		                        fecha = rec.invoice_id.date
		                        fecha = str(fecha)
		                        file.write(fecha + "\t")#3

		                        file.write("C" + "\t")#4

		                        file.write(trans + "\t") #5

		                        rif_proveedor= rif_format(rec.invoice_id.partner_id.vat,rec.invoice_id.partner_id.doc_type)
		                        file.write(rif_proveedor + "\t") #6

		                        invoicer_number=str(rec.invoice_id.invoice_number)
		                        #invoicer_number=completar_cero(invoicer_number,10)
		                        file.write(invoicer_number + "\t") #7

		                        invoice_sequence = str(rec.invoice_id.invoice_ctrl_number)
		                        #invoice_sequence = completar_cero(invoice_sequence,10)
		                        file.write(invoice_sequence + "\t") #8

		                        total = str(float_format2(rec.amount_vat_ret+rec.amount_untaxed+acum_exemto))
		                        #total = completar_cero(total,12)
		                        file.write(total + "\t") #9

		                        importe_base = str(float_format2(rec.amount_untaxed)) # PREGUNTAR rec.total_base
		                        #importe_base = completar_cero(importe_base,12)
		                        file.write(importe_base + "\t") #10

		                        monto_ret=str(float_format2(rec.retention_amount)) # PREGUNTAR
		                        #monto_ret = completar_cero(monto_ret,12)
		                        file.write(monto_ret + "\t") #11

		                        if rec.invoice_id.ref==False:
		                            fact_afec='0'
		                        else:
		                            fact_afec = str(rec.invoice_id.ref)
		                        #fact_afec = completar_cero(fact_afec,5)
		                        file.write(fact_afec + "\t") #12

		                        nro_comprobante = str(rec.retention_id.name)
		                        file.write(nro_comprobante + "\t") #13

		                        #total_exento= str(rec.total_exento)
		                        """if rec.tax_id.aliquot=="exempt":
		                        	total_exento=rec.amount_untaxed
		                        else:
		                        	total_exento=0.00"""
		                        total_exento=acum_exemto
		                        total_exento=str(float_format2(total_exento))
		                        file.write(total_exento + "\t")#14

		                        porcentage_iva=rec.tax_id.amount
		                        porcentage_iva = str(round(porcentage_iva))
		                        #porcentage_iva = completar_cero(porcentage_iva,5)
		                        file.write(porcentage_iva + "\t") #15 PREGUNTAR"""

		                        file.write('0' + "\n") #16



        self.write({'file_data': base64.encodestring(open(ruta, "rb").read()),
                    'file_name': "Retenciones de IVA desde %s hasta %s.txt"%(self.date_from,self.date_to),
                    })

        return self.show_view('Archivo Generado', self._name, 'vat_retention.snc_wizard_retencioniva_form_view', self.id)
