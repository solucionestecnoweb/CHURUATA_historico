# coding: utf-8
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
import calendar
from odoo.exceptions import UserError, ValidationError

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    zapatos = fields.Selection([('32','32'),('33','33'),('34','34'),('35','35'),('36','36'),('37','37'),('38','38'),('39','39'),('40','40'),('41','41'),('42','42'),('43','43'),('44','44'),('45','45'),('46','46')])
    camisas = fields.Selection([('XS', 'XS'),('S', 'S'),('M', 'M'),('M-L', 'M-L'),('L', 'L'),('L-XL', 'L-XL'),('XL', 'XL'),('XL-XXL', 'XL-XXL'),('XXL', 'XXL')])
    pantalon = fields.Selection([('24','24'),('25','25'),('26','26'),('27','27'),('28','28'),('29','29'),('30','30'),('31','31'),('32','32'),('33','33'),('34','34'),('35','35'),('36','36'),('37','37'),('38','38'),('39','39'),('40','40'),('41','41'),('42','42'),('43','43'),('44','44'),('45','45'),('46','46')])
    chemise = fields.Selection([('XS', 'XS'),('S', 'S'),('M', 'M'),('M-L', 'M-L'),('L', 'L'),('L-XL', 'L-XL'),('XL', 'XL'),('XL-XXL', 'XL-XXL'),('XXL', 'XXL')])