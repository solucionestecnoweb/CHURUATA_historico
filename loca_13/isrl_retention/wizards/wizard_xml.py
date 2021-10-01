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

class WiizarXml(models.TransientModel):
    _name = "account.xml.wizard"

    date_from = fields.Date(string='Date From', default=lambda *a:datetime.now().strftime('%Y-%m-%d'))
    date_to = fields.Date('Date To', default=lambda *a:(datetime.now() + timedelta(days=(1))).strftime('%Y-%m-%d'))
    state = fields.Selection([('choose', 'choose'), ('get', 'get')],default='choose')
    report = fields.Binary('Prepared file', filters='.xls', readonly=True)
    name =  fields.Char('File Name', size=32)
    
    def create_xml(self):

        retencion = self.env['isrl.retention'].search([
            ('date_isrl','>=',self.date_from),
            ('date_isrl','<=',self.date_to),
            ('state','in',('done','cancel' )),
            ('type','in',('in_invoice','in_refund','in_receipt'))
            ])

        periodo = str(self.date_from.year) 
        rif= self.env.company.vat
        if  10 > int(self.date_from.month)   :
            periodo += '0'+ str(self.date_from.month)
        else :
            periodo += str(self.date_from.month)

        elemento_1 = ET.Element('RelacionRetencionesISLR',RifAgente=rif,Periodo=periodo)
        for item in retencion:
            for line in item.lines_id:
                doc = str(item.partner_id.doc_type)
                if  len(item.partner_id.vat) == 6 :
                    doc += '0'+ str(item.partner_id.vat)
                else :
                    doc += str(item.partner_id.vat)
                fecha = ''
                #fecha = str(item.date_isrl.day)+ '/' + str(item.date_isrl.month) + "/" + str(item.date_isrl.year)
                if  10 > int(item.date_isrl.day)   :
                    fecha += '0'+ str(item.date_isrl.day)+ '/'
                else :
                    fecha += str(item.date_isrl.day)+ '/'
                
                if  10 > int(item.date_isrl.month)   :
                    fecha += '0'+ str(item.date_isrl.month)+ '/'
                else :
                    fecha += str(item.date_isrl.month)+ '/'
                fecha += str(item.date_isrl.year)

                nro_fact=item.invoice_id.invoice_number.replace('-', '')
                nro_fact=nro_fact.replace('000','00')
                elemento_hijo_1 = ET.SubElement(elemento_1, 'DetalleRetencion')
                elemento_hijo_2 = ET.SubElement(elemento_hijo_1, 'RifRetenido').text=str(doc)
                elemento_hijo_3 = ET.SubElement(elemento_hijo_1, 'NumeroFactura').text=str(nro_fact)
                elemento_hijo_4 = ET.SubElement(elemento_hijo_1, 'NumeroControl').text=str(item.invoice_id.invoice_ctrl_number.replace('-', ''))
                elemento_hijo_5 = ET.SubElement(elemento_hijo_1, 'FechaOperacion').text=str(fecha)
                elemento_hijo_6 = ET.SubElement(elemento_hijo_1, 'CodigoConcepto').text=str(line.code)
                elemento_hijo_7 = ET.SubElement(elemento_hijo_1, 'MontoOperacion').text=str(line.base)
                elemento_hijo_8 = ET.SubElement(elemento_hijo_1, 'PorcentajeRetencion').text=str(int(line.cantidad))

        tree = ET.ElementTree(elemento_1)
        tree.write('isrl_odoo.xml', encoding='utf-8',xml_declaration=True) #Habilitar
        #tree.write('/opt/odoo/addons/isrl_retention/static/doc/isrl_odoo.xml', encoding='utf-8',xml_declaration=True)
        #tree.write('/home/admin-odoo/odoo/odoo_addons/isrl_retention/static/doc/isrl_odoo.xml', encoding='utf-8',xml_declaration=True)
        #tree.write('/mnt/extra-addons/isrl_retention/static/doc/isrl_odoo.xml', encoding='utf-8',xml_declaration=True)

        xml = open('isrl_odoo.xml') # Habilitar
        #xml = open('/opt/odoo/addons/isrl_retention/static/doc/isrl_odoo.xml') # Habilitar
        #xml = open('/home/admin-odoo/odoo/odoo_addons/isrl_retention/static/doc/isrl_odoo.xml') # Habilitar
        #xml = open('/mnt/extra-addons/isrl_retention/static/doc/isrl_odoo.xml') # Habilitar
        out = xml.read()
        base64.b64encode(bytes(out, 'utf-8'))
        action = self.env.ref('isrl_retention.action_account_xml_wizard_descargar').read()[0]
        #self.write({'state': 'get', 'report': base64.b64encode(bytes(out, 'utf-8')), 'name':'isrl_odoo.xml'})
        ids = self.env['account.xml.wizard.descargar'].create({ 'report': base64.b64encode(bytes(out, 'utf-8')), 'name':'isrl_odoo.xml'})
        action['res_id']= ids.id
        return action



class WiizarXmlDescargar(models.TransientModel):
    _name = "account.xml.wizard.descargar"
    
    def _set_name_value(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url = base_url + '/isrl_retention/static/doc/isrl_odoo.xml'
        return url

    name = fields.Char(string='Link',default=_set_name_value,readonly="True",)
    report = fields.Binary('Prepared file', filters='.xls', readonly=True)
