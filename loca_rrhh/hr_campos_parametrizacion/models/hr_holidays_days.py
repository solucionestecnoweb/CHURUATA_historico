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
    hollydays_str = fields.Integer('Feriados Trabajados', compute='_compute_feriados_laborados')
    days_attended = fields.Integer(string='Días asistidos', compute='_compute_days_attended')
    days_inasisti = fields.Integer(string='Dias Inasistidos', compute='_compute_days_inasisti')#odoo 14

    horas_extras_diurnas = fields.Float(compute='_compute_horas_extras_diurnas')
    horas_extras_nocturnas = fields.Float()

    tiempo_antiguedad = fields.Integer(compute='_compute_tiempo_antiguedad')
    dias_vacaciones = fields.Integer(compute='_compute_dias_vacaciones')

    sueldo_anterior_mes = fields.Float(compute='_compute_sueldo_mes_anterior')
    dias_utilidades = fields.Integer(compute='_compute_dias_utilidades')
    dias_por_antiguedad = fields.Integer(compute='compute_dias_por_ano_antiguedad')

    @api.depends('employee_id','date_from','date_to')
    def _compute_tiempo_antiguedad(self):
        tiempo=0
        for selff in self:
            if selff.employee_id.id:
                fecha_ing=selff.employee_id.contract_id.date_start
                fecha_actual=selff.date_to
                dias=selff.days_dife(fecha_actual,fecha_ing)
                tiempo=dias/365
            selff.tiempo_antiguedad=tiempo

    @api.depends('employee_id')
    def _compute_dias_utilidades(self):
        for selff in self:
            dias_utilidades=30
            indicador=self.env['hr.payroll.indicadores.economicos'].search([('code','=','DUT')])
            if indicador:
                for det in indicador:
                    dias_utilidades=det.valor
            selff.dias_utilidades=dias_utilidades

    @api.depends('employee_id')
    def _compute_sueldo_mes_anterior(self):
        for selff in self:
            mes_actual=selff.mes(selff.date_to)
            mes_anterior=sueldo_anterior=0
            mes_anterior=mes_actual-1
            if mes_anterior==0:
                mes_anterior=12
            verifica=selff.env['hr.payroll.prestaciones'].search([('employee_id','=',selff.employee_id.id),('nro_mes','=',mes_anterior)],order='id desc')
            #raise UserError(_('valor= %s')%verifica)
            if verifica:
                for det in verifica:
                    sueldo_anterior=det.sueldo_base_mensual
            selff.sueldo_anterior_mes=sueldo_anterior

    @api.depends('employee_id')
    def _compute_dias_vacaciones(self):
        dias_difrute=0
        for selff in self:
            verifica=selff.env['hr.payroll.dias.vacaciones'].search([('service_years','=',selff.tiempo_antiguedad)])
            if verifica:
                for det in verifica:
                    dias_difrute=det.pay_day
            selff.dias_vacaciones=dias_difrute

    def compute_dias_por_ano_antiguedad(self):
        dias_antiguedad=0
        for selff in self:
            verifica_antig=selff.env['hr.payroll.dias.vacaciones'].search([('service_years','=',selff.tiempo_antiguedad)])
            if verifica_antig:
                for det in verifica_antig:
                    dias_antiguedad=det.pay_day_garantia
            selff.dias_por_antiguedad=dias_antiguedad

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

    @api.depends('date_from','date_to')
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

    #odoo 14
    @api.depends('date_from','date_to')
    def _compute_days_inasisti(self):
        for selff in self:
            dias_descontar=0
            verifica=selff.env['hr.leave'].search([('employee_id','=',selff.employee_id.id),('state','=','validate'),('request_date_to','<=',selff.date_to),('request_date_from','>=',selff.date_from)])
            #raise UserError(_('verifica= %s')%verifica)
            if verifica:
                for det in verifica:
                    dias_descontar=dias_descontar+det.number_of_days
            selff.days_inasisti=dias_descontar

    @api.depends('date_from','date_to','employee_id')
    def _compute_feriados_laborados(self):
        for selff in self:
            nro_feriado=nro_dia=0
            selff.hollydays_str=nro_feriado
            asistencia=selff.env['hr.attendance'].search([('check_out','<=',selff.date_to),('check_in','>=',selff.date_from),('employee_id','=',selff.employee_id.id)])
            #raise UserError(_('valor= %s')%asistencia)
            if asistencia:
                for det in asistencia:
                    fecha=det.check_out
                    dia=selff.dia(fecha)
                    mes=selff.mes(fecha)
                    ano=selff.ano(fecha)
                    nro_dia=calendar.weekday(ano,mes,dia)
                    if nro_dia==6:# aqui verifica si trabajo el domingo
                        nro_feriado=nro_feriado+1
                    # aqui verifica si trabaja en un dia feriado
                    lista_feriado=selff.env['hr.payroll.hollydays'].search([('date_from','<=',det.check_out),('date_to','>=',det.check_out)])
                    if lista_feriado:
                        for ret in lista_feriado:
                            nro_feriado=nro_feriado+1
            selff.hollydays_str=nro_feriado

    @api.depends('date_from','date_to','employee_id')
    def _compute_horas_extras_diurnas(self):
        for selff in self:
            horas=0
            dias_asis=0
            total_horas_extras=0
            selff.horas_extras_diurnas=total_horas_extras
            selff.horas_extras_nocturnas=total_horas_extras
            horas_extr_d=selff.env['hr.attendance'].search([('check_out','<=',selff.date_to),('check_in','>=',selff.date_from),('employee_id','=',selff.employee_id.id)])
            if horas_extr_d:
                for rec in horas_extr_d:
                    horas=horas+rec.worked_hours
                    dias_asis=dias_asis+1
            cantidad_horas_dia_permitida=selff.employee_id.contract_id.resource_calendar_id.hours_per_day
            total_horas_dias_permitidas=dias_asis*cantidad_horas_dia_permitida
            total_horas_extras=horas-total_horas_dias_permitidas
            if horas>total_horas_dias_permitidas:
                selff.horas_extras_diurnas=total_horas_extras
                selff.horas_extras_nocturnas=total_horas_extras


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

    def ano2(self,data):
        fecha = str(data)
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
