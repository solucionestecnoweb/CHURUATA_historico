# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Contract Aditional Data',
    'version': '1.1',
    'author': 'INM&RDL',
    'category': 'Human Resources',
    'sequence': 104,
    'summary': 'Adds aditional fields to hr_contract module',
    'description': '''
        Agrega los siguientes campos adicionales al contrato de los empleados:\n
            * Bono Nocturno\n
            * Dias de Sueldo Pendiente\n
            * Feriados\n
            * Feriados no Laborados\n
            * Horas extraordinarias Diurnas\n
            * Retroactivo de Sueldo\n
            * Aporte Patronal F.A.O.V.\n
            * Aporte Patronal  Fondo de Ahorro\n
            * Aporte Patronal P.I.E.\n
            * Aporte Patronal S.O.S.\n
            * Fondo de Caja de Ahorro\n
            * Horas no Laboradas\n
            * Inasistencias Injustificadas\n
            * Permiso no Remunerados Dias\n
            * Permiso no Remunerados Horas\n
            * Retenciones  F.A.O.V.\n
            * Retenciones Fondo de Ahorro\n
            * Retenciones I.S.L.R.\n
            * Retenciones P.I.E.\n
            * Retenciones  S.O.S.\n
    ''',
    'depends': [
        'base_setup',
        'base',
        'hr',
        'hr_contract',
        'hr_payroll',
        'hr_attendance',
        'hr_holidays',
        'l10n_ve_res_currency',
        'hr_holidays'
    ],
    'data': [
        'views/hr_contract_add_fields_view1.xml',
        'views/hr_special_days.xml',
        'views/hr_inherit_payslip_view.xml',
        'views/hr_vacation_days.xml',
        'views/hr_indicadores_economicos.xml',
        'views/hr_seting_inherit.xml',
        'views/hr_inherit_payroll_structure.xml',
        'views/hr_employee_inherit.xml',
        'views/hr_prestaciones.xml',
        'views/hr_incremento_view.xml',
        'views/hr_salary_rule_inherit.xml',
        'views/hr_leave_inherit.xml',
        'report/recibo_pago.xml',
        'report/recibo_vacaciones.xml',
        'report/recibo_liquidacion.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [],
}