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
    _name = "account.wizard.pdf.ventas" 

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

class libro_ventas(models.TransientModel):
    _name = "account.wizard.libro.ventas" ## = nombre de la carpeta.nombre del archivo deparado con puntos

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

    line  = fields.Many2many(comodel_name='account.wizard.pdf.ventas', string='Lineas')
    
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
            ('type','in',('out_invoice','out_refund','out_receipt'))
            ])
        temp = self.env['account.wizard.pdf.ventas'].search([])

        for t in temp:
            t.unlink()
        for factura in self.facturas_ids :
            for line in factura.alicuota_line_ids:
                self.env['account.wizard.pdf.ventas'].create({
                    'name':factura.invoice_date,
                    'document': factura.partner_id.doc_type + factura.partner_id.vat if factura.partner_id.doc_type else '' ,
                    'partner':factura.partner_id.id,
                    'invoice_number': factura.invoice_number,#darrell
                    'tipo_doc': factura.journal_id.tipo_doc,
                    #'tipo_doc': line.tipo_doc,
                    'invoice_ctrl_number': factura.invoice_ctrl_number,
                    'sale_total': (line.total_base+line.total_valor_iva),
                    'base_imponible': line.total_base,
                    'iva' : line.total_valor_iva,
                    'iva_retenido': line.total_ret_iva,
                    'retenido': factura.vat_ret_id.name,
                    'state_retantion': factura.vat_ret_id.state,
                    'retenido_date':factura.vat_ret_id.voucher_delivery_date,
                    'alicuota':line.tax_id.description,
                    'alicuota_type': line.tax_id.aliquot,
                    'state': factura.state,
                    'reversed_entry_id':factura.reversed_entry_id.id,
                    'currency_id':factura.currency_id.id,
                    'ref':factura.ref,
                })
        self.line = self.env['account.wizard.pdf.ventas'].search([])


    def print_facturas(self):
        self.get_invoice()
        return self.env.ref('libro_ventas.libro_factura_clientes').report_action(self)




    def cont_row(self):
        row = 0
        for record in self.facturas_ids:
            row +=1
        return row

    def float_format(self,valor):
        if valor:
            result = '{:,.2f}'.format(valor)
            result = result.replace(',','*')
            result = result.replace('.',',')
            result = result.replace('*','.')
        return result

    @api.depends('company_id')
    def generate_xls_report(self):
        self.get_invoice()
        self.ensure_one()

        wb1 = xlwt.Workbook(encoding='utf-8')
        ws1 = wb1.add_sheet('Ventas')
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
        ws1.write_merge(row, row, 12, 14,"Ventas Internas o Exportacion Gravadas",sub_header_style)
        row += 1
        ws1.write(row,col+0,"#",sub_header_style_c)
        ws1.col(col+0).width = int((len('Desde :')+1)*256)
        ws1.write(row,col+1,"Fecha Documento",sub_header_style_c)
        ws1.col(col+1).width = int((len('Fecha Documento')+3)*256)
        ws1.write(row,col+2,"RIF",sub_header_style_c)
        ws1.col(col+2).width = int((len('J-456987531')+2)*256)
        ws1.write(row,col+3,"Nombre Razon Social",sub_header_style_c)
        ws1.col(col+3).width = int(len('Nombre Razon Social')*256)
        ws1.write(row,col+4,"Tipo de Persona",sub_header_style_c)
        ws1.col(col+4).width = int(len('Tipo de Persona')*256)
        ws1.write(row,col+5,"Numero de Planilla de exportacion",sub_header_style_c)
        ws1.col(col+5).width = int(len('Numero de Planilla de exportacion')*256)
        ws1.write(row,col+6,"Nro Factura / Entrega",sub_header_style_c)
        ws1.col(col+6).width = int(len('Nro. Factura / Entrega')*256)
        ws1.write(row,col+7,"Nro de Control",sub_header_style_c)
        ws1.col(col+7).width = int(len('Nro de control')*256)
        ws1.write(row,col+8,"Nro de nota de debito",sub_header_style_c)
        ws1.col(col+8).width = int(len('Nro de nota de debito')*256)
        ws1.write(row,col+9,"Numero de nota de credito ",sub_header_style_c)
        ws1.col(col+9).width = int(len('Numero de nota de credito')*256)
        ws1.write(row,col+10,"Nro Factura Afectada",sub_header_style_c)
        ws1.col(col+10).width = int(len('Nro de factura afectada')*256)
        ws1.write(row,col+11,"Tipo de transacc.",sub_header_style_c)
        ws1.col(col+11).width = int(len('Tipo de transacc.')*256)
        ws1.write(row,col+12,"Ventas Incluyendo el IVA",sub_header_style_c)
        ws1.col(col+12).width = int(len('Ventas Incluyendo el IVA')*256)
        ws1.write(row,col+13,"Ventas internas o exoneraciones no gravadas",sub_header_style_c)
        ws1.col(col+13).width = int(len('Ventas internas o exoneraciones no gravadas')*256)
        ws1.write(row,col+14,"Ventas internas o exportaciones exentas o exoneradas",sub_header_style_c)
        ws1.col(col+14).width = int(len('Ventas internas o exportaciones exentas o exoneradas')*256)
        ws1.write(row,col+15,"Base Imponible",sub_header_style_c)
        ws1.col(col+15).width = int(len('Base Imponible')*256)
        ws1.write(row,col+16,"'%'Alicuota",sub_header_style_c)
        ws1.col(col+16).width = int((len('IVA (00.0%) ventas')+1)*256)
        ws1.write(row,col+17,"Impuesto IVA",sub_header_style_c)
        ws1.col(col+17).width = int((len('Impuesto IVA')+2)*256)
        ws1.write(row,col+18,"IVA Retenido Comprador",sub_header_style_c)
        ws1.col(col+18).width = int(len('IVA Retenido Comprador')*256)
        ws1.write(row,col+19,"Nro. Comprobante de Retencion",sub_header_style_c)
        ws1.col(col+19).width = int(len('Nro. Comprobante de retencion')*256)
        ws1.write(row,col+20,"Fecha comp",sub_header_style_c)
        ws1.col(col+20).width = int((len('Fecha comp')+1)*256)


        #Searching for customer invoices
        self.invoices = self.env['account.move'].search([('invoice_date','>=',self.date_from),('invoice_date','<=', self.date_to),('type','!=','in_invoice'),('type','!=','in_refund'),('state','!=','draft'),('state', '!=', 'cancel')], order = 'invoice_date ASC')
        _logger.info("\n\n\n {} \n\n\n".format(self.invoices))


        all_inv_total = 0
        num2 = 0
        total_internas = 0
        total_iva = 0
        total_imponible = 0
        total_con_iva = 0
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
        t_retenido=0

        # Nuevas variables
        tot_exentas = 0
        base_genel_mas_adicional = 0
        tax_genel_mas_adicional = 0
        ret_general = 0
        ret_reducido = 0
        ret_genel_mas_adicional = 0


        for invoice in self.invoices:
            num2 += 1

            ## traer datos del iva para saber el orden de cada producto de las factura con su montos
            exent_p_fac = 0
            post_exectas = 0

            base_16 = 0
            tax_16 = 0
            tot_comp_p_iva_16 = 0  # base + iva
            ret_16 = 0
            cont_16 = 0

            base_8 = 0
            tax_8 = 0
            tot_comp_p_iva_8 = 0  # base + iva
            ret_8 = 0
            cont_8 = 0

            base_31 = 0
            tax_31 = 0
            tot_comp_p_iva_31 = 0  # base + iva
            ret_31 = 0
            cont_31 = 0

        numero = 1
        total_con_iva = 0
        tot_no_gra = 0
        tot_exentas = 0
        total_bi = 0
        total_iva = 0
        total_iva_reten = 0
        lines= self.line.sorted(key=lambda x: (x.name,x.invoice_ctrl_number ),reverse=False)
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
            
            ws1.write(row,col+5,' ',center)
            
            if invoice.tipo_doc == 'fc':
                ws1.write(row,col+6,str(invoice.invoice_number),center)
            else :
                ws1.write(row,col+6,'')
            
            ws1.write(row,col+7,str(invoice.invoice_ctrl_number),center)

            if invoice.tipo_doc == 'nb':
                ws1.write(row,col+8,str(invoice.invoice_number),center)
            else :
                ws1.write(row,col+8,'')
            
            if invoice.tipo_doc == 'nc':
                ws1.write(row,col+9,str(invoice.invoice_number),center)
            else :
                ws1.write(row,col+9,'')
            
            if invoice.tipo_doc == 'nc' or invoice.tipo_doc == 'nb' :
                    ws1.write(row,col+10,str(invoice.ref),center)
            else :
                ws1.write(row,col+10,'')
            
            if invoice.tipo_doc == 'nb':
                ws1.write(row,col+11,'02-Reg',center)
            elif invoice.tipo_doc == 'nc' :
                ws1.write(row,col+11,'03-Reg',center)
            else :
                ws1.write(row,col+11,'01-Reg',center)
                
            sale_total = str(invoice.float_format(invoice.sale_total)) if invoice.sale_total else ""
            if invoice.alicuota_type == 'exempt':
                if invoice.tipo_doc == 'nc':
                    ws1.write(row,col+14,'-' + str(invoice.float_format(invoice.sale_total)),right)
                    tot_exentas -= float(invoice.sale_total)
                    ws1.write(row,col+12,'-' + sale_total,right)
                    total_con_iva -= float(invoice.sale_total)
                    
                else:
                    ws1.write(row,col+14,str(invoice.float_format(invoice.sale_total)),right)
                    tot_exentas += float(invoice.sale_total)
                    ws1.write(row,col+12,sale_total,right)
                    total_con_iva += float(invoice.sale_total)
                    
            elif invoice.alicuota_type == 'no_tax_credit':
                if invoice.tipo_doc == 'nc':
                    ws1.write(row,col+13,'-' + str(invoice.float_format(invoice.sale_total)),right)
                    tot_no_gra -= float(invoice.sale_total)
                    ws1.write(row,col+12,'-' + sale_total,right)
                    total_con_iva -= float(invoice.sale_total)
                else:
                    ws1.write(row,col+13,str(invoice.float_format(invoice.sale_total)),right)
                    tot_no_gra += float(invoice.sale_total)
                    ws1.write(row,col+12,sale_total,right)
                    total_con_iva += float(invoice.sale_total)
            else :
                if invoice.tipo_doc == 'nc':
                    ws1.write(row,col+12,'-' + sale_total,right)
                    total_con_iva -= float(invoice.sale_total)
                else:
                    ws1.write(row,col+12,sale_total,right)
                    total_con_iva += float(invoice.sale_total)
            if invoice.alicuota_type == 'exempt' or invoice.alicuota_type == 'no_tax_credit' :
                pass
            else :
                if invoice.tipo_doc == 'nc':
                    ws1.write(row,col+15,'-' + str(invoice.float_format(invoice.base_imponible)),right)
                    total_bi -= float(invoice.base_imponible)
                else:
                    ws1.write(row,col+15,str(invoice.float_format(invoice.base_imponible)),right)
                    total_bi += float(invoice.base_imponible)

            is_alicuota = str(invoice.alicuota) if invoice.alicuota else ""
            ws1.write(row,col+16,str(is_alicuota),right)

            if invoice.tipo_doc == 'nc':
                ws1.write(row,col+17,'-' + str(invoice.float_format(invoice.iva)),right)
                total_iva -= float(invoice.iva)
            else:
                ws1.write(row,col+17,str(invoice.float_format(invoice.iva)),right)
                total_iva += float(invoice.iva)

            if invoice.alicuota_type == 'exempt' or invoice.alicuota_type == 'no_tax_credit':
                ws1.write(row,col+18,0,right)
            else:
                if invoice.tipo_doc == 'nc':
                    ws1.write(row,col+18,'-' + str(invoice.float_format(invoice.iva_retenido)),right)
                    if invoice.state_retantion == 'posted':
                        total_iva_reten -= float(invoice.iva_retenido)
                else:
                    ws1.write(row,col+18,str(invoice.float_format(invoice.iva_retenido)),right)
                    if invoice.state_retantion == 'posted':
                        total_iva_reten += float(invoice.iva_retenido)
            
            retenido = str(invoice.retenido) if invoice.retenido else ""
            ws1.write(row,col+19,retenido,center)

            retenido_date = str(invoice.formato_fecha2(invoice.retenido_date)) if invoice.retenido_date else ""
            ws1.write(row,col+20,retenido_date,center)

            numero += 1
                

            # ==================== Fin de calculos =====================================================================

            cont_impri = cont_8 + cont_16 + cont_31 + post_exectas

            # ==========================================================================================================

            for p in range(cont_impri):

                ws1.write(row, col + 1, num2, line_content_style)  # contador

               # Fecha del documento
                fech_doc = datetime.strftime(datetime.strptime(invoice.invoice_date, DEFAULT_SERVER_DATE_FORMAT), "%d/%m/%Y")

                ws1.write(row, col + 2, fech_doc, line_content_style)  # fecha de documento
                ws1.write(row, col + 3, invoice.vat, line_content_style)  # rif
                ws1.write(row, col + 4, invoice.partner_id.name, line_content_style)  # Nombre Razon social
                ws1.write(row, col + 5, "", line_content_style)  # numero de planilla de exportacion

                if (invoice.origin == 0):
                    ws1.write(row, col+6, invoice.move_id.name, line_content_style)  # Numero de Factura
                else:
                    ws1.write(row, col + 6, "", line_content_style)

                ws1.write(row, col + 7, invoice.invoice_sequence, line_content_style)  # Numero de control


                ws1.write(row, col + 8, invoice.supplier_control_number,line_content_style)  # nro de nota de debito

                if (invoice.origin == 0):
                    ws1.write(row, col + 9, "", line_content_style)  # nro de nota de credito
                else:
                    ws1.write(row, col + 9, invoice.move_id.name, line_content_style)

                if (invoice.origin == 0):
                    ws1.write(row, col + 10, "", line_content_style)  # nro factura afectada
                else:
                    ws1.write(row, col + 10, invoice.origin, line_content_style)


                if post_exectas == 1:  # Si una factura es reembolsada

                    # Total compras con IVA
                    ws1.write(row, col + 11, 0, line_content_style)

                    # Exectas
                    ws1.write(row, col + 12, exent_p_fac, line_content_style)

                    # Exoneradas
                    ws1.write(row, col + 13, 0, line_content_style)

                    # Base Imponible
                    ws1.write(row, col + 14, 0, line_content_style)

                    # % Alicuota
                    ws1.write(row, col + 15, por_ali_0, line_content_style)

                    # Impuesto IVA
                    ws1.write(row, col + 16, 0, line_content_style)

                    # Retencion de IVA
                    ws1.write(row, col + 17, 0, line_content_style)

                    ## traer datos retencion de iva de otra tabla=============

                    self.retivas = self.env['snc.retiva.partners.lines'].search([('invoice_id', '=', ids_accounts)])

                    n_comprob = self.retivas.retiva_partner_id.name
                    fec_comprob = self.retivas.retiva_partner_id.fecha_contabilizacion

                    # =========================================================

                    # Nro. Comprobante de Retencion
                    ws1.write(row, col + 18, n_comprob, line_content_style)

                    # Fecha comp
                    ws1.write(row, col + 19, fec_comprob, line_content_style)

                    post_exectas = 0

                elif cont_16 == 1:

                    # Total compras con IVA
                    ws1.write(row, col + 11, tot_comp_p_iva_16, line_content_style)

                    # Exectas
                    ws1.write(row, col + 12, 0, line_content_style)

                    # Exoneradas
                    ws1.write(row, col + 13, 0, line_content_style)

                    # Base Imponible
                    ws1.write(row, col + 14, base_16, line_content_style)

                    # % Alicuota
                    ws1.write(row, col + 15, por_ali_16, line_content_style)

                    # Impuesto IVA
                    ws1.write(row, col + 16, tax_16, line_content_style)

                    # Retencion de IVA
                    ws1.write(row, col + 17, ret_16, line_content_style)

                    ## traer datos retencion de iva de otra tabla=============

                    self.retivas = self.env['snc.retiva.partners.lines'].search([('invoice_id', '=', ids_accounts)])

                    n_comprob = self.retivas.retiva_partner_id.name
                    fec_comprob = self.retivas.retiva_partner_id.fecha_contabilizacion

                    # =========================================================

                    # Nro. Comprobante de Retencion
                    ws1.write(row, col + 18, n_comprob, line_content_style)

                    # Fecha comp
                    ws1.write(row, col + 19, fec_comprob, line_content_style)

                    cont_16 = 0

                elif cont_8 == 1:

                    # Total compras con IVA
                    ws1.write(row, col + 11, tot_comp_p_iva_8, line_content_style)

                    # Exectas
                    ws1.write(row, col + 12, 0, line_content_style)

                    # Exoneradas
                    ws1.write(row, col + 13, 0, line_content_style)

                    # Base Imponible
                    ws1.write(row, col + 14, base_8, line_content_style)

                    # % Alicuota
                    ws1.write(row, col + 15, por_ali_8, line_content_style)

                    # Impuesto IVA
                    ws1.write(row, col + 16, tax_8, line_content_style)

                    # Retencion de IVA
                    ws1.write(row, col + 17, ret_8, line_content_style)

                    ## traer datos retencion de iva de otra tabla=============

                    self.retivas = self.env['snc.retiva.partners.lines'].search([('invoice_id', '=', ids_accounts)])

                    n_comprob = self.retivas.retiva_partner_id.name
                    fec_comprob = self.retivas.retiva_partner_id.fecha_contabilizacion

                    # =========================================================

                    # Nro. Comprobante de Retencion
                    ws1.write(row, col + 18, n_comprob, line_content_style)

                    # Fecha comp
                    ws1.write(row, col + 19, fec_comprob, line_content_style)

                    cont_8 = 0

                elif cont_31 == 1:

                    # Total compras con IVA
                    ws1.write(row, col + 11, tot_comp_p_iva_31, line_content_style)

                    # Exectas
                    ws1.write(row, col + 12, 0, line_content_style)

                    # Exoneradas
                    ws1.write(row, col + 13, 0, line_content_style)

                    # Base Imponible
                    ws1.write(row, col + 14, base_31, line_content_style)

                    # % Alicuota
                    ws1.write(row, col + 15, por_ali_31, line_content_style)

                    # Impuesto IVA
                    ws1.write(row, col + 16, tax_31, line_content_style)

                    # Retencion de IVA
                    ws1.write(row, col + 17, ret_31, line_content_style)

                    ## traer datos retencion de iva de otra tabla=============

                    self.retivas = self.env['snc.retiva.partners.lines'].search([('invoice_id', '=', ids_accounts)])

                    n_comprob = self.retivas.retiva_partner_id.name
                    fec_comprob = self.retivas.retiva_partner_id.fecha_contabilizacion

                    # =========================================================

                    # Nro. Comprobante de Retencion
                    ws1.write(row, col + 18, n_comprob, line_content_style)

                    # Fecha comp
                    ws1.write(row, col + 19, fec_comprob, line_content_style)

                    cont_31 = 0

                row += 1

        row +=1
        ws1.write(row,col+11,"TOTALES:",sub_header_style_c)
        ws1.write(row,col+12,total_con_iva,sub_header_style_r) #Total con IVA
        ws1.write(row,col+13,tot_no_gra,sub_header_style_r) # EXONERADAS NO AGRAVADAS
        ws1.write(row,col+14,tot_exentas,sub_header_style_r) # exoneradas
        ws1.write(row,col+15,total_bi,sub_header_style_r)# base imponible
        ws1.write(row,col+17,total_iva,sub_header_style_r) #iva
        ws1.write(row,col+18,total_iva_reten,sub_header_style_r) #retencion de iva

        tot_base_exentas = 0
        tot_iva_exentas = 0
        tot_reten_exent = 0

        tot_base_no_gra = 0
        tot_iva_no_gra = 0
        tot_reten_no_gra = 0

        for l in self.line:
            if l.alicuota_type == 'general':
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
            if l.alicuota_type == 'additional':
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
            if l.alicuota_type == 'reduced':
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
            if l.alicuota_type == 'exempt':
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
            if l.alicuota_type == 'no_tax_credit':
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

        row +=2
        result_right = xlwt.easyxf('font: name Helvetica, height 170; align: horiz right;')
        ws1.write_merge(row, row, 11, 15,"Resumen de Ventas",sub_header_style_c)
        ws1.write(row,col+16,"Base Imponible",sub_header_style_c)
        ws1.write(row,col+17,"Debito Fiscal",sub_header_style_c)
        ws1.write_merge(row, row, 18, 19,"IVA retenido por comp.",sub_header_style_c)
        row+=1
        ws1.write_merge(row, row, 11, 15,"Ventas de Exportacion",sub_header_style)
        ws1.write(row, col + 16, 0, result_right)
        ws1.write(row, col + 17, 0, result_right)
        ws1.write(row, col + 18, 0, result_right)
        row+=1
        
        ws1.write_merge(row, row, 11, 15,"Ventas Internas Afectadas solo Alicuota General",sub_header_style)
        ws1.write(row, col + 16, invoice.float_format(base_general), result_right)
        ws1.write(row, col + 17, invoice.float_format(tax_general), result_right)
        ws1.write(row, col + 18, invoice.float_format(ret_general), result_right)
        row+=1
        ws1.write_merge(row, row, 11, 15,"Ventas Internas Afectadas solo Alicuota General + Adicional",sub_header_style)
        ws1.write(row, col + 16, invoice.float_format(base_genel_mas_adicional), result_right)
        ws1.write(row, col + 17, invoice.float_format(tax_genel_mas_adicional), result_right)
        ws1.write(row, col + 18, invoice.float_format(ret_genel_mas_adicional), result_right)
        row+=1
        ws1.write_merge(row, row, 11, 15,"Ventas Internas Afectadas solo Alicuota Reducida",sub_header_style)
        ws1.write(row, col + 16, invoice.float_format(base_reducido), result_right)
        ws1.write(row, col + 17, invoice.float_format(tax_reducido), result_right)
        ws1.write(row, col + 18, invoice.float_format(ret_reducido), result_right)
        row+=1
        ws1.write_merge(row, row, 11, 15,"Ventas Internas Exentas o Exoneradas",sub_header_style)
        ws1.write(row, col + 16, invoice.float_format(tot_base_exentas), result_right)
        ws1.write(row, col + 17, invoice.float_format(tot_iva_exentas), result_right)
        ws1.write(row, col + 18, invoice.float_format(tot_reten_exent), result_right)
        row+=1
        ws1.write_merge(row, row, 11, 15,"Ventas Internas No Gravadas",sub_header_style)
        ws1.write(row, col + 16, invoice.float_format(tot_base_no_gra), result_right)
        ws1.write(row, col + 17, invoice.float_format(tot_iva_no_gra), result_right)
        ws1.write(row, col + 18, invoice.float_format(tot_reten_no_gra), result_right)
        row+=1
        ws1.write_merge(row, row, 11, 15,"Total",sub_header_style)
        ws1.write(row, col + 16, invoice.float_format((base_general+base_genel_mas_adicional+base_reducido+tot_base_exentas+tot_base_no_gra)), result_right)
        ws1.write(row, col + 17, invoice.float_format((tax_general+tax_genel_mas_adicional+tax_reducido+tot_iva_exentas+tot_iva_no_gra)), result_right)
        ws1.write(row, col + 18, invoice.float_format((ret_general+ret_genel_mas_adicional+ret_reducido+tot_reten_exent+tot_reten_no_gra)), result_right)

        wb1.save(fp)
        out = base64.encodestring(fp.getvalue())
        fecha  = datetime.now().strftime('%d/%m/%Y') 
        self.write({'state': 'get', 'report': out, 'name':'Libro de ventas '+ fecha+'.xls'})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.wizard.libro.ventas',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
