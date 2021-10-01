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

class LibroComprasModelo(models.Model):
    _name = "account.wizard.pdf.compras" 

    name = fields.Char(string='Fecha')
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
    state = fields.Char(string='state')
    import_form_num = fields.Char(string='import_form_num')
    import_dossier = fields.Char(string='import_dossier')
    import_date = fields.Char(string='import_date')
    reversed_entry_id = fields.Many2one('account.move', string='Facturas', store=True)
    state_retantion = fields.Char(string='state')
    ref = fields.Char(string='ref')
    
    
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

    def doc_cedula(self,aux):
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
        resultado=str(tipo_doc)+str(nro_doc)
        return resultado
        #raise UserError(_('cedula: %s')%resultado)
        

class libro_compras(models.TransientModel):
    _name = "account.wizard.libro.compras"

    facturas_ids = fields.Many2many('account.move', string='Facturas', store=True)

    line_ids = fields.Many2many('account.move.line', string='Facturas_3', store=True)


    date_from = fields.Date(string='Date From', default=lambda *a:datetime.now().strftime('%Y-%m-%d'))
    date_to = fields.Date('Date To', default=lambda *a:(datetime.now() + timedelta(days=(1))).strftime('%Y-%m-%d'))

    # fields for download xls
    state = fields.Selection([('choose', 'choose'), ('get', 'get')],default='choose')
    report = fields.Binary('Prepared file', filters='.xls', readonly=True)
    name =  fields.Char('File Name', size=32)
    handler = fields.Char('Handler', compute='count_handler', default='0')
    company_id = fields.Many2one('res.company','Company',default=lambda self: self.env.user.company_id.id)

    line  = fields.Many2many(comodel_name='account.wizard.pdf.compras', string='Lineas')
    
    #CREATE TABLE public.vat_retention
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
        resultado=str(tipo_doc)+str(nro_doc)
        return resultado

    def get_invoice(self):
        self.facturas_ids = self.env['account.move'].search([
            ('invoice_date','>=',self.date_from),
            ('invoice_date','<=',self.date_to),
            ('state','in',('posted','cancel' )),
            ('type','in',('in_invoice','in_refund','in_receipt'))
            ],order="invoice_date asc")
        temp = self.env['account.wizard.pdf.compras'].search([])

        for t in temp:
            t.unlink()

        for factura in self.facturas_ids :
            for line in factura.alicuota_line_ids:
                self.env['account.wizard.pdf.compras'].create({
                    'name':factura.invoice_date,
                    'document': factura.partner_id.doc_type + factura.partner_id.vat if factura.partner_id.doc_type else '' ,
                    'partner':factura.partner_id.id,
                    'invoice_number': factura.invoice_number,#darrell
                    'tipo_doc': factura.journal_id.tipo_doc,
                    'invoice_ctrl_number': factura.invoice_ctrl_number,
                    'sale_total': (line.total_base+line.total_valor_iva),
                    'base_imponible': line.total_base,
                    'iva' : line.total_valor_iva,
                    'state_retantion': factura.vat_ret_id.state,
                    'iva_retenido': line.total_ret_iva,
                    'retenido': factura.vat_ret_id.name,
                    'retenido_date':factura.vat_ret_id.voucher_delivery_date,
                    'alicuota': line.tax_id.description,
                    'alicuota_type':  line.tax_id.aliquot,
                    'state': factura.state,
                    'reversed_entry_id':factura.id,
                    'import_form_num':factura.import_form_num,
                    'import_dossier':factura.import_dossier,
                    'import_date': factura.import_date,
                    'ref':factura.ref,
                        })
        self.line = self.env['account.wizard.pdf.compras'].search([],order="name,retenido  desc")
        pass
    def print_facturas(self):
        self.get_invoice()
        return {'type': 'ir.actions.report','report_name': 'libro_compras.libro_factura_proveedores','report_type':"qweb-pdf"}




    @api.depends('company_id')
    def generate_xls_report(self):
    
        self.ensure_one()
        self.get_invoice()

        wb1 = xlwt.Workbook(encoding='utf-8')
        ws1 = wb1.add_sheet('Invoices Details')
        fp = BytesIO()

        #Content/Text style
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
        ws1.write_merge(row, row, 2, 4,  str(self.company_id.partner_id.doc_type.upper()) +'-'+ str(self.company_id.partner_id.vat), sub_header_content_style)
        row+=1
        ws1.write_merge(row, row, 0, 1, "Direccion Fiscal:", sub_header_style)
        ws1.write_merge(row, row, 2, 5, str(self.get_company_address()), sub_header_content_style)
        row +=1
        ws1.write(row, col+0, "Desde :", sub_header_style)
        # ws1.write(row, col+2, datetime.strftime(datetime.strptime(self.date_from,DEFAULT_SERVER_DATE_FORMAT),"%d/%m/%Y"), sub_header_content_style)
        fec_desde = self.line.formato_fecha2(self.date_from)
        ws1.write(row, col+1, fec_desde, sub_header_content_style)
        row += 1
        ws1.write(row, col+0, "Hasta :", sub_header_style)
        # ws1.write(row, col+2, datetime.strftime(datetime.strptime(self.date_to,DEFAULT_SERVER_DATE_FORMAT),"%d/%m/%Y"), sub_header_content_style)
        fec_hasta = self.line.formato_fecha2(self.date_to)
        ws1.write(row, col+1, fec_hasta, sub_header_content_style)
        row += 2
        ws1.write_merge(row, row, 10, 12, "Compras Internas o Exportacion Gravada", sub_header_style)
        ws1.write_merge(row, row, 15, 16, "Compras Internas / Importaciones", sub_header_style)
        ws1.col(col+15).width = int(len('Compras Internas ')*256)
        ws1.col(col+16).width = int(len('/ Importaciones')*256)
        row += 1
        ws1.write(row,col+0,"#",sub_header_style_c)
        ws1.col(col+0).width = int((len('Desde :')+1)*256)
        ws1.write(row,col+1,"Fecha Documento",sub_header_style_c)
        ws1.col(col+1).width = int((len('Fecha Documento')+3)*256)
        ws1.write(row,col+2,"RIF",sub_header_style_c)
        ws1.col(col+2).width = int((len('J-456987531'))*256)
        ws1.write(row,col+3,"Nombre Razon Social",sub_header_style_c)
        ws1.col(col+3).width = int(len('Nombre Razon Social')*256)
        ws1.write(row,col+4,"Tipo de Persona",sub_header_style_c)
        ws1.col(col+4).width = int(len('Tipo de Persona')*256)
        ws1.write(row,col+5,"Nro. Factura / Entrega",sub_header_style_c)
        ws1.col(col+5).width = int(len('Nro. Factura / Entrega')*256)
        ws1.write(row,col+6,"Nro de control",sub_header_style_c)
        ws1.col(col+6).width = int(len('Nro de control')*256)
        ws1.write(row,col+7,"Nro de nota de debito",sub_header_style_c)
        ws1.col(col+7).width = int(len('Nro de nota de debito')*256)
        ws1.write(row,col+8,"Nro de nota de credito",sub_header_style_c)
        ws1.col(col+8).width = int(len('Nro de nota de credito')*256)
        ws1.write(row,col+9,"Nro de factura afectada",sub_header_style_c)
        ws1.col(col+9).width = int(len('Nro de factura afectada')*256)
        ws1.write(row,col+10,"Tipo de transacc.",sub_header_style_c)
        ws1.col(col+10).width = int(len('Tipo de transacc.')*256)
        ws1.write(row,col+11,"Nro Planilla de Importaciones",sub_header_style_c)
        ws1.col(col+11).width = int(len('Nro Planilla de Importaciones')*256)
        ws1.write(row,col+12,"Nro Expediente Importaciones",sub_header_style_c)
        ws1.col(col+12).width = int(len('Nro Expediente Importaciones')*256)
        ws1.write(row,col+13,"Fecha de importaciones",sub_header_style_c)
        ws1.col(col+13).width = int(len('Fecha de importaciones')*256)
        ws1.write(row,col+14,"Total compras con IVA",sub_header_style_c)
        ws1.col(col+14).width = int(len('Total compras con IVA')*256)
        ws1.write(row,col+15,"Exentas",sub_header_style_c)
        ws1.write(row,col+16,"Exoneradas",sub_header_style_c)
        ws1.write(row,col+17,"Base Imponible",sub_header_style_c)
        ws1.col(col+17).width = int(len('Base Imponible')*256)
        ws1.write(row,col+18,"'%'Alic",sub_header_style_c)
        ws1.col(col+18).width = int(len('IVA (00.0%) compras')*256)
        ws1.write(row,col+19,"Impuesto IVA",sub_header_style_c)
        ws1.col(col+19).width = int((len('Impuesto IVA')+2)*256)
        ws1.write(row,col+20,"IVA Retenido (Vendedor)",sub_header_style_c)
        ws1.col(col+20).width = int(len('IVA Retenido (Vendedor)')*256)
        ws1.write(row,col+21,"Nro. Comprobante de retencion",sub_header_style_c)
        ws1.col(col+21).width = int(len('Nro. Comprobante de retencion')*256)
        ws1.write(row,col+22,"Fecha comp.",sub_header_style_c)
        ws1.col(col+22).width = int(len('Fecha comp.')*256)
        #Searching for customer invoices
        invoices = self.env['account.move'].search([('date','>=',self.date_from),('date','<=', self.date_to),('type','!=','out_invoice'),('type','!=','out_refund'),('state','!=','draft'),('state','!=','cancel')], order = 'date ASC') # order sirve para ordenar de manera ascendente o descendete los valores de una variable  (ASC o DEC))
        #invoices.sorted(key=lambda r: r.date_invoice, reverse=False)

        #tax_exentos = self.env['account.move.tax'].search([])
        #ids_line_taxs = self.env['account.move.line.tax'].search([])
        #ids_lines = self.env['account.move.line'].search([])

        all_inv_total = 0
        num = 0
        total_internas = 0
        total_iva = 0
        total_imponible = 0
        total_con_IVA = 0
        reten_iva_total = 0
        alicuota = 0
        alicuota_reten = 0
        alicuota_porcent = ''
        alicuota_porcent_reten = ''
        tax_general = 0
        tax_reducido = 0
        base_general = 0
        base_reducido = 0
        cont_execto = 0

        #Nuevas variables
        tot_exentas = 0
        tot_exoneradas = 0
        base_genel_mas_adicional = 0
        tax_genel_mas_adicional = 0
        ret_general = 0
        ret_reducido = 0
        ret_genel_mas_adicional =0
        numero = 1
        lines= self.line #.sorted(key=lambda x: (x.name,x.retenido ),reverse=False)
        for invoice in lines:
            row += 1

            center = xlwt.easyxf("align: horiz center")
            right = xlwt.easyxf("align: horiz right")

            ws1.write(row,col+0,str(numero),center)
            ws1.write(row,col+1,str(invoice.formato_fecha2(invoice.name)),center)
            ws1.write(row,col+2,str(invoice.document.upper()),center)
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
            
            if invoice.tipo_doc == 'fc':
                ws1.write(row,col+5,str(invoice.invoice_number),center)
            else :
                ws1.write(row,col+5,'')
            ws1.write(row,col+6,str(invoice.invoice_ctrl_number),center)

            if invoice.tipo_doc == 'nb':
                ws1.write(row,col+7,str(invoice.invoice_number),center)
            else :
                ws1.write(row,col+7,'')
            
            if invoice.tipo_doc == 'nc':
                ws1.write(row,col+8,str(invoice.invoice_number),center)
            else :
                ws1.write(row,col+8,'')

            if invoice.tipo_doc == 'nc' or invoice.tipo_doc == 'nb' :
                    ws1.write(row,col+9,str(invoice.ref),center)
            else :
                ws1.write(row,col+9,'')
            
            if invoice.tipo_doc == 'nb':
                ws1.write(row,col+10,'02-Reg',center)
            elif invoice.tipo_doc == 'nc' :
                ws1.write(row,col+10,'03-Reg',center)
            else :
                ws1.write(row,col+10,'01-Reg',center)
            
            import_form_num = str(invoice.import_form_num) if invoice.import_form_num else ""
            ws1.write(row,col+11,import_form_num,center)

            import_dossier = str(invoice.import_dossier) if invoice.import_dossier else ""
            ws1.write(row,col+12,import_dossier,center)
            
            import_date = str(invoice.import_date) if invoice.import_date else ""
            ws1.write(row,col+13,import_date,center)
            sale_total = str(invoice.float_format(invoice.sale_total)) if invoice.sale_total else ""
            
            if invoice.alicuota_type == 'exempt':
                if invoice.tipo_doc == 'nc':
                    ws1.write(row,col+15,'-' + str(invoice.float_format(invoice.sale_total)),right)
                    tot_exentas -= float(invoice.sale_total)
                    ws1.write(row,col+14,'-' + sale_total,right)
                    total_con_IVA -= float(invoice.sale_total)
                else:
                    ws1.write(row,col+15,str(invoice.float_format(invoice.sale_total)),right)
                    tot_exentas += float(invoice.sale_total)
                    ws1.write(row,col+14,sale_total,right)
                    total_con_IVA += float(invoice.sale_total)
            elif invoice.alicuota_type == 'no_tax_credit':
                if invoice.tipo_doc == 'nc':
                    ws1.write(row,col+16,'-' + str(invoice.float_format(invoice.sale_total)),right)
                    tot_exoneradas -= float(invoice.sale_total)
                    ws1.write(row,col+14,'-' + sale_total,right)
                    total_con_IVA -= float(invoice.sale_total)

                else:
                    ws1.write(row,col+16,str(invoice.float_format(invoice.sale_total)),right)
                    tot_exoneradas += float(invoice.sale_total)
                    ws1.write(row,col+14,sale_total,right)
                    total_con_IVA += float(invoice.sale_total)
            else :
                
                if invoice.tipo_doc == 'nc':
                    ws1.write(row,col+14,'-' + sale_total,right)
                    total_con_IVA -= float(invoice.sale_total)
                else:
                    ws1.write(row,col+14,sale_total,right)
                    total_con_IVA += float(invoice.sale_total) 


            if invoice.alicuota_type == 'exempt' or invoice.alicuota_type == 'no_tax_credit':
                pass
            else:
                if invoice.tipo_doc == 'nc':
                    ws1.write(row,col+17,'-' + str(invoice.float_format(invoice.base_imponible)),right)
                    total_imponible -= float(invoice.base_imponible)
                else:
                    ws1.write(row,col+17,str(invoice.float_format(invoice.base_imponible)),right)
                    total_imponible += float(invoice.base_imponible)

            is_alicuota = str(invoice.alicuota) if invoice.alicuota else ""
            ws1.write(row,col+18,str(is_alicuota),right)

            if invoice.tipo_doc == 'nc':
                ws1.write(row,col+19,'-' + str(invoice.float_format(invoice.iva)),right)
                total_iva -= float(invoice.iva)
            else:
                ws1.write(row,col+19,str(invoice.float_format(invoice.iva)),right)
                total_iva += float(invoice.iva)

            if invoice.alicuota_type == 'exempt' or invoice.alicuota_type == 'no_tax_credit':
                ws1.write(row,col+20,0,right)
            else:
                if invoice.tipo_doc == 'nc':
                    ws1.write(row,col+20,'-' + str(invoice.float_format(invoice.iva_retenido)),right)
                    if invoice.state_retantion == 'posted':
                        reten_iva_total -= float(invoice.iva_retenido)
                else:
                    ws1.write(row,col+20,str(invoice.float_format(invoice.iva_retenido)),right)
                    if invoice.state_retantion == 'posted':
                        reten_iva_total += float(invoice.iva_retenido)

            retenido = str(invoice.retenido) if invoice.retenido else ""
            ws1.write(row,col+21,retenido,center)

            retenido_date = str(invoice.formato_fecha2(invoice.retenido_date)) if invoice.retenido_date else ""
            ws1.write(row,col+22,retenido_date,center)

            numero += 1

        row +=1

        ws1.write(row,col+13,"TOTALES:",sub_header_style_c)
        ws1.write(row,col+14,invoice.float_format(total_con_IVA),sub_header_style_r)
        ws1.write(row,col+15,invoice.float_format(tot_exentas),sub_header_style_r)
        ws1.write(row,col+16,invoice.float_format(tot_exoneradas),sub_header_style_r)
        ws1.write(row,col+17,invoice.float_format(total_imponible),sub_header_style_r)
        #ws1.write(row,col+19,'0',sub_header_style_r)
        ws1.write(row,col+19,invoice.float_format(total_iva),sub_header_style_r)
        ws1.write(row,col+20,invoice.float_format(reten_iva_total),sub_header_style_r)

        tot_base_exentas = 0
        tot_iva_exentas = 0
        tot_reten_exent = 0

        tot_base_no_gra = 0
        tot_iva_no_gra = 0
        tot_reten_no_gra = 0

        for l in self.line:
            if l.alicuota_type == 'general' and l.import_form_num == False:
                if l.tipo_doc == 'nc':
                    base_general -= float(l.base_imponible)
                    tax_general -= float(l.iva)
                    if l.state_retantion == 'posted':
                        ret_general -= float(l.iva_retenido)
                else:
                    base_general += float(l.base_imponible)
                    tax_general += float(l.iva)
                    if l.state_retantion == 'posted':
                        ret_general += float(l.iva_retenido)
        
        for l in self.line:
            if l.alicuota_type == 'additional' and l.import_form_num == False:
                if l.tipo_doc == 'nc':
                    base_genel_mas_adicional -= float(l.base_imponible)
                    tax_genel_mas_adicional -= float(l.iva)
                    if l.state_retantion == 'posted':
                        ret_genel_mas_adicional -= float(l.iva_retenido)
                else:
                    base_genel_mas_adicional += float(l.base_imponible)
                    tax_genel_mas_adicional += float(l.iva)
                    if l.state_retantion == 'posted':
                        ret_genel_mas_adicional += float(l.iva_retenido)
        
        for l in self.line:
            if l.alicuota_type == 'reduced' and l.import_form_num == False :
                if l.tipo_doc == 'nc':
                    base_reducido -= float(l.base_imponible)
                    tax_reducido -= float(l.iva)
                    if l.state_retantion == 'posted':
                        ret_reducido -= float(l.iva_retenido)
                else:
                    base_reducido += float(l.base_imponible)
                    tax_reducido += float(l.iva)
                    if l.state_retantion == 'posted':
                        ret_reducido += float(l.iva_retenido)
        
        for l in self.line:
            if l.alicuota_type == 'exempt' and l.import_form_num == False:
                if l.tipo_doc == 'nc':
                    tot_base_exentas -= float(l.base_imponible)
                    tot_iva_exentas -= float(l.iva)
                    if l.state_retantion == 'posted':
                        tot_reten_exent -= 0
                else:
                    tot_base_exentas += float(l.base_imponible)
                    tot_iva_exentas += float(l.iva)
                    if l.state_retantion == 'posted':
                        tot_reten_exent += 0

        for l in self.line:
            if l.alicuota_type == 'no_tax_credit' and l.import_form_num == False:
                if l.tipo_doc == 'nc':
                    tot_base_no_gra -= float(l.base_imponible)
                    tot_iva_no_gra -= float(l.iva)
                    if l.state_retantion == 'posted':
                        tot_reten_no_gra -= 0
                else:
                    tot_base_no_gra += float(l.base_imponible)
                    tot_iva_no_gra += float(l.iva)
                    if l.state_retantion == 'posted':
                        tot_reten_no_gra += 0
        total_impo = 0
        total_iva_impo = 0
        tot_reten_impo = 0 
        for l in self.line:
            

            if l.import_form_num :
                if l.tipo_doc == 'nc':
                    total_impo -= float(l.base_imponible)
                    total_iva_impo -= float(l.iva)
                    if l.state_retantion == 'posted':
                        tot_reten_impo -= float(l.iva_retenido)
                else:
                    total_impo += float(l.base_imponible)
                    total_iva_impo += float(l.iva)
                    if l.state_retantion == 'posted':
                        tot_reten_impo += float(l.iva_retenido)

        row +=2
        result_right = xlwt.easyxf('font: name Helvetica, height 170; align: horiz right;')
        ws1.write_merge(row, row, 12, 16,"Resumen de Compras",sub_header_style_c)
        ws1.write(row,col+17,"Base Imponible",sub_header_style_c)
        ws1.write(row,col+18,"Credito Fiscal",sub_header_style_c)
        ws1.write_merge(row, row, 19, 20,"IVA retenido por Vendedor.",sub_header_style_c)
        row+=1

        ws1.write_merge(row, row, 12, 16,"Compras de Importaciones",sub_header_style)
        ws1.write(row, col + 17, invoice.float_format(total_impo), result_right)
        ws1.write(row, col + 18, invoice.float_format(total_iva_impo), result_right)
        ws1.write(row, col + 19, invoice.float_format(tot_reten_impo), result_right)

        row+=1

        
        ws1.write_merge(row, row, 12, 16,"Compras Internas Afectadas sólo Alícuota General",sub_header_style)
        ws1.write(row, col + 17, invoice.float_format(base_general), result_right)
        ws1.write(row, col + 18, invoice.float_format(tax_general), result_right)
        ws1.write(row, col + 19, invoice.float_format(ret_general), result_right)
        row+=1
        ws1.write_merge(row, row, 12, 16,"Compras Internas Afectadas sólo Alícuota General + Adicional",sub_header_style)
        ws1.write(row, col + 17, invoice.float_format(base_genel_mas_adicional), result_right)
        ws1.write(row, col + 18, invoice.float_format(tax_genel_mas_adicional), result_right)
        ws1.write(row, col + 19, invoice.float_format(ret_genel_mas_adicional), result_right)
        row+=1
        ws1.write_merge(row, row, 12, 16,"Compras Internas Afectadas sólo Alícuota Reducida",sub_header_style)
        ws1.write(row, col + 17, invoice.float_format(base_reducido), result_right)
        ws1.write(row, col + 18, invoice.float_format(tax_reducido), result_right)
        ws1.write(row, col + 19, invoice.float_format(ret_reducido), result_right)
        row+=1
        ws1.write_merge(row, row, 12, 16,"Compras internas Exentas o Exoneradas",sub_header_style)
        ws1.write(row, col + 17, invoice.float_format(tot_base_exentas), result_right)
        ws1.write(row, col + 18, invoice.float_format(tot_iva_exentas), result_right)
        ws1.write(row, col + 19, invoice.float_format(tot_reten_exent), result_right)
        row+=1
        ws1.write_merge(row, row, 12, 16,"Compras Internas No Gravadas",sub_header_style)
        ws1.write(row, col + 17, invoice.float_format(tot_base_no_gra), result_right)
        ws1.write(row, col + 18, invoice.float_format(tot_iva_no_gra), result_right)
        ws1.write(row, col + 19, invoice.float_format(tot_reten_no_gra), result_right)
        row+=1
        ws1.write_merge(row, row, 12, 16,"Total",sub_header_style)
        ws1.write(row, col + 17,invoice.float_format((base_general+base_genel_mas_adicional+base_reducido+tot_base_exentas+tot_base_no_gra+total_impo)), result_right)
        ws1.write(row, col + 18,invoice.float_format((tax_general+tax_genel_mas_adicional+tax_reducido+tot_iva_exentas+tot_iva_no_gra+total_iva_impo)), result_right)
        ws1.write(row, col + 19,invoice.float_format((ret_general+ret_genel_mas_adicional+ret_reducido+tot_reten_exent+tot_reten_no_gra+tot_reten_impo)), result_right)

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
