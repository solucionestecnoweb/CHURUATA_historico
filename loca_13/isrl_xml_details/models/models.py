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

_logger = logging.getLogger(__name__)

class XmlDetails(models.Model):
    _name = "account.xml.detalle.line"

    rif_retenido = fields.Char(string='RIF Retenido')
    numero_factura = fields.Char(string='Número de Factura')
    numero_control = fields.Char(string='Número de Control')
    fecha_operacion = fields.Date(string='Fecha de Operación') 
    codigo_concepto = fields.Char(string='Código del Concepto')
    monto_operacion = fields.Char(string='Monto de Operación')
    porcentaje_retencion = fields.Char(string='Porcentaje de Retención')
    detalle_id = fields.Many2one(comodel_name='account.xml.detalle', string='Declaracion')
    

class XmlLines(models.Model):
    _name = "account.xml.detalle"

    date_from = fields.Date(string='Desde', default=lambda *a:datetime.now().strftime('%Y-%m-%d'))
    date_to = fields.Date('Hasta', default=lambda *a:(datetime.now() + timedelta(days=(1))).strftime('%Y-%m-%d'))
    state = fields.Selection([('por_generar', 'Por Generar'),('generada','Generada')],default='por_generar')
    report = fields.Binary('XML', filters='.xls', readonly=True)
    name =  fields.Char('File Name', size=32)
    company_id = fields.Many2one('res.company','Company',default=lambda self: self.env.user.company_id.id, readonly=True)
    line_id    = fields.One2many(comodel_name='account.xml.detalle.line', inverse_name='detalle_id', string='Lineas')
    
    def views_detalle(self):
        action = self.env.ref('isrl_xml_details.action_account_reten_details_line').read()[0]
        action['domain'] = [('id', 'in', self.line_id.ids)]
        action['context'] = dict(self._context, default_detalle_id=self.id)
        return action

    def generar_xml(self):
        periodo = str(self.date_from.year) 
        rif= self.env.company.vat
        if  10 > int(self.date_from.month)   :
            periodo += '0'+ str(self.date_from.month)
        else :
            periodo += str(self.date_from.month)

        elemento_1 = ET.Element('RelacionRetencionesISLR',RifAgente=rif,Periodo=periodo)
        for item in self.line_id:
            fecha = ''
            if  10 > int(item.fecha_operacion.day)   :
                fecha += '0'+ str(item.fecha_operacion.day)+ '/'
            else :
                fecha += str(item.fecha_operacion.day)+ '/'
            
            if  10 > int(item.fecha_operacion.month)   :
                fecha += '0'+ str(item.fecha_operacion.month)+ '/'
            else :
                fecha += str(item.fecha_operacion.month)+ '/'
            fecha += str(item.fecha_operacion.year)

            if item.numero_factura:
                nro_fact=item.numero_factura.replace('-', '')
                nro_fact=item.numero_factura[:1]+item.numero_factura[-10:]
            else:
                nro_fact=0
            elemento_hijo_1 = ET.SubElement(elemento_1, 'DetalleRetencion')
            elemento_hijo_2 = ET.SubElement(elemento_hijo_1, 'RifRetenido').text=str(item.rif_retenido)
            elemento_hijo_3 = ET.SubElement(elemento_hijo_1, 'NumeroFactura').text=str(nro_fact) if item.numero_factura else '0'
            elemento_hijo_4 = ET.SubElement(elemento_hijo_1, 'NumeroControl').text=str(item.numero_control) if  item.numero_control else 'NA'
            elemento_hijo_5 = ET.SubElement(elemento_hijo_1, 'FechaOperacion').text=str(fecha)
            elemento_hijo_6 = ET.SubElement(elemento_hijo_1, 'CodigoConcepto').text=str(item.codigo_concepto)
            elemento_hijo_7 = ET.SubElement(elemento_hijo_1, 'MontoOperacion').text=str(item.monto_operacion)
            elemento_hijo_8 = ET.SubElement(elemento_hijo_1, 'PorcentajeRetencion').text=str(item.porcentaje_retencion)

        tree = ET.ElementTree(elemento_1)
        tree.write('isrl_odoo.xml', encoding='utf-8',xml_declaration=True) #Habilitar
        #tree.write('/opt/odoo/addons/isrl_retention/static/doc/isrl_odoo.xml', encoding='utf-8',xml_declaration=True)
        #tree.write('/mnt/extra-addons/isrl_retention/static/doc/isrl_odoo.xml', encoding='utf-8',xml_declaration=True)
        #tree.write('/home/admin-odoo/odoo/odoo_addons/isrl_retention/static/doc/isrl_odoo.xml', encoding='utf-8',xml_declaration=True)

        xml = open('isrl_odoo.xml') # Habilitar
        #xml = open('/home/admin-odoo/odoo/odoo_addons/isrl_retention/static/doc/isrl_odoo.xml') # Habilitar
        #xml = open('/mnt/extra-addons/isrl_retention/static/doc/isrl_odoo.xml') # Habilitar
        #xml = open('/opt/odoo/addons/isrl_retention/static/doc/isrl_odoo.xml') # Habilitar
        out = xml.read()
        base64.b64encode(bytes(out, 'utf-8'))
        action = self.env.ref('isrl_retention.action_account_xml_wizard_descargar').read()[0]
        #self.write({'state': 'get', 'report': base64.b64encode(bytes(out, 'utf-8')), 'name':'isrl_odoo.xml'})
        ids = self.env['account.xml.wizard.descargar'].create({ 'report': base64.b64encode(bytes(out, 'utf-8')), 'name':'isrl_odoo.xml'})
        action['res_id']= ids.id
        return action

class WiizarXml(models.TransientModel):
    _inherit = "account.xml.wizard"

    def create_xml(self):
        documento = self.env['account.xml.detalle'].create({
            'date_from':self.date_from,
            'date_to':self.date_to,
        })

        retencion = self.env['isrl.retention'].search([
            ('date_isrl','>=',self.date_from),
            ('date_isrl','<=',self.date_to),
            ('state','in',('done','cancel' )),
            ('type','in',('in_invoice','in_refund','in_receipt'))
            ])

        for item in retencion:
            for line in item.lines_id:
                doc = str(item.partner_id.doc_type)
                if  len(item.partner_id.vat) == 6 :
                    doc += '0'+ str(item.partner_id.vat)
                else :
                    doc += str(item.partner_id.vat)

                linea = self.env['account.xml.detalle.line'].create({
                'rif_retenido': str(doc),
                'numero_factura': str(item.invoice_id.invoice_number),
                'numero_control': str(item.invoice_id.invoice_ctrl_number.replace('-', '')),
                'fecha_operacion': item.date_isrl,
                'codigo_concepto' : str(line.code),
                'monto_operacion' : str(line.base),
                'porcentaje_retencion' : str(int(line.cantidad)),
                'detalle_id' : documento.id
                })
        action = self.env.ref('isrl_xml_details.action_account_reten_details_wizard').read()[0]
        ids = documento
        action['res_id']= ids.id
        return action