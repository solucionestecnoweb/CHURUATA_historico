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
    #partner_id  = fields.Many2one(comodel_name='res.partner', string='Partner')
    
    """invoice_number =   fields.Char(string='Fac. Número')
    invoice_ctrl_number = fields.Char(string='Nro Control')
    nro_comp = fields.Char(string='Nro Comprobante')
    factura_total = fields.Float(string='Monto Factura')
    base_imponible = fields.Float(string='base imponible')
    retenido = fields.Float(string='retenido')
    porcentaje = fields.Float(string='Porcentaje')
    codigo = fields.Char(string='Código Actividad Económica')
    invoice_id = fields.Many2one('account.move')"""


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

    def get_invoice(self,dett,id_code):
        t=self.env['resumen.islr.wizard.pdf']
        cursor_resumen = self.env['isrl.retention'].search([
            ('date_isrl','>=',self.date_from),
            ('date_isrl','<=',self.date_to),
            ('state','=','done'),
            ])
        for det in cursor_resumen:
            det2=det.lines_id.search([('code','=',id_code.code)])
            for det_line in det2:
                values={
                'fecha_comprobante':det.date_isrl,
                'invoice_id':det.invoice_id.id,
                'retention_id':det_line.retention_id.id,
                'code':det_line.code,
                'abono_cta':abs(det.invoice_id.amount_total_signed),
                'cant_retencion':det_line.retention,
                'porcentaje':det_line.cantidad,
                'total':det_line.total,
                'id_code':id_code.id,
                #'factura_total':signo*self.conv_div_nac(det.invoice_id.amount_total,det),
                }
                pdf_id = t.create(values)
        line_resumen=self.env['resumen.islr.wizard.pdf'].search([('id_code','=',id_code.code)])
        code=self.env['resumen.islr.wizard.code'].search([('code','=',dett.code)])# validar el code
        for x in code:
            self.env['resumen.islr.wizard.code'].browse(x.id).write({
                'line_resumen':line_resumen,
                })
        #self.line_people = self.env['resumen.islr.wizard.pdf'].search([])

    def arma_tabla_type_people(self):
        people=self.env['resumen.islr.wizard.type.people']
        people.search([]).unlink()
        code=self.env['resumen.islr.wizard.code']
        code.search([]).unlink()
        t=self.env['resumen.islr.wizard.pdf']
        d=t.search([])
        d.unlink()
        aux=''
        cursor = self.env['islr.rates'].search([],order='people_type ASC')
        for det_cur in cursor:
            if det_cur.people_type:
                if aux!=det_cur.people_type:
                    aux=det_cur.people_type
                    values={'name':det_cur.people_type,}
                    id_people=people.create(values)
                    #self.arma_tabla_code(det_cur,id_people)

    def arma_tabla_code(self,det_cur,id_people):
        code2=self.env['resumen.islr.wizard.code']
        cursor2 = self.env['islr.rates'].search([('people_type','=',det_cur.people_type)])
        for det in cursor2:
            values={'code':det.code,'islr_concept_id':det.islr_concept_id.id,'id_people':id_people.id,}
            id_code=code2.create(values)
            #self.get_invoice(det,id_code)

        line_code=self.env['resumen.islr.wizard.code'].search([('id_people','=',id_people.id)])
        people=self.env['resumen.islr.wizard.type.people'].search([('name','=',det_cur.people_type)])
        for x in people:
            self.env['resumen.islr.wizard.type.people'].browse(x.id).write({
                'line_code':line_code,
                })
        #raise UserError(_('det_cur.line_code: %s')%det_cur.line_code)


    def print_resumen_islr(self):
        #pass
        w=self.env['wizard.resumen.islr'].search([('id','!=',self.id)])
        w.unlink()
        self.arma_tabla_type_people()
        #self.line_people = self.env['resumen.islr.wizard.type.people'].search([])
        #return {'type': 'ir.actions.report','report_name': 'l10n_ve_resumen_retenciones.libro_resumen_islr','report_type':"qweb-pdf"}