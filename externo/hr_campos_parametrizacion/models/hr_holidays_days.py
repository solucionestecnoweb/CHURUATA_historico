# coding: utf-8
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
import calendar
from odoo.exceptions import UserError, ValidationError

class hr_payroll_hollydays(models.Model):
    _name = 'hr.payroll.hollydays'
    _description = 'Dias Feriados'

    hollydays = fields.Boolean('Dias')
    nombre = fields.Char('Motivo del dia Festivo', size=256, required=True)
    date_from = fields.Date('Desde', required=True)
    date_to = fields.Date('Hasta')

    @api.onchange('date_from')
    def onchange_date_from(self):
        if not self.hollydays:
            self.date_to = self.date_from

    @api.onchange('hollydays')
    def onchange_date_hollydays(self):
        if not self.hollydays:
            self.date_to = self.date_from

class hr_special_days(models.Model):
    _inherit = 'hr.payslip'

    saturdays = fields.Integer('Sabados', compute='_compute_days', store=True, readonly=True)
    sundays = fields.Integer('Domingos', compute='_compute_days', store=True, readonly=True)
    mondays = fields.Integer('Nro lunes', compute='_compute_days', help='este campo trae el numero de lunes',store=True, readonly=True)
    workdays = fields.Integer('Dias habiles', help='este campo los dias habiles del periodo', compute='_compute_days',
                             store=True, readonly=True)
    holydays = fields.Integer('Dias Festivos', compute='_compute_days', readonly=True)
    hollydays_str = fields.Char('Feriados', size=768)
    days_attended = fields.Char(string='Días asistidos', compute='_compute_days_attended')

    @api.depends('date_from', 'date_to')
    def _compute_days(self):
        for selff in self:
            holydays = mondays = saturdays = sundays = workdays = nro_feriado = 0
            hr_payroll_hollydays = selff.env['hr.payroll.hollydays']
            selff.actualiza_periodo()
            dia_in=selff.dia(selff.date_from)
            mes_in=selff.mes(selff.date_from)
            ano_in=selff.ano(selff.date_from)
            dia_fin=selff.dia(selff.date_to)
            mes_fin=selff.mes(selff.date_to)
            ano_fin=selff.ano(selff.date_to)
            dia=dia_in

            dif_dia=selff.days_dife(selff.date_from,selff.date_to)
            dif_dia=dif_dia+1
            mes=mes_in
            for i in range(dif_dia):
                dia_aux=0
                dia_aux=calendar.weekday(ano_in,mes,dia)
                if dia_aux==0:
                    mondays=mondays+1
                if dia_aux==5:
                    saturdays=saturdays+1
                if dia_aux==6:
                    sundays=sundays+1
                dia=dia+1
                if dia>selff.verif_ult_dia_mes(mes):
                    dia=1
                    mes=mes+1
            hollyday_id = hr_payroll_hollydays.search([('date_to','<=',selff.date_to),('date_from','>=',selff.date_from),('hollydays','=',True)])
            #raise UserError(_('valor= %s')%hollyday_id)
            if hollyday_id:
                for det_holyday in hollyday_id:
                    nro_feriado=1+selff.days_dife(det_holyday.date_from,det_holyday.date_to)
                    holydays=holydays+nro_feriado

            workdays = dif_dia - saturdays - sundays - holydays
            selff.saturdays=saturdays
            selff.sundays=sundays
            selff.mondays=mondays
            selff.workdays=workdays
            selff.holydays=holydays

    @api.depends('date_from', 'date_to')
    def _compute_days_attended(self):
        for selff in self:
            nro_asis=0
            asistencia=selff.env['hr.attendance'].search([('check_out','<=',selff.date_to),('check_in','>=',selff.date_from)])
            #raise UserError(_('valor= %s')%asistencia)
            if asistencia:
                for det in asistencia:
                    nro_asis=nro_asis+1
            selff.days_attended=nro_asis
            #self.days_attended=69

    def dia(self,date):
        fecha = str(date)
        fecha_aux=fecha
        dia=fecha[8:10]  
        resultado=dia
        return int(resultado)

    def mes(self,date):
        fecha = str(date)
        fecha_aux=fecha
        mes=fecha[5:7]
        resultado=mes
        return int(resultado)

    def ano(self,date):
        fecha = str(date)
        fecha_aux=fecha
        ano=fecha_aux[0:4]  
        resultado=ano
        return int(resultado)

    def days_dife(self,d1, d2):
       return abs((d2 - d1).days)

    def actualiza_periodo(self):
        feriados=self.env['hr.payroll.hollydays'].search([])
        if feriados:
            for det in feriados:
                inicio=det.date_from
                fin=det.date_to
                ano_actual=self.ano(self.date_from)
                dia=self.dia(inicio)
                mes=self.mes(inicio)
                ano=self.ano(inicio)
                nuevo_from=str(ano_actual)+"-"+str(mes)+"-"+str(dia)
                dia=self.dia(fin)
                mes=self.mes(fin)
                ano=self.ano(fin)
                nuevo_to=str(ano_actual)+"-"+str(mes)+"-"+str(dia)
                det.date_from=nuevo_from
                det.date_to=nuevo_to

    def verif_ult_dia_mes(self,mes):
        if mes==1:
            ultimo=31
        if mes==2:
            ultimo=28
        if mes==3:
            ultimo=31
        if mes==4:
            ultimo=30
        if mes==5:
            ultimo=31
        if mes==6:
            ultimo=30
        if mes==7:
            ultimo=31
        if mes==8:
            ultimo=31
        if mes==9:
            ultimo=30
        if mes==10:
            ultimo=31
        if mes==11:
            ultimo=30
        if mes==12:
            ultimo=31
        return ultimo
