# coding: utf-8
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
import calendar
from odoo.exceptions import UserError, ValidationError


class hr_special_days(models.Model):
    _inherit = 'hr.payslip'

    #days_attended = fields.Char(string='Días asistidos', compute='_compute_days_attended')
    monto_bono_alimenticio = fields.Float(compute='_bono_div')


    def _bono_div(self):
        for selff in self:
            id_moneda_bono=selff.employee_id.contract_id.bono_alimenticio_currency.id
            id_moneda_compa=selff.company_id.currency_id.id
            monto_bono_alimenticio=selff.employee_id.contract_id.bono_alimenticio_value
            valor_aux=0.000000000000000000000000000001
            if id_moneda_compa!=id_moneda_bono:
                tasa= selff.env['res.currency.rate'].search([('currency_id','=',id_moneda_bono),('hora','<=',selff.date_to)],order="hora asc") #('name','<=',self.date)
                for det_tasa in tasa:
                    valor_aux=det_tasa.rate_real
                rate=round(1*valor_aux,2)
                resultado=monto_bono_alimenticio*rate
            else:
                resultado=monto_bono_alimenticio
            selff.monto_bono_alimenticio=resultado