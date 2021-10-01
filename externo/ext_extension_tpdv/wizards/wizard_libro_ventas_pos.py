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

class LibroVentasPosModelo(models.Model):
    _name = "pos.wizard.pdf.ventas" 

    name = fields.Date(string='Fecha')
    document = fields.Char(string='Rif')
    #partner  = fields.Many2one(comodel_name='res.partner', string='Partner')
    tipo_doc = fields.Char(string='tipo_doc')
    sale_total = fields.Float(string='invoice_ctrl_number')
    base_imponible = fields.Float(string='invoice_ctrl_number')
    iva = fields.Float(string='iva')
    iva_retenido = fields.Float(string='iva retenido')
    alicuota = fields.Char(string='alicuota')
    alicuota_type = fields.Char(string='alicuota type')
    state_retantion = fields.Char(string='state')
    state = fields.Char(string='state')
    currency_id = fields.Many2one('res.currency', 'Currency')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
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
    fecha_fact= fields.Datetime(string="Fecha Cierre")
    reg_maquina = fields.Char(string="Registro de Máquina Fiscal")
    nro_rep_z = fields.Char(string="Número Reporte Z")
    nro_doc = fields.Char(string="Nro de documentos")
    nro_doc_nc = fields.Char(string="Nro de nota credito")
    base_imponible_nc = fields.Float(string="Base Imponible NC")
    alicuota_nc =  fields.Float(string='Alicuota NC')
    total_nc= fields.Float(string="Total NC",default=0)
    fact_afectada = fields.Char()
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)


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


class libro_ventas(models.TransientModel):
    _name = "pos.wizard.libro.ventas" ## = nombre de la carpeta.nombre del archivo deparado con puntos

    facturas_ids = fields.Many2many('pos.order', string='Ordebes de Ventas', store=True) ##Relacion con el modelo de la vista de la creacion de facturas
   
    date_from = fields.Datetime(string='Date From', default=lambda *a:datetime.now().strftime('%Y-%m-%d 04:00:00'))
    date_to = fields.Datetime('Date To', default=lambda *a:(datetime.now() + timedelta(days=(1))).strftime('%Y-%m-%d 03:59:59'))
    #date_from = fields.Date(string='Date From', default=lambda *a:datetime.now().strftime('%Y-%m-%d'))
    #date_to = fields.Date('Date To', default=lambda *a:(datetime.now() + timedelta(days=(1))).strftime('%Y-%m-%d'))

    # fields for download xls
    state = fields.Selection([('choose', 'choose'), ('get', 'get')],default='choose') ##Genera los botones de exportar xls y pdf como tambien el de cancelar
    report = fields.Binary('Prepared file', filters='.xls', readonly=True)
    name = fields.Char('File Name', size=32)
    company_id = fields.Many2one('res.company','Company',default=lambda self: self.env.company.id)

    line  = fields.Many2many(comodel_name='pos.wizard.pdf.ventas', string='Lineas')


    def print_libro_pos(self):
        #pass
        self.get_invoice()
        #return self.env.ref('libro_ventas.libro_factura_clientes').report_action(self)
        return {'type': 'ir.actions.report','report_name': 'ext_extension_tpdv.reporte_ventas_pos','report_type':"qweb-pdf"}

    def get_invoice(self):
        t=self.env['pos.wizard.pdf.ventas']
        d=t.search([])
        d.unlink()
        cursor_resumen = self.env['pos.order.line.resumen'].search([
            ('fecha_fact','>=',self.date_from),
            ('fecha_fact','<=',self.date_to),
            ('company_id','=',self.env.company.id)
            ])
        #raise UserError(_('name:%s')%cursor_resumen)
        for det in cursor_resumen:
            values={
            'name':det.fecha_fact,
            #'tipo_doc': det.tipo_doc,
            'sale_total': self.conv_div_bs(det.total_con_iva,det),
            'base_imponible': self.conv_div_bs(det.total_base,det),
            'iva' : self.conv_div_bs(det.total_valor_iva,det),
            'total_exento':self.conv_div_bs(det.total_exento,det),
            'alicuota_reducida':self.conv_div_bs(det.alicuota_reducida,det),
            'alicuota_general':self.conv_div_bs(det.alicuota_general,det),
            'alicuota_adicional':self.conv_div_bs(det.alicuota_adicional,det),
            'base_adicional':self.conv_div_bs(det.base_adicional,det),
            'base_reducida':self.conv_div_bs(det.base_reducida,det),
            'base_general':self.conv_div_bs(det.base_general,det),
            'retenido_reducida':self.conv_div_bs(det.retenido_reducida,det),
            'retenido_adicional':self.conv_div_bs(det.retenido_adicional,det),
            'retenido_general':self.conv_div_bs(det.retenido_general,det),
            'fecha_fact':det.fecha_fact,
            'reg_maquina':det.reg_maquina,
            'nro_rep_z':det.nro_rep_z,
            'nro_doc':det.nro_doc,
            'nro_doc_nc':det.nro_doc_nc,
            'base_imponible_nc':self.conv_div_bs(det.base_imponible_nc,det),
            'alicuota_nc':self.conv_div_bs(det.alicuota_nc,det),
            'total_nc':self.conv_div_bs(det.total_nc,det),
            'fact_afectada':det.fact_afectada,
            }
            pdf_id = t.create(values)
        self.line = self.env['pos.wizard.pdf.ventas'].search([])

    def conv_div_bs(self,valor,det):
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
        ws1 = wb1.add_sheet('Ventas pos')
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
        ws1.write_merge(row,row, 0, 4, "Libro de Ventas", header_content_style)
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
        ws1.write_merge(row, row, 19, 25,"CONTRIBUYENTES",sub_header_style_c)
        ws1.write_merge(row, row, 26, 32,"NO CONTRIBUYENTES",sub_header_style_c)
        row += 1
        #CABECERA DE LA TABLA
        ws1.write(row,col+0,"#",sub_header_style_c)
        ws1.write(row,col+1,"Fecha Documento",sub_header_style_c)
        ws1.col(col+1).width = int((len('Fecha Documento')+3)*256)
        ws1.write(row,col+2,"RIF",sub_header_style_c)
        ws1.col(col+2).width = int((len('J-456987531')+2)*256)
        ws1.write(row,col+3,"Nombre Razon Social",sub_header_style_c)
        ws1.col(col+3).width = int(len('Nombre Razon Social')*256)
        ws1.write(row,col+4,"Numero de Planilla de exportacion",sub_header_style_c)
        ws1.col(col+4).width = int(len('Numero de Planilla de exportacion')*256)
        ws1.write(row,col+5,"Nro Factura / Entrega",sub_header_style_c)
        ws1.col(col+5).width = int(len('Nro. Factura / Entrega')*256)
        ws1.write(row,col+6,"Nro. de Maquina",sub_header_style_c)
        ws1.col(col+6).width = int(len('Nro. de Maquina')*256)
        ws1.write(row,col+7,"Nro Reporte Z",sub_header_style_c)
        ws1.col(col+7).width = int(len('Nro Reporte Z')*256)
        ws1.write(row,col+8,"Número nota de debito",sub_header_style_c)
        ws1.col(col+8).width = int(len('Número nota de debito')*256)
        ws1.write(row,col+9,"Numero de nota de credito ",sub_header_style_c)
        ws1.col(col+9).width = int(len('Numero de nota de credito')*256)
        ws1.write(row,col+10,"Base Imponible",sub_header_style_c)
        ws1.col(col+10).width = int(len('Base Imponible')*256)
        ws1.write(row,col+11,"Alicuota",sub_header_style_c)
        ws1.col(col+11).width = int(len('Alicuota')*256)
        ws1.write(row,col+12,"Impuesto IVA",sub_header_style_c)
        ws1.col(col+12).width = int(len('Impuesto IVA')*256)
        ws1.write(row,col+13,"Total",sub_header_style_c)
        ws1.col(col+13).width = int(len('Total')*256)
        ws1.write(row,col+14,"Nro Fact Afectada",sub_header_style_c)
        ws1.col(col+14).width = int(len('Nro Fact Afectada')*256)
        ws1.write(row,col+15,"Tipo de Transacc.",sub_header_style_c)
        ws1.col(col+15).width = int(len('Tipo de Transacc.')*256) 
        ws1.write(row,col+16,"Total Venta Incluyendo Iva",sub_header_style_c)
        ws1.col(col+16).width = int(len('Total Venta Incluyendo Iva')*256)
        ws1.write(row,col+17,"Valor FOB",sub_header_style_c)
        ws1.col(col+17).width = int(len('Valor FOB')*256)
        ws1.write(row,col+18,"Ventas Exentas o Exoneradas",sub_header_style_c)
        ws1.col(col+18).width = int(len('Ventas Exentas o Exoneradas')*256) 

        # CONTRIBUYENTES
        ws1.write(row,col+19,"Base Imponible",sub_header_style_c)
        ws1.col(col+19).width = int(len('Base Imponible')*256)
        ws1.write(row,col+20,"Alicuota Reducida",sub_header_style_c)
        ws1.col(col+20).width = int(len('Alicuota Reducida')*256)
        ws1.write(row,col+21,"Impuesto Iva",sub_header_style_c)
        ws1.col(col+21).width = int(len('Impuesto Iva')*256)
        ws1.write(row,col+22,"Alicuota General",sub_header_style_c)
        ws1.col(col+22).width = int(len('Alicuota General')*256)
        ws1.write(row,col+23,"Base Imponible",sub_header_style_c)
        ws1.col(col+23).width = int(len('Base Imponible')*256)
        ws1.write(row,col+24,"Alicuota General + Adicional",sub_header_style_c)
        ws1.col(col+24).width = int(len('Alicuota General + Adicional')*256)
        ws1.write(row,col+25,"Impuesto Iva",sub_header_style_c)
        ws1.col(col+25).width = int(len('Impuesto Iva')*256)
        # NO CONTRIBUYENTES
        ws1.write(row,col+26,"Base Imponible",sub_header_style_c)
        ws1.col(col+26).width = int(len('Base Imponible')*256)
        ws1.write(row,col+27,"Alicuota Reducida",sub_header_style_c)
        ws1.col(col+27).width = int(len('Alicuota Reducida')*256)
        ws1.write(row,col+28,"Impuesto Iva",sub_header_style_c)
        ws1.col(col+28).width = int(len('Impuesto Iva')*256)
        ws1.write(row,col+29,"Alicuota General",sub_header_style_c)
        ws1.col(col+29).width = int(len('Alicuota General')*256)
        ws1.write(row,col+30,"Base Imponible",sub_header_style_c)
        ws1.col(col+30).width = int(len('Base Imponible')*256)
        ws1.write(row,col+31,"Alicuota General + Adicional",sub_header_style_c)
        ws1.col(col+31).width = int(len('Alicuota General + Adicional')*256)
        ws1.write(row,col+32,"Impuesto Iva",sub_header_style_c)
        ws1.col(col+32).width = int(len('Impuesto Iva')*256)

        ws1.write(row,col+33,"Iva retenido (Comprador)",sub_header_style_c)
        ws1.col(col+33).width = int(len('Iva retenido (Comprador)')*256)
        ws1.write(row,col+34,"Nro Comprobante",sub_header_style_c)
        ws1.col(col+34).width = int(len('Nro Comprobante')*256)
        ws1.write(row,col+35,"Fecha Comp.",sub_header_style_c)
        ws1.col(col+35).width = int(len('Fecha Comp.')*256)

        center = xlwt.easyxf("align: horiz center")
        right = xlwt.easyxf("align: horiz right")

        numero = 1
        contador=0
        acum_venta_iva=0
        acum_exento=0
        acum_fob=0

        #### variables de contribiyentes
        acum_b_reducida=0
        acum_reducida=0
        acum_b_general=0                         
        acum_iva=0

        # ####variables no contribuyentes
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

        total_base_imponible_nc=0
        total_alicuota_nc=0
        total_total_nc=0

        for line in self.line.sorted(key=lambda x: (x.name ),reverse=False):
            contador=contador+1
            acum_base_general=acum_base_general+line.base_general
            acum_general=acum_general+line.alicuota_general
            acum_base_adicional=acum_base_adicional+line.base_adicional
            acum_base_reducida=acum_base_reducida+line.base_reducida
            acum_adicional=acum_adicional+line.alicuota_adicional
            row += 1
            ws1.write(row,col+0,str(numero),center)
            ws1.write(row,col+1,str(line.formato_fecha2(line.fecha_fact)),center)
            ws1.write(row,col+2,'RESUMEN',center)
            ws1.write(row,col+4,'RESUMEN DIIARIO DE VENTAS',center)
            ws1.write(row,col+5,str(line.nro_doc),center)
            ws1.write(row,col+6,str(line.reg_maquina),center)
            ws1.write(row,col+7,str(line.nro_rep_z),center)
            ws1.write(row,col+9,str(line.nro_doc_nc),center)
            ws1.write(row,col+10,str(round(line.base_imponible_nc,2)),center)
            total_base_imponible_nc=total_base_imponible_nc+line.base_imponible_nc
            ws1.write(row,col+11,'16%',center)
            ws1.write(row,col+12,str(round(line.alicuota_nc,2)),center)
            total_alicuota_nc=total_alicuota_nc+line.alicuota_nc
            ws1.write(row,col+13,str(round(line.total_nc,2)),center)
            total_total_nc=total_total_nc+line.total_nc
            ws1.write(row,col+14,str(line.fact_afectada),center)
            if line.total_nc==0:
                ws1.write(row,col+15,'01-Registro',center)
            if line.total_nc!=0:
                ws1.write(row,col+15,'03-NC',center)
            ws1.write(row,col+16,str(round(line.sale_total,2)),center)
            acum_venta_iva=acum_venta_iva+line.sale_total
            ws1.write(row,col+18,str(round(line.total_exento,2)),center)
            acum_exento=acum_exento+line.total_exento
            # campos de contribuyentes
            ws1.write(row,col+19,'0.0',center)
            ws1.write(row,col+21,'0.0',center)
            ws1.write(row,col+23,'0.0',center)
            ws1.write(row,col+25,'0.0',center)
            # CAMPOS NO CONTRIBUYENTES
            ws1.write(row,col+26,str(round(line.base_reducida,2)),center)
            acum_b_reducida=acum_b_reducida+(line.base_reducida)
            if line.base_reducida!=0:
                ws1.write(row,col+27,'8%',center)
            ws1.write(row,col+28,str(round(line.alicuota_reducida,2)),center)
            acum_reducida=acum_reducida+line.alicuota_reducida
            if line.base_general!=0:
                ws1.write(row,col+29,'16%',center)
            ws1.write(row,col+30,str(round(line.base_general+line.base_adicional,2)),center)
            acum_b_general=acum_b_general+(line.base_general+line.base_adicional)
            if line.base_adicional!=0:
                ws1.write(row,col+31,'31%',center)
            ws1.write(row,col+32,str(round(line.alicuota_general+line.alicuota_adicional,2)),center)
            acum_iva=acum_iva+(line.alicuota_general+line.alicuota_adicional)
            ws1.write(row,col+33,str(round(line.iva_retenido,2)),center)
            acum_iva_ret=acum_iva_ret+line.iva_retenido
            ws1.write(row,col+35,'---',center)


            numero=numero+1
        # ******* FILA DE TOTALES **********
        row=row+1
        ws1.write(row,col+9," TOTALES",sub_header_style)
        ws1.write(row,col+10,str(round(total_base_imponible_nc,2)),right)
        ws1.write(row,col+12,str(round(total_alicuota_nc,2)),right)
        ws1.write(row,col+13,str(round(total_total_nc,2)),center)
        ws1.col(col+13).width = int(len(str(total_total_nc))*256)
        ws1.write(row,col+16,str(round(acum_venta_iva,2)),center)
        ws1.write(row,col+17,str(round(acum_fob,2)),center)
        ws1.write(row,col+18,str(round(acum_exento,2)),center)
        ws1.write(row,col+19,str(round(acum_b_reducida2,2)),center)
        ws1.write(row,col+20,'---',center)
        ws1.write(row,col+21,str(round(acum_reducida2,2)),center)
        ws1.write(row,col+22,'---',center)
        ws1.write(row,col+23,str(round(acum_b_general2,2)),center)
        ws1.write(row,col+24,'---',center)
        ws1.write(row,col+25,str(round(acum_iva2,2)),center)
        ws1.write(row,col+26,str(round(acum_b_reducida,2)),center)
        ws1.write(row,col+27,'---',center)
        ws1.write(row,col+28,str(round(acum_reducida,2)),center)
        ws1.write(row,col+29,'---',center)
        ws1.write(row,col+30,str(round(acum_b_general,2)),center)
        ws1.write(row,col+31,'---',center)
        ws1.write(row,col+32,str(round(acum_iva,2)),center)
        ws1.write(row,col+33,str(round(acum_iva_ret,2)),center)

        # ******* RESUMEN DE VENTAS **********
        row=row+1
        ws1.write_merge(row, row, 20, 22,"RESUMEN DE VENTAS",sub_header_style_c)
        ws1.write_merge(row, row, 23, 24,"Base Imponible",sub_header_style_c)
        ws1.write_merge(row, row, 25, 26,"Débito Fiscal",sub_header_style_c)
        ws1.write_merge(row, row, 27, 29,"Iva Retenidos por Ventas",sub_header_style_c)

        # ************* fila exentas o exoneradas *********
        row=row+1
        ws1.write_merge(row, row, 20, 22,"Ventas internas Exentas o Exoneradas",right)
        ws1.write_merge(row, row, 23, 24,acum_exento,right)
        total_bases=total_bases+acum_exento
        ws1.write_merge(row, row, 25, 26,"0.00",right)
        ws1.write_merge(row, row, 27, 29,"0.00",right)

        # ************* fila SOLO ALICUOTA GENERAL *********
        row=row+1
        ws1.write_merge(row, row, 20, 22,"Ventas Internas Afectadas sólo Alícuota General",right)
        ws1.write_merge(row, row, 23, 24,round(acum_base_general+total_base_imponible_nc,2),right)
        total_bases=total_bases+acum_base_general+total_base_imponible_nc
        ws1.write_merge(row, row, 25, 26,round(acum_general+total_alicuota_nc,2),right)
        total_debitos=total_debitos+(acum_general+total_alicuota_nc)
        ws1.write_merge(row, row, 27, 29,round(acum_ret_general,2),right)
        total_retenidos=total_retenidos+acum_ret_general

        # ************* fila ALICUOTA GENERAL MAS ADICIONAL *********
        row=row+1
        ws1.write_merge(row, row, 20, 22,"Ventas Internas Afectadas sólo AlícuotaGeneral + Adicional",right)
        ws1.write_merge(row, row, 23, 24,acum_base_adicional,right)
        total_bases=total_bases+acum_base_adicional
        ws1.write_merge(row, row, 25, 26,acum_adicional,right)
        total_debitos=total_debitos+acum_adicional
        ws1.write_merge(row, row, 27, 29,acum_ret_adicional,right)
        total_retenidos=total_retenidos+acum_ret_adicional

        # ************* fila REDUCIDA *********
        row=row+1
        ws1.write_merge(row, row, 20, 22,"Ventas Internas Afectadas sólo Alícuota Reducida",right)
        ws1.write_merge(row, row, 23, 24,acum_base_reducida,right)
        total_bases=total_bases+acum_base_reducida
        ws1.write_merge(row, row, 25, 26,acum_reducida+acum_reducida2,right)
        total_debitos=total_debitos+(acum_reducida+acum_reducida2)
        ws1.write_merge(row, row, 27, 29,acum_ret_reducida,right)
        total_retenidos=total_retenidos+acum_ret_reducida

        # ************* fila EXPORTACION *********
        row=row+1
        ws1.write_merge(row, row, 20, 22,"Ventas de Exportación",right)
        ws1.write_merge(row, row, 23, 24,acum_fob,right)
        total_bases=total_bases+acum_fob
        ws1.write_merge(row, row, 25, 26,"0.00",right)
        ws1.write_merge(row, row, 27, 29,"0.00",right)

        # ************* fila totales*********
        row=row+1
        ws1.write_merge(row, row, 20, 22,"TOTAL:",right)
        ws1.write_merge(row, row, 23, 24,total_bases,right)
        ws1.write_merge(row, row, 25, 26,total_debitos,right)
        ws1.write_merge(row, row, 27, 29,total_retenidos,right)



        wb1.save(fp)
        out = base64.encodestring(fp.getvalue())
        fecha  = datetime.now().strftime('%d/%m/%Y') 
        self.write({'state': 'get', 'report': out, 'name':'TPDV pos_'+fecha+'.xls'})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'pos.wizard.libro.ventas',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }