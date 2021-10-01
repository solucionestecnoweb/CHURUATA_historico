from datetime import datetime, timedelta
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT

from odoo import models, fields, api, _, tools
from odoo.exceptions import UserError
import openerp.addons.decimal_precision as dp
import logging

import io
from io import BytesIO

import xlsxwriter
import shutil
import base64
import csv
import xlwt
import xml.etree.ElementTree as ET

class ResumenMunicipalModelo(models.Model):
    _name = "resumen.municipal.wizard.pdf"

    fecha_comprobante = fields.Date(string='Fecha')
    partner_id  = fields.Many2one(comodel_name='res.partner', string='Partner')
    invoice_number =   fields.Char(string='Fac. Número')
    invoice_ctrl_number = fields.Char(string='Nro Control')
    nro_comp = fields.Char(string='Nro Comprobante')
    factura_total = fields.Float(string='Monto Factura')
    base_imponible = fields.Float(string='base imponible')
    retenido = fields.Float(string='retenido')
    porcentaje = fields.Float(string='Porcentaje')
    codigo = fields.Char(string='Código Actividad Económica')
    invoice_id = fields.Many2one('account.move')


    def float_format(self,valor):
        #valor=self.base_tax
        if valor:
            result = '{:,.2f}'.format(valor)
            result = result.replace(',','*')
            result = result.replace('.',',')
            result = result.replace('*','.')
        else:
            result="0,00"
        return result

    def formato_fecha2(self,date):
        fecha = str(date)
        fecha_aux=fecha
        ano=fecha_aux[0:4]
        mes=fecha[5:7]
        dia=fecha[8:10]  
        resultado=dia+"/"+mes+"/"+ano
        return resultado

    def rif2(self,aux):
        #nro_doc=self.partner_id.vat
        busca_partner = self.env['res.partner'].search([('id','=',aux)])
        if busca_partner:
            for det in busca_partner:
                tipo_doc=busca_partner.doc_type
                if busca_partner.vat:
                    nro_doc=str(busca_partner.vat)
                else:
                    nro_doc='0000000000'
        else:
            nro_doc='000000000'
            tipo_doc='V'
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
        nro_doc=nro_doc.replace('c','')
        nro_doc=nro_doc.replace('C','')
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
        resultado=str(tipo_doc)+"-"+str(nro_doc)
        return resultado

class WizardReport_2(models.TransientModel): # aqui declaro las variables del wizar que se usaran para el filtro del pdf
    _name = 'wizard.resumen.municipal'
    _description = "Resumen Retenciones Municipal"

    date_from  = fields.Date('Date From', default=lambda *a:(datetime.now() - timedelta(days=(1))).strftime('%Y-%m-%d'))
    date_to = fields.Date(string='Date To', default=lambda *a:datetime.now().strftime('%Y-%m-%d'))
    date_actual = fields.Date(default=lambda *a:datetime.now().strftime('%Y-%m-%d'))

    company_id = fields.Many2one('res.company','Company',default=lambda self: self.env.user.company_id.id)
    line  = fields.Many2many(comodel_name='resumen.municipal.wizard.pdf', string='Lineas')

    def rif(self,aux):
        #nro_doc=self.partner_id.vat
        busca_partner = self.env['res.partner'].search([('id','=',aux)])
        for det in busca_partner:
            tipo_doc=busca_partner.doc_type
            nro_doc=str(busca_partner.vat)
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
        resultado=str(tipo_doc)+"-"+str(nro_doc)
        return resultado

    def periodo(self,date):
        fecha = str(date)
        fecha_aux=fecha
        mes=fecha[5:7] 
        resultado=mes
        return resultado

    def formato_fecha(self,date):
        fecha = str(date)
        fecha_aux=fecha
        ano=fecha_aux[0:4]
        mes=fecha[5:7]
        dia=fecha[8:10]  
        resultado=dia+"/"+mes+"/"+ano
        return resultado

    def float_format2(self,valor):
        #valor=self.base_tax
        if valor:
            result = '{:,.2f}'.format(valor)
            result = result.replace(',','*')
            result = result.replace('.',',')
            result = result.replace('*','.')
        else:
            result="0,00"
        return result

    def conv_div_nac(self,valor,selff):
        selff.invoice_id.currency_id.id
        fecha_contable_doc=selff.invoice_id.date
        monto_factura=selff.invoice_id.amount_total
        valor_aux=0
        #raise UserError(_('moneda compañia: %s')%self.company_id.currency_id.id)
        if selff.invoice_id.currency_id.id!=self.company_id.currency_id.id:
            tasa= self.env['account.move'].search([('id','=',selff.invoice_id.id)],order="id asc")
            for det_tasa in tasa:
                monto_nativo=det_tasa.amount_untaxed_signed
                monto_extran=det_tasa.amount_untaxed
                valor_aux=abs(monto_nativo/monto_extran)
            rate=round(valor_aux,2)  # LANTA
            #rate=round(valor_aux,2)  # ODOO SH
            resultado=valor*rate
        else:
            resultado=valor
        return resultado

    def get_invoice(self):
        t=self.env['resumen.municipal.wizard.pdf']
        d=t.search([])
        d.unlink()
        cursor_resumen = self.env['municipality.tax'].search([
            ('transaction_date','>=',self.date_from),
            ('transaction_date','<=',self.date_to),
            ('state','=','posted'),
            ('type','in',('in_invoice','in_refund','in_receipt'))
            ])
        for det in cursor_resumen:
            if det.type=="in_refund":
                signo=-1
            else:
                signo=1
            for det_line in det.act_code_ids:
                values={
                'fecha_comprobante':det.transaction_date,
                'partner_id':det.partner_id.id,
                'nro_comp':det.name,
                'invoice_number':det_line.invoice_number,
                'invoice_ctrl_number':det_line.invoice_ctrl_number,
                'factura_total':signo*self.conv_div_nac(det.invoice_id.amount_total,det),
                'base_imponible':signo*det_line.base_tax,
                'retenido':signo*det_line.wh_amount,
                'porcentaje':det_line.aliquot,
                'codigo':det_line.code,
                'invoice_id':det.invoice_id.id,
                }
                pdf_id = t.create(values)
        #   temp = self.env['account.wizard.pdf.ventas'].search([])
        self.line = self.env['resumen.municipal.wizard.pdf'].search([])

    def print_resumen_municipal(self):
        #pass
        self.get_invoice()
        return {'type': 'ir.actions.report','report_name': 'l10n_ve_resumen_retenciones.libro_resumen_municipal','report_type':"qweb-pdf"}