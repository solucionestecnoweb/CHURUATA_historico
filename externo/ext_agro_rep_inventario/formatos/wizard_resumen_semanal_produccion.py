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
    _name = "resumen.semanal.pdf"

    location_id = fields.Many2one('stock.location')
    inventario_total = fields.Float('Total Inventario')
    mortalidad = fields.Float('Mortalidad')
    porcentaje_mortalidad = fields.Float()
    #partner_id  = fields.Many2one(comodel_name='res.partner', string='Partner')

    #fecha_comprobante = fields.Date(string='Fecha')
    #partner_id  = fields.Many2one(comodel_name='res.partner', string='Partner')
    #invoice_number =   fields.Char(string='Fac. Número')
    #invoice_ctrl_number = fields.Char(string='Nro Control')
    #nro_comp = fields.Char(string='Nro Comprobante')
    #factura_total = fields.Float(string='Monto Factura')
    #base_imponible = fields.Float(string='base imponible')
    #retenido = fields.Float(string='retenido')
    #porcentaje = fields.Float(string='Porcentaje')
    #codigo = fields.Char(string='Código Actividad Económica')
    #invoice_id = fields.Many2one('account.move')

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


class WizardReport_2(models.TransientModel): # aqui declaro las variables del wizar que se usaran para el filtro del pdf
    _name = 'wizard.resumen.semanal.produccion'
    _description = "Resumen semanal de produccion tem"

    date_from  = fields.Date('Date From', default=lambda *a:(datetime.now() - timedelta(days=(1))).strftime('%Y-%m-%d'))
    date_to = fields.Date(string='Date To', default=lambda *a:datetime.now().strftime('%Y-%m-%d'))
    date_actual = fields.Date(default=lambda *a:datetime.now().strftime('%Y-%m-%d'))

    company_id = fields.Many2one('res.company','Company',default=lambda self: self.env.user.company_id.id)
    line  = fields.Many2many(comodel_name='resumen.semanal.pdf', string='Lineas')

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


    def get_invoice(self):
        inventario_total=0
        t=self.env['resumen.semanal.pdf']
        d=t.search([])
        d.unlink()
        cursor_resumen = self.env['stock.location'].search([('usage','=','internal'),('active','=',True),('scrap_location','=',False),('x_studio_ubicacin_final','=','si')])
        #raise UserError(_('cursor_resumen: %s')%cursor_resumen)
        if cursor_resumen:
            for det in cursor_resumen:
                inventario_total=self.total_stock(det.id)
                values={
                'location_id':det.id,
                'inventario_total':inventario_total,
                }
                pdf_id = t.create(values)
        #   temp = self.env['account.wizard.pdf.ventas'].search([])
        self.line = self.env['resumen.semanal.pdf'].search([])

    def total_stock(self,id_location):
        total=0
        lista_quant=self.env['stock.quant'].search([('location_id','=',id_location)])
        if lista_quant:
            for dett in lista_quant:
                total=total+dett.quantity
        return total

    def print_resumen(self):
        #pass
        self.get_invoice()
        return {'type': 'ir.actions.report','report_name': 'ext_agro_rep_inventario.resumen_semanal','report_type':"qweb-pdf"}