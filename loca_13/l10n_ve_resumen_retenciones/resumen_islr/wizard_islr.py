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

class TablaTypePeople(models.Model):
    _name = "resumen.islr.wizard.type.people"

    name=fields.Char(string='Tipo de persona')
    line_code  = fields.Many2many(comodel_name='resumen.islr.wizard.code', string='Lineas')

    def float_format4(self,valor):
        #valor=self.base_tax
        if valor:
            result = '{:,.2f}'.format(valor)
            result = result.replace(',','*')
            result = result.replace('.',',')
            result = result.replace('*','.')
        else:
            result="0,00"
        return result

    def nombre(self,valor):
        nombre='---'
        if valor=='resident_nat_people':
            nombre='PNRE Persona Natural Residente'
        if valor=='non_resit_nat_people':
            nombre='PNNR Persona Natural no Residente'
        if valor=='domi_ledal_entity':
            nombre='PJDO Persona Juridica Domiciliada'
        if valor=='legal_ent_not_domicilied':
            nombre='PJDO Persona Juridica no Domiciliada'
        return nombre

class TablaCodigo(models.Model):
    _name = 'resumen.islr.wizard.code'

    code= fields.Char(string='Codico')
    islr_concept_id = fields.Many2one('islr.concept')
    id_people= fields.Many2one('resumen.islr.wizard.type.people')
    line_resumen = fields.Many2many(comodel_name='resumen.islr.wizard.pdf', string='Lineas')

    def float_format3(self,valor):
        #valor=self.base_tax
        if valor:
            result = '{:,.2f}'.format(valor)
            result = result.replace(',','*')
            result = result.replace('.',',')
            result = result.replace('*','.')
        else:
            result="0,00"
        return result



class ResumenIslrModelo(models.Model):
    _name = "resumen.islr.wizard.pdf"

    fecha_comprobante = fields.Date(string='Fecha Comprobante')
    #fecha_doc = fields.Date(string='Fecha Documento')
    invoice_id = fields.Many2one('account.move') # traego rif, fecha factura, datos de proveedor
    retention_id=fields.Many2one('isrl.retention')
    code= fields.Char(string='Codico')
    abono_cta=fields.Float(string='Abono Cuenta')
    cant_retencion=fields.Float(string='Cantidad de objeto a retencion')
    porcentaje=fields.Float(string='Porcentaje')
    total = fields.Float(string='Monto Total')
    id_code= fields.Many2one('resumen.islr.wizard.code')


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
    _name = 'wizard.resumen.islr'
    _description = "Resumen Retenciones islr"

    date_from  = fields.Date('Date From', default=lambda *a:(datetime.now() - timedelta(days=(1))).strftime('%Y-%m-%d'))
    date_to = fields.Date(string='Date To', default=lambda *a:datetime.now().strftime('%Y-%m-%d'))
    date_actual = fields.Date(default=lambda *a:datetime.now().strftime('%Y-%m-%d'))

    company_id = fields.Many2one('res.company','Company',default=lambda self: self.env.user.company_id.id)
    line_people  = fields.Many2many(comodel_name='resumen.islr.wizard.type.people', string='Lineas')


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
        t=self.env['resumen.islr.wizard.pdf']
        d=t.search([])
        d.unlink()
        cursor_resumen = self.env['isrl.retention'].search([
            ('date_isrl','>=',self.date_from),
            ('date_isrl','<=',self.date_to),
            ('state','=','done'),
            ])
        for det in cursor_resumen:
            #det2=det.lines_id.search([('code','=',id_code.code)])
            #if det.invoice_id.type=="in_invoice" or det.invoice_id.type=="in_refund" or det.invoice_id.type=="in_recept":
            if det.invoice_id.type=="in_invoice" or det.invoice_id.type=="in_refund":
	            for det_line in det.lines_id:
	                values={
	                'fecha_comprobante':det.date_isrl,
	                'invoice_id':det.invoice_id.id,
	                'retention_id':det_line.retention_id.id,
	                'code':det_line.code,
	                'abono_cta':abs(det.invoice_id.amount_total_signed),
	                'cant_retencion':det_line.base,
	                'porcentaje':det_line.cantidad,
	                'total':det_line.total,
	                #'id_code':id_code.id,
	                }
	                pdf_id = t.create(values)
        #self.line_people = self.env['resumen.islr.wizard.pdf'].search([])

    def arma_tabla_code(self):
        code=self.env['resumen.islr.wizard.code']
        code.search([]).unlink()
        aux_code=''

        tabla_resumen=self.env['resumen.islr.wizard.pdf'].search([],order='code ASC')
        for det_res in tabla_resumen:
            if aux_code!=det_res.code:
                aux_code=det_res.code
                cursor=self.env['islr.rates'].search([('code','=',det_res.code)])
                for det in cursor:
                    values={
                    'code':det.code,
                    'islr_concept_id':det.islr_concept_id.id,
                    'line_resumen':self.env['resumen.islr.wizard.pdf'].search([('code','=',det.code)]),
                    #'id_people':id_people.id,
                    }
                    id_code=code.create(values)
                    det_res.id_code=id_code
        #raise UserError(_('det_cur.line_code: %s')%det_cur.line_code)

    def arma_tabla_type_people(self):
        people=self.env['resumen.islr.wizard.type.people']
        people.search([]).unlink()
        aux=''
        tabla_code=self.env['resumen.islr.wizard.code'].search([])
        for det_cod in tabla_code:
            #det_cod.islr_concept_id.id.name
            cursor2=self.env['islr.rates'].search([('islr_concept_id','=',det_cod.islr_concept_id.id),('code','=',det_cod.code)],order='people_type ASC')
            for det in cursor2:
                if aux!=det.people_type:
                    aux=det.people_type
                    valida=people.search([('name','=',det.people_type)])
                    if not valida:
                        values={
                        'name':det.people_type,
                        }
                        id_people=people.create(values)
                    else:
                        id_people=valida.id
                det_cod.id_people=id_people # OJO PROBAR PRIMERO

        for det_people in people.search([]):
            lista_code=self.env['resumen.islr.wizard.code'].search([('id_people','=',det_people.id)])
            self.env['resumen.islr.wizard.type.people'].browse(det_people.id).write({
                'line_code':lista_code,
                })



    def print_resumen_islr(self):
        #pass
        w=self.env['wizard.resumen.islr'].search([('id','!=',self.id)])
        w.unlink()
        self.get_invoice()
        self.arma_tabla_code()
        self.arma_tabla_type_people()
        self.line_people = self.env['resumen.islr.wizard.type.people'].search([])
        return {'type': 'ir.actions.report','report_name': 'l10n_ve_resumen_retenciones.libro_resumen_islr','report_type':"qweb-pdf"}