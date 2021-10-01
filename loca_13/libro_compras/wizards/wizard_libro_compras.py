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

class LibroVentasModelo(models.Model):
    _name = "account.wizard.pdf.compras" 

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

    def formato_fecha2(self,date):
        fecha = str(date)
        fecha_aux=fecha
        ano=fecha_aux[0:4]
        mes=fecha[5:7]
        dia=fecha[8:10]  
        resultado=dia+"/"+mes+"/"+ano
        return resultado
    
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


    # FUNCION QUE HACE LAS CONVERSIONES DE LAS DIVISAS
    """def conv_div(self,valor):
        self.currency_id.id
        fecha_contable_doc=self.invoice_id.date
        monto_factura=self.invoice_id.amount_total
        valor_aux=0.000000000000001
        tasa= self.env['res.currency.rate'].search([('currency_id','=',self.currency_id.id),('name','<=',fecha_contable_doc)],order="name asc")
        #raise UserError(_('tasa: %s')%tasa)
        for det_tasa in tasa:
            if fecha_contable_doc>=det_tasa.name:
                valor_aux=det_tasa.rate
        rate=round(1/valor_aux,2)  # LANTA
        #rate=round(valor_aux,2)  # ODOO SH
        resultado=monto_factura*rate
        return resultado"""

    def conv_div(self,valor):
        self.invoice_id.currency_id.id
        fecha_contable_doc=self.invoice_id.date
        monto_factura=self.invoice_id.amount_total
        valor_aux=0
        prueba=valor
        #raise UserError(_('moneda compañia: %s')%self.company_id.currency_id.id)
        if self.invoice_id.company_id.currency_id.id!=self.currency_id.id:
            tasa= self.env['account.move'].search([('id','=',self.invoice_id.id)],order="id asc")
            for det_tasa in tasa:
                monto_nativo=det_tasa.amount_untaxed_signed
                monto_extran=det_tasa.amount_untaxed
                valor_aux=abs(monto_nativo/monto_extran)
            rate=round(valor_aux,3)  # LANTA
            #rate=round(valor_aux,2)  # ODOO SH
            resultado=valor*rate
        else:
            resultado=valor
        return resultado

    def float_format_div(self,valor):
        #valor=self.base_tax
        if valor:
            result = '{:,.2f}'.format(valor)
            result = result.replace(',','*')
            result = result.replace('.',',')
            result = result.replace('*','.')
        else:
            result="0,00"
        return result

    def doc_cedula(self,aux):
        #nro_doc=self.partner_id.vat
        nro_doc="00000000"
        tipo_doc="V"
        busca_partner = self.env['res.partner'].search([('id','=',aux)])
        for det in busca_partner:
            tipo_doc=det.doc_type
            if det.vat:
                nro_doc=str(det.vat)
            else:
                nro_doc="00000000"
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

class libro_ventas(models.TransientModel):
    _name = "account.wizard.libro.compras" ## = nombre de la carpeta.nombre del archivo deparado con puntos

    facturas_ids = fields.Many2many('account.move', string='Facturas', store=True) ##Relacion con el modelo de la vista de la creacion de facturas
    retiva_ids = 0 ## Malo

    tax_ids = fields.Many2many('account.tax', string='Facturas_1', store=True)

    #line_tax_ids = fields.Many2many('account.move.line.tax', string='Facturas_2', store=True)
    line_ids = fields.Many2many('account.move.line', string='Facturas_3', store=True)
    #invoice_ids = fields.Char(string="idss", related='facturas_ids.id')

    date_from = fields.Date(string='Date From', default=lambda *a:datetime.now().strftime('%Y-%m-%d'))
    date_to = fields.Date('Date To', default=lambda *a:(datetime.now() + timedelta(days=(1))).strftime('%Y-%m-%d'))

    # fields for download xls
    state = fields.Selection([('choose', 'choose'), ('get', 'get')],default='choose') ##Genera los botones de exportar xls y pdf como tambien el de cancelar
    report = fields.Binary('Prepared file', filters='.xls', readonly=True)
    name = fields.Char('File Name', size=32)
    company_id = fields.Many2one('res.company','Company',default=lambda self: self.env.user.company_id.id)

    line  = fields.Many2many(comodel_name='account.wizard.pdf.compras', string='Lineas')
    
    def conv_div_nac(self,valor,selff):
        selff.invoice_id.currency_id.id
        fecha_contable_doc=selff.invoice_id.date
        monto_factura=selff.invoice_id.amount_total
        valor_aux=0
        prueba=22
        #raise UserError(_('moneda compañia: %s')%self.company_id.currency_id.id)
        if selff.invoice_id.currency_id.id!=self.company_id.currency_id.id:
            tasa= self.env['account.move'].search([('id','=',selff.invoice_id.id)],order="id asc")
            for det_tasa in tasa:
                monto_nativo=det_tasa.amount_untaxed_signed
                monto_extran=det_tasa.amount_untaxed
                valor_aux=abs(monto_nativo/monto_extran)
            rate=round(valor_aux,3)  # LANTA
            #rate=round(valor_aux,2)  # ODOO SH
            resultado=valor*rate
        else:
            resultado=valor
        return resultado

    def get_company_address(self):
        location = ''
        streets = ''
        if self.company_id:
            streets = self._get_company_street()
            location = self._get_company_state_city()
        _logger.info("\n\n\n street %s location %s\n\n\n", streets, location)
        return  (streets + " " + location)

    def _get_company_street(self):
        street2 = ''
        av = ''
        if self.company_id.street:
            av = str(self.company_id.street or '')
        if self.company_id.street2:
            street2 = str(self.company_id.street2 or '')
        result = av + " " + street2
        return result


    def _get_company_state_city(self):
        state = ''
        city = ''
        if self.company_id.state_id:
            state = "Edo." + " " + str(self.company_id.state_id.name or '')
            _logger.info("\n\n\n state %s \n\n\n", state)
        if self.company_id.city:
            city = str(self.company_id.city or '')
            _logger.info("\n\n\n city %s\n\n\n", city)
        result = city + " " + state
        _logger.info("\n\n\n result %s \n\n\n", result)
        return  result


    def doc_cedula2(self,aux):
        #nro_doc=self.partner_id.vat
        busca_partner = self.env['res.partner'].search([('id','=',aux)])
        for det in busca_partner:
            tipo_doc=det.doc_type
            nro_doc=str(det.vat)
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
        resultado=str(tipo_doc)+str(nro_doc)
        return resultado
        
    def get_invoice(self):
        t=self.env['account.wizard.pdf.compras']
        d=t.search([])
        d.unlink()
        cursor_resumen = self.env['account.move.line.resumen'].search([
            ('fecha_fact','>=',self.date_from),
            ('fecha_fact','<=',self.date_to),
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
        self.line = self.env['account.wizard.pdf.compras'].search([])


    def print_facturas(self):
        self.get_invoice()
        #return self.env.ref('libro_ventas.libro_factura_clientes').report_action(self)
        return {'type': 'ir.actions.report','report_name': 'libro_compras.libro_factura_proveedores','report_type':"qweb-pdf"}




    def cont_row(self):
        row = 0
        for record in self.facturas_ids:
            row +=1
        return row

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

    def float_format_div2(self,valor):
        #valor=self.base_tax
        if valor:
            result = '{:,.2f}'.format(valor)
            result = result.replace(',','*')
            result = result.replace('.',',')
            result = result.replace('*','.')
        else:
            result="0,00"
        return result


# *******************  REPORTE EN EXCEL ****************************

    def generate_xls_report(self):
        self.get_invoice()

        wb1 = xlwt.Workbook(encoding='utf-8')
        ws1 = wb1.add_sheet('Compras')
        fp = BytesIO()

        header_content_style = xlwt.easyxf("font: name Helvetica size 20 px, bold 1, height 170;")
        sub_header_style = xlwt.easyxf("font: name Helvetica size 10 px, bold 1, height 170; borders: left thin, right thin, top thin, bottom thin;")
        sub_header_style_c = xlwt.easyxf("font: name Helvetica size 10 px, bold 1, height 170; borders: left thin, right thin, top thin, bottom thin; align: horiz center")
        sub_header_style_r = xlwt.easyxf("font: name Helvetica size 10 px, bold 1, height 170; borders: left thin, right thin, top thin, bottom thin; align: horiz right")
        sub_header_content_style = xlwt.easyxf("font: name Helvetica size 10 px, height 170;")
        line_content_style = xlwt.easyxf("font: name Helvetica, height 170;")
        row = 0
        col = 0
        ws1.row(row).height = 500
        ws1.write_merge(row,row, 0, 4, "Libro de Compras", header_content_style)
        row += 2
        ws1.write_merge(row, row, 0, 1, "Razon Social :", sub_header_style)
        ws1.write_merge(row, row, 2, 4,  str(self.company_id.name), sub_header_content_style)
        row+=1
        ws1.write_merge(row, row, 0, 1, "RIF:", sub_header_style)
        ws1.write_merge(row, row, 2, 4, str(self.company_id.partner_id.doc_type.upper()) +'-'+ str(self.company_id.partner_id.vat), sub_header_content_style)
        row+=1
        ws1.write_merge(row, row, 0, 1, "Direccion Fiscal:", sub_header_style)
        ws1.write_merge(row, row, 2, 5, str(self.get_company_address()), sub_header_content_style)
        row +=1
        ws1.write(row, col+0, "Desde :", sub_header_style)
        #fec_desde = datetime.strftime(datetime.strptime(self.date_from,DEFAULT_SERVER_DATE_FORMAT),"%d/%m/%Y")
        fec_desde = self.line.formato_fecha2(self.date_from)

        ws1.write(row, col+1, fec_desde, sub_header_content_style)
        row += 1
        ws1.write(row, col+0, "Hasta :", sub_header_style)
        #fec_hasta = datetime.strftime(datetime.strptime(self.date_to,DEFAULT_SERVER_DATE_FORMAT),"%d/%m/%Y")
        fec_hasta = self.line.formato_fecha2(self.date_to)
        ws1.write(row, col+1, fec_hasta, sub_header_content_style)
        row += 2
        ws1.write_merge(row, row, 15, 21,"Compras Internas o Importacion Gravada",sub_header_style_c)
        row += 1
        #CABECERA DE LA TABLA 
        ws1.write(row,col+0,"#",sub_header_style_c)
        ws1.write(row,col+1,"Fecha Documento",sub_header_style_c)
        ws1.col(col+1).width = int((len('Fecha Documento')+3)*256)
        ws1.write(row,col+2,"RIF",sub_header_style_c)
        ws1.col(col+2).width = int((len('J-456987531')+2)*256)
        ws1.write(row,col+3,"Nombre Razon Social",sub_header_style_c)
        ws1.col(col+3).width = int(len('Nombre Razon Social')*256)
        ws1.write(row,col+4,"Tipo de Persona",sub_header_style_c)
        ws1.col(col+4).width = int(len('Tipo de Persona')*256)
        ws1.write(row,col+5,"Numero de Planilla de exportacion",sub_header_style_c)
        ws1.col(col+5).width = int(len('Numero de Planilla de Importaciones')*256)

        ws1.write(row,col+6,"Número Expediente Importaciones",sub_header_style_c)
        ws1.col(col+6).width = int(len('Número Expediente Importaciones')*256)
        ws1.write(row,col+7,"Fecha de Importaciones",sub_header_style_c)
        ws1.col(col+7).width = int(len('Fecha de Importaciones')*256)

        ws1.write(row,col+8,"Nro Factura / Entrega",sub_header_style_c)
        ws1.col(col+8).width = int(len('Nro. Factura / Entrega')*256)
        ws1.write(row,col+9,"Nro de Control",sub_header_style_c)
        ws1.col(col+9).width = int(len('Nro de control')*256)
        ws1.write(row,col+10,"Nro de nota de debito",sub_header_style_c)
        ws1.col(col+10).width = int(len('Nro de nota de debito')*256)
        ws1.write(row,col+11,"Numero de nota de credito ",sub_header_style_c)
        ws1.col(col+11).width = int(len('Numero de nota de credito')*256)
        ws1.write(row,col+12,"Nro Factura Afectada",sub_header_style_c)
        ws1.col(col+12).width = int(len('Nro de factura afectada')*256)
        ws1.write(row,col+13,"Tipo de transacc.",sub_header_style_c)
        ws1.col(col+13).width = int(len('Tipo de transacc.')*256)
        ws1.write(row,col+14,"Compras Incluyendo el IVA",sub_header_style_c)
        ws1.col(col+14).width = int(len('Compras Incluyendo el IVA')*256)
        ws1.write(row,col+15,"Valor Total de Importaciones",sub_header_style_c)
        ws1.col(col+15).width = int(len('Valor Total de Importacione')*256)
        ws1.write(row,col+16,"Compras Exentas o Exoneradas",sub_header_style_c)
        ws1.col(col+16).width = int(len('Compras Exentas o Exoneradas')*256)
        # CONTRIBUYENTES
        ws1.write(row,col+17,"Base Imponible",sub_header_style_c)
        ws1.col(col+17).width = int(len('Base Imponible')*256)
        ws1.write(row,col+18,"Alicuota Reducida",sub_header_style_c)
        ws1.col(col+18).width = int(len('Alicuota Reducida')*256)
        ws1.write(row,col+19,"Impuesto Iva",sub_header_style_c)
        ws1.col(col+19).width = int(len('Impuesto Iva')*256)
        ws1.write(row,col+20,"Alicuota General",sub_header_style_c)
        ws1.col(col+20).width = int(len('Alicuota General')*256)
        ws1.write(row,col+21,"Base Imponible",sub_header_style_c)
        ws1.col(col+21).width = int(len('Base Imponible')*256)
        ws1.write(row,col+22,"Alicuota General + Adicional",sub_header_style_c)
        ws1.col(col+22).width = int(len('Alicuota General + Adicional')*256)
        ws1.write(row,col+23,"Impuesto Iva",sub_header_style_c)
        ws1.col(col+23).width = int(len('Impuesto Iva')*256)
        
        ws1.write(row,col+24,"Iva retenido (Vendedor)",sub_header_style_c)
        ws1.col(col+24).width = int(len('Iva retenido (Vendedor)')*256)
        ws1.write(row,col+25,"Nro Comprobante",sub_header_style_c)
        ws1.col(col+25).width = int(len('Nro Comprobante')*256)
        ws1.write(row,col+26,"Fecha Comp.",sub_header_style_c)
        ws1.col(col+26).width = int(len('Fecha Comp.')*256)

        center = xlwt.easyxf("align: horiz center")
        right = xlwt.easyxf("align: horiz right")
        numero = 1

        contador=0
        acum_venta_iva=0
        acum_exento=0
        acum_fob=0
        # variables de contribuyentes
        acum_b_reducida=0
        acum_reducida=0
        acum_b_general=0                          
        acum_iva=0
        # variables no contribuyentes
        acum_b_reducida2=0
        acum_reducida2=0
        acum_b_general2=0
        acum_iva2=0

        acum_general=0
        acum_base=0              
        acum_adicional1=0
        acum_adicional=0
        acum_base2=0             
        acum_adicional2=0

        acum_iva_ret=0

        acum_base_general=0
        acum_base_adicional=0
        acum_base_reducida=0

        acum_ret_general=0
        acum_ret_adicional=0
        acum_ret_reducida=0

        total_bases=0
        total_debitos=0
        total_retenidos=0

        for invoice in self.line.sorted(key=lambda x: (x.invoice_id.invoice_date,x.invoice_id.id ),reverse=False):
            # variables para los resumenes de totales
            acum_base_general=acum_base_general+invoice.base_general
            acum_general=acum_general+invoice.alicuota_general
            acum_base_adicional=acum_base_adicional+invoice.base_adicional
            acum_base_reducida=acum_base_reducida+invoice.base_reducida
            acum_adicional=acum_adicional+invoice.alicuota_adicional
            if invoice.state_retantion == 'posted':
                acum_ret_general=acum_ret_general+invoice.retenido_general
                acum_ret_adicional=acum_ret_adicional+invoice.retenido_adicional
                acum_ret_reducida=acum_ret_reducida+invoice.retenido_reducida
            # fin variables resumenes totales
            row += 1
            ws1.write(row,col+0,str(numero),center)
            ws1.write(row,col+1,str(invoice.formato_fecha2(invoice.invoice_id.invoice_date)),center)
            ws1.write(row,col+2,str(invoice.doc_cedula(invoice.partner.id)),center)
            ws1.write(row,col+3,str(invoice.partner.name),center)
            if invoice.partner.people_type == 'resident_nat_people':
                ws1.write(row,col+4,'PNRE',center)
            elif invoice.partner.people_type == 'non_resit_nat_people':
                ws1.write(row,col+4,'PNNR',center)
            elif invoice.partner.people_type == 'domi_ledal_entity':
                ws1.write(row,col+4,'PJDO',center)
            elif invoice.partner.people_type == 'legal_ent_not_domicilied':
                ws1.write(row,col+4,'PJND',center)
            else :
                ws1.write(row,col+4,'')

            if invoice.invoice_id.import_form_num:
                ws1.write(row,col+5,str(invoice.invoice_id.import_form_num),center) # planilla de exportacion
            else:
                ws1.write(row,col+5,'')

            if invoice.invoice_id.import_dossier:
                ws1.write(row,col+6,invoice.invoice_id.import_dossier,center)
            else:
                ws1.write(row,col+6,'')

            if invoice.invoice_id.import_date:
                ws1.write(row,col+7,invoice.invoice_id.import_date,center)
            else:
                ws1.write(row,col+7,'')

            if invoice.tipo_doc == '01':
                ws1.write(row,col+8,str(invoice.invoice_number),center)
            else:
                ws1.write(row,col+8,'')

            ws1.write(row,col+9,str(invoice.invoice_ctrl_number),center)

            if invoice.tipo_doc == '02':
                ws1.write(row,col+10,str(invoice.invoice_number),center)
            else:
                ws1.write(row,col+10,' ',center)
            if invoice.tipo_doc == '03':
                 ws1.write(row,col+11,str(invoice.invoice_number),center)
            else:
                ws1.write(row,col+11,' ',center)

            if invoice.tipo_doc == '03' or invoice.tipo_doc == '02':
                ws1.write(row,col+12,str(invoice.ref),center)
            else:
                ws1.write(row,col+12,' ',center)

            ws1.write(row,col+13,str(invoice.tipo_doc+'-Reg'),center)

# corregir a partir de aqui
            if invoice.invoice_id.partner_id.vendor != 'international':
                ws1.write(row,col+14,invoice.sale_total,right) # total venta iva incluido
                acum_venta_iva=acum_venta_iva+invoice.sale_total

            if invoice.invoice_id.partner_id.vendor == 'international':
                ws1.write(row,col+15,invoice.sale_total,right) # total valor FOB
                acum_fob=acum_fob+invoice.sale_total

            if invoice.invoice_id.partner_id.vendor != 'international':
                ws1.write(row,col+16,invoice.total_exento,right) # total exento
                acum_exento=acum_exento+invoice.total_exento

            # CAMPOS CONTRIBUYENTES ***************

            if invoice.invoice_id.partner_id.vendor != 'international':
                ws1.write(row,col+17,invoice.base_reducida,right)
                acum_b_reducida=acum_b_reducida+invoice.base_reducida

            if invoice.invoice_id.partner_id.vendor != 'international':
                if invoice.base_reducida!=0:
                    ws1.write(row,col+18,"8%",center)
                else:
                    ws1.write(row,col+18," ",center)

            if invoice.invoice_id.partner_id.vendor != 'international':
                ws1.write(row,col+19,invoice.alicuota_reducida,right)
                acum_reducida=acum_reducida+invoice.alicuota_reducida

            if invoice.invoice_id.partner_id.vendor != 'international':
                if invoice.base_general!=0:
                    ws1.write(row,col+20,"16%",center)
                else:
                    ws1.write(row,col+20," ",center)

            if invoice.invoice_id.partner_id.vendor != 'international':
                ws1.write(row,col+21,invoice.base_general+invoice.base_adicional,right)
                acum_b_general=acum_b_general+(invoice.base_general+invoice.base_adicional)

            if invoice.invoice_id.partner_id.vendor != 'international':
                if invoice.base_adicional!=0:
                    ws1.write(row,col+22,"31%",center)
                else:
                    ws1.write(row,col+22," ",center)

            if invoice.invoice_id.partner_id.vendor != 'international':
                ws1.write(row,col+23,invoice.alicuota_general+invoice.alicuota_adicional,right)
                acum_iva=acum_iva+(invoice.alicuota_general+invoice.alicuota_adicional)

            
            if invoice.vat_ret_id.state == 'posted':
                if invoice.invoice_id.partner_id.vendor != 'international':
                    ws1.write(row,col+24,invoice.iva_retenido,right) # IVA RETENIDO
                    acum_iva_ret=acum_iva_ret+invoice.iva_retenido

            if invoice.vat_ret_id.state == 'posted':
                ws1.write(row,col+25,str(invoice.retenido),right) # NRO CONTROL
                ws1.write(row,col+26,str(invoice.formato_fecha2(invoice.retenido_date)),right) # FECHA COMPROBANTE
            numero=numero+1

        # ******* FILA DE TOTALES **********
        row=row+1
        ws1.write(row,col+13," TOTALES",sub_header_style)
        ws1.write(row,col+14,str(acum_venta_iva),right)
        ws1.write(row,col+15,str(acum_fob),right)
        ws1.write(row,col+16,str(acum_exento),right)
        # contribuyentes
        ws1.write(row,col+17,str(acum_b_reducida),right)
        ws1.write(row,col+18,'---',center)
        ws1.write(row,col+19,str(acum_reducida),right)
        #ws1.write(row,col+17,str(),right)
        ws1.write(row,col+20,'---',center)
        ws1.write(row,col+21,str(acum_b_general),right)
        ws1.write(row,col+22,'---',center)
        ws1.write(row,col+23,str(acum_iva),right)

        ws1.write(row,col+24,str(acum_iva_ret),right)

        # ********* FILA DE TITULOS DE RESUMENES DE VENTAS
        row=row+1
        ws1.write_merge(row, row, 15, 17,"RESUMEN DE COMPRAS",sub_header_style_c)
        ws1.write_merge(row, row, 18, 20,"Base Imponible",sub_header_style_c)
        ws1.write_merge(row, row, 21, 22,"Crédito Fiscal",sub_header_style_c)
        ws1.write_merge(row, row, 23, 25,"Iva Retenidos por Compras",sub_header_style_c)

        # ************* fila exentas o exoneradas *********
        row=row+1
        ws1.write_merge(row, row, 15, 17,"Compras internas Exentas o Exoneradas",right)
        ws1.write_merge(row, row, 18, 20,acum_exento,right)
        total_bases=total_bases+acum_exento
        ws1.write_merge(row, row, 21, 22,"0.00",right)
        ws1.write_merge(row, row, 23, 25,"0.00",right)

        # ************* fila SOLO ALICUOTA GENERAL *********
        row=row+1
        ws1.write_merge(row, row, 15, 17,"Compras Internas Afectadas sólo Alícuota General",right)
        ws1.write_merge(row, row, 18, 20,acum_base_general,right)
        total_bases=total_bases+acum_base_general
        ws1.write_merge(row, row, 21, 22,acum_general,right)
        total_debitos=total_debitos+(acum_general)
        ws1.write_merge(row, row, 23, 25,acum_ret_general,right)
        total_retenidos=total_retenidos+acum_ret_general

        # ************* fila ALICUOTA GENERAL MAS ADICIONAL *********
        row=row+1
        ws1.write_merge(row, row, 15, 17,"Compras Internas Afectadas sólo Alícuota General + Adicional",right)
        ws1.write_merge(row, row, 18, 20,acum_base_adicional,right)
        total_bases=total_bases+acum_base_adicional
        ws1.write_merge(row, row, 21, 22,acum_adicional,right)
        total_debitos=total_debitos+acum_adicional
        ws1.write_merge(row, row, 23, 25,acum_ret_adicional,right)
        total_retenidos=total_retenidos+acum_ret_adicional

        # ************* fila REDUCIDA *********
        row=row+1
        ws1.write_merge(row, row, 15, 17,"Compras Internas Afectadas sólo Alícuota Reducida",right)
        ws1.write_merge(row, row, 18, 20,acum_base_reducida,right)
        total_bases=total_bases+acum_base_reducida
        ws1.write_merge(row, row, 21, 22,acum_reducida+acum_reducida2,right)
        total_debitos=total_debitos+(acum_reducida+acum_reducida2)
        ws1.write_merge(row, row, 23, 25,acum_ret_reducida,right)
        total_retenidos=total_retenidos+acum_ret_reducida

        # ************* fila EXPORTACION *********
        row=row+1
        ws1.write_merge(row, row, 15, 17,"Compras Internacionales",right)
        ws1.write_merge(row, row, 18, 20,acum_fob,right)
        total_bases=total_bases+acum_fob
        ws1.write_merge(row, row, 21, 22,"0.00",right)
        ws1.write_merge(row, row, 23, 25,"0.00",right)

        # ************* fila totales*********
        row=row+1
        ws1.write_merge(row, row, 15, 17,"TOTAL:",right)
        ws1.write_merge(row, row, 18, 20,total_bases,right)
        ws1.write_merge(row, row, 21, 22,total_debitos,right)
        ws1.write_merge(row, row, 23, 25,total_retenidos,right)

        wb1.save(fp)
        out = base64.encodestring(fp.getvalue())
        fecha  = datetime.now().strftime('%d/%m/%Y') 
        self.write({'state': 'get', 'report': out, 'name':'Libro de compras '+ fecha+'.xls'})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.wizard.libro.compras',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }