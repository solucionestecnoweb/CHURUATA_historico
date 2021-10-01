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

class LibroComprasModelo(models.Model):
    _name = "resumen.iva.wizard.pdf"

    name = fields.Date(string='Fecha')
    document = fields.Char(string='Rif')
    partner  = fields.Many2one(comodel_name='res.partner', string='Partner')
    invoice_number =   fields.Char(string='invoice_number')
    tipo_doc = fields.Char(string='tipo_doc')
    invoice_ctrl_number = fields.Char(string='invoice_ctrl_number')
    sale_total = fields.Float(string='invoice_ctrl_number')
    base_imponible = fields.Float(string='invoice_ctrl_number')
    iva = fields.Float(string='iva')
    iva_retenido = fields.Float(string='iva retenido')
    retenido = fields.Char(string='retenido')
    retenido_date = fields.Date(string='date')
    alicuota = fields.Char(string='alicuota')
    alicuota_type = fields.Char(string='alicuota type')
    state_retantion = fields.Char(string='state')
    state = fields.Char(string='state')
    reversed_entry_id = fields.Many2one('account.move', string='Facturas', store=True)
    currency_id = fields.Many2one('res.currency', 'Currency')
    ref = fields.Char(string='ref')

    total_exento = fields.Float(string='Total Excento')
    alicuota_reducida = fields.Float(string='Alicuota Reducida')
    alicuota_general = fields.Float(string='Alicuota General')
    alicuota_adicional = fields.Float(string='Alicuota General + Reducida')

    base_general = fields.Float(string='Total Base General')
    base_reducida = fields.Float(string='Total Base Reducida')
    base_adicional = fields.Float(string='Total Base General + Reducida')

    retenido_general = fields.Float(string='retenido General')
    retenido_reducida = fields.Float(string='retenido Reducida')
    retenido_adicional = fields.Float(string='retenido General + Reducida')

    vat_ret_id = fields.Many2one('vat.retention', string='Nro de Comprobante IVA')
    invoice_id = fields.Many2one('account.move')
    tax_id = fields.Many2one('account.tax', string='Tipo de Impuesto')


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

class WizardReport_1(models.TransientModel): # aqui declaro las variables del wizar que se usaran para el filtro del pdf
    _name = 'wizard.resumen.iva'
    _description = "Resumen Retenciones IVA"

    date_from  = fields.Date('Date From', default=lambda *a:(datetime.now() - timedelta(days=(1))).strftime('%Y-%m-%d'))
    date_to = fields.Date(string='Date To', default=lambda *a:datetime.now().strftime('%Y-%m-%d'))
    date_actual = fields.Date(default=lambda *a:datetime.now().strftime('%Y-%m-%d'))

    company_id = fields.Many2one('res.company','Company',default=lambda self: self.env.user.company_id.id)
    line  = fields.Many2many(comodel_name='resumen.iva.wizard.pdf', string='Lineas')

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
        t=self.env['resumen.iva.wizard.pdf']
        d=t.search([])
        d.unlink()
        cursor_resumen = self.env['account.move.line.resumen'].search([
            ('fecha_fact','>=',self.date_from),
            ('fecha_fact','<=',self.date_to),
            ('state_voucher_iva','=','posted'),
            ('state','in',('posted','cancel' )),
            ('type','in',('in_invoice','in_refund','in_receipt'))
            ])
        for det in cursor_resumen:
            values={
            'name':det.fecha_fact,
            'document':det.invoice_id.name,
            'partner':det.invoice_id.partner_id.id,
            'invoice_number': det.invoice_id.invoice_number,#darrell
            'tipo_doc': det.tipo_doc,
            'invoice_ctrl_number': det.invoice_id.invoice_ctrl_number,
            'sale_total': self.conv_div_nac(det.total_con_iva,det),
            'base_imponible': self.conv_div_nac(det.total_base,det),
            'iva' : self.conv_div_nac(det.total_valor_iva,det),
            'iva_retenido': self.conv_div_nac(det.total_ret_iva,det),
            'retenido': det.vat_ret_id.name,
            'retenido_date':det.vat_ret_id.voucher_delivery_date,
            'state_retantion': det.vat_ret_id.state,
            'state': det.invoice_id.state,
            'currency_id':det.invoice_id.currency_id.id,
            'ref':det.invoice_id.ref,
            'total_exento':self.conv_div_nac(det.total_exento,det),
            'alicuota_reducida':self.conv_div_nac(det.alicuota_reducida,det),
            'alicuota_general':self.conv_div_nac(det.alicuota_general,det),
            'alicuota_adicional':self.conv_div_nac(det.alicuota_adicional,det),
            'base_adicional':self.conv_div_nac(det.base_adicional,det),
            'base_reducida':self.conv_div_nac(det.base_reducida,det),
            'base_general':self.conv_div_nac(det.base_general,det),
            'retenido_reducida':self.conv_div_nac(det.retenido_reducida,det),
            'retenido_adicional':self.conv_div_nac(det.retenido_adicional,det),
            'retenido_general':self.conv_div_nac(det.retenido_general,det),
            'vat_ret_id':det.vat_ret_id.id,
            'invoice_id':det.invoice_id.id,
            'tax_id':det.tax_id.id,
            }
            pdf_id = t.create(values)
        #   temp = self.env['account.wizard.pdf.ventas'].search([])
        self.line = self.env['resumen.iva.wizard.pdf'].search([])

    def print_resumen_iva(self):
        self.get_invoice()
        #return self.env.ref('libro_ventas.libro_factura_clientes').report_action(self)
        return {'type': 'ir.actions.report','report_name': 'l10n_ve_resumen_retenciones.libro_resumen_iva','report_type':"qweb-pdf"}