# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields,models,api,_
import datetime
from odoo.exceptions import UserError, ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    one_approve_by = fields.Many2one("res.users",string="Primer Aprobador")
    statu_one=fields.Selection(selection=[('approve','Aprobado'),('refuse','Rechazado'),('hold','En Espera')],default='hold')
    one_approve_time = fields.Datetime(string="Fecha de decisión", copy=False, index=True, track_visibility='onchange')
    two_approve_by = fields.Many2one("res.users",string="Segundo Aprobador")
    statu_two=fields.Selection(selection=[('approve','Aprobado'),('refuse','Rechazado'),('hold','En Espera')],default='hold')
    two_approve_time = fields.Datetime(string="Fecha de decisón", copy=False, index=True, track_visibility='onchange')
    state = fields.Selection(selection_add=[('draft','Quotation'),('sent','Quotation Sent'),('approve','Por Aprobar'),('approve2','Por Segunda Aprobación'),('approves','Aprobado'),('refuse','Rechazado'),('sale','Sales Order'),('done','Locked'),('cancel','Cancelled'),],
                               string='Status', readonly=False, copy=False, index=True, track_visibility='onchange', default='draft')

    def action_approve(self):
        self.state='approve'

    def action_approves(self):
        valida= self.env['sale.conf.approve'].search([('one_approve_by','=',self.env.user.id)])
        if not valida:
            raise UserError(_("Usted %s no esta autorizado para este tipo de aprobacion:")%self.env.user.partner_id.name)
        else:
            for det in valida:
                if det.one_approve_by:
                    self.state='approve2'
                    self.one_approve_by=self.env.user.id
                    self.one_approve_time=datetime.datetime.now()
                    self.statu_one='approve'
                

    def action_approve2(self):
        valida= self.env['sale.conf.approve'].search([('two_approve_by','=',self.env.user.id)])
        if not valida:
            raise UserError(_("Usted %s no esta autorizado para la aprobacion final:")%self.env.user.partner_id.name)
        else:
            for det in valida:
                if det.one_approve_by:
                    self.state='approves'
                    self.two_approve_by=self.env.user.id
                    self.two_approve_time=datetime.datetime.now()
                    self.statu_two='approve'
        #self.state='approves'

    def action_refuse(self):
        valida= self.env['sale.conf.approve'].search(['|',('two_approve_by','=',self.env.user.id),('one_approve_by','=',self.env.user.id)])
        if not valida:
            raise UserError(_("Usted %s no esta autorizado Rechazar esta orden:")%self.env.user.partner_id.name)
        else:
            for det in valida:
                if det.one_approve_by.id==self.env.user.id:
                    #raise UserError(_("hello moto:%s")%self.env.user.id)
                    self.one_approve_by=self.env.user.id
                    self.statu_one='refuse'
                    self.one_approve_time=datetime.datetime.now()
                    self.state='refuse'
                if det.two_approve_by.id==self.env.user.id:
                    #raise UserError(_("hello moto 2:%s")%self.env.user.id)
                    self.two_approve_by=self.env.user.id
                    self.statu_two='refuse'
                    self.two_approve_time=datetime.datetime.now()
                    self.state='refuse'

    def action_draft(self):
        res = super(SaleOrder,self).action_draft()
        self.statu_one='hold'
        self.statu_two='hold'
        return res

class PermisoSaleOrder(models.Model):
    _name="sale.conf.approve"
    _description="Configurar Personas que aprueban ordenes"
    
    name = fields.Char(string="Configuracion de Aprobaciones", default="Configuración de Aprobaciones")

    one_approve_by = fields.Many2one("res.users",string="Primer Aprobador")
    two_approve_by = fields.Many2one("res.users",string="Segundo Aprobador")