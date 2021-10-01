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
    _name = "account.arc.wizard"

    name  = fields.Many2one(comodel_name='res.partner', string='Empresa')
    date_from = fields.Date(string='Date From', default=lambda *a:datetime.now().strftime('%Y-%m-%d'))
    date_today = fields.Date(string='Date Today', default=lambda *a:datetime.now().strftime('%Y-%m-%d'))
    date_to = fields.Date('Date To', default=lambda *a:(datetime.now() + timedelta(days=(1))).strftime('%Y-%m-%d'))
    isrl_id = fields.Many2many(comodel_name='isrl.retention', string='ISLR')
    company_id = fields.Many2one('res.company', string='Company', required=True,default=lambda self: self.env.company)

    def get_isrl_id(self):
        self.isrl_id = self.env['isrl.retention'].search([
            ('date_isrl','>=',self.date_from),
            ('date_isrl','<=',self.date_to),
            ('partner_id','=',self.name.id),
            ('state','=','done'),
            ('type','in',('in_invoice','in_refund','in_receipt'))
            ],order="date_isrl asc")

    def print_pdf(self):
        self.get_isrl_id()
        return {'type': 'ir.actions.report','report_name': 'isrl_retention.report_arc','report_type':"qweb-pdf"}
    