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

_logger = logging.getLogger(__name__)

class CostoGananciaModelo(models.Model):
    _name = "stock.wizard.pdf.costogana"

    name = fields.Date(string='Fecha')
    product_id = fields.Many2one('product.template', 'Productos')
    cantidad = fields.Float()
    valor_venta_unit = fields.Float()
    sub_total = fields.Float()
    costo_unit=fields.Float()
    costo_total = fields.Float()
    ganancia_total = fields.Float()

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

class costo_ganancia(models.TransientModel):
    _name = "stock.wizard.costo.ganancia" ## = nombre de la carpeta.nombre del archivo deparado con puntos

    date_from = fields.Date(string='Date From', default=lambda *a:datetime.now().strftime('%Y-%m-%d'))
    date_to = fields.Date('Date To', default=lambda *a:(datetime.now() + timedelta(days=(1))).strftime('%Y-%m-%d'))
    # fields for download xls
    state = fields.Selection([('choose', 'choose'), ('get', 'get')],default='choose') ##Genera los botones de exportar xls y pdf como tambien el de cancelar
    report = fields.Binary('Prepared file', filters='.xls', readonly=True)
    name = fields.Char('File Name', size=32)
    company_id = fields.Many2one('res.company','Company',default=lambda self: self.env.user.company_id.id)

    line  = fields.Many2many(comodel_name='stock.wizard.pdf.costogana', string='Lineas')

    def doc_cedula(self,aux):
        #nro_doc=self.partner_id.vat
        busca_partner = self.env['res.partner'].search([('id','=',aux)])
        for det in busca_partner:
            tipo_doc=busca_partner.doc_type
            if busca_partner.vat:
                nro_doc=str(busca_partner.vat)
            else:
                nro_doc="00000000"
            tipo_doc=busca_partner.doc_type
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
        resultado=str(tipo_doc)+str(nro_doc)
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

    def periodo(self,date):
        fecha = str(date)
        fecha_aux=fecha
        ano=fecha_aux[0:4]
        mes=fecha[5:7]
        dia=fecha[8:10]  
        resultado=dia+"/"+mes+"/"+ano
        return resultado

    def print_costo_ganancia(self):
        self.env['stock.wizard.pdf.costogana'].search([]).unlink()
        self.lista_producto()
        return {'type': 'ir.actions.report','report_name': 'odoo_process_costing_manufacturing.reporte_costo_ganancia','report_type':"qweb-pdf"}
        #self.env['stock.wizard.costo.ganancia'].search([]).unlink()

    def lista_producto(self):
        cursor_resumen = self.env['product.template'].search([('sale_ok','=','True'),('producto_terminado','=','s')],order ="id ASC")
        t=self.env['stock.wizard.pdf.costogana']
        d=t.search([])
        for det in cursor_resumen:
            values={
            'name':"2021-01-01",
            'product_id':det.id,
            'cantidad':self.busca_cantidad(det),
            'valor_venta_unit':det.list_price,
            'sub_total':self.busca_sub(det),
            'costo_unit':det.standard_price,
            'costo_total':self.busca_cantidad(det)*det.standard_price, #self.costo_total(det),
            'ganancia_total':self.busca_sub(det)-(self.busca_cantidad(det)*det.standard_price),
            }
            pdf_id = t.create(values)
        self.line = self.env['stock.wizard.pdf.costogana'].search([])

    def busca_cantidad(self,dett):
        quantity=0
        product_id=self.id_producto(dett)
        lista_fact=self.env['account.move.line'].search([('product_id','=',product_id)])
        if lista_fact:
            for det_list in lista_fact:
                if det_list.move_id.type=="out_invoice" or det_list.move_id.type=="out_refund" or det_list.move_id.type=="out_receipt":
                    quantity=quantity+det_list.quantity
        return quantity

    def id_producto(self,dete):
        lista_product=self.env['product.product'].search([('product_tmpl_id','=',dete.id)])
        for detalle in lista_product:
            id_producto=detalle.id
        return id_producto


    def busca_sub(self,dett):
        sub_totales=0
        product_id=self.id_producto(dett)
        lista_fact=self.env['account.move.line'].search([('product_id','=',product_id)])
        if lista_fact:
            for det_list in lista_fact:
                if det_list.move_id.type=="out_invoice" or det_list.move_id.type=="out_refund" or det_list.move_id.type=="out_receipt":
                    sub_totales=sub_totales+det_list.price_subtotal
        return sub_totales