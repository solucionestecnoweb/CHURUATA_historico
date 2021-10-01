# -*- coding: utf-8 -*-


import logging
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError




class ResumenAlicuotaTpv(models.Model):
    _name = 'pos.order.line.resumen'


    session_id=fields.Many2one('pos.session', ondelete='cascade')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    state=fields.Char()
    total_con_iva = fields.Float(string=' Total con IVA')
    total_base = fields.Float(string='Total Base Imponible')

    base_general = fields.Float(string='Total Base General')
    base_reducida = fields.Float(string='Total Base Reducida')
    base_adicional = fields.Float(string='Total Base General + Reducida')

    total_exento = fields.Float(string='Total Excento')
    alicuota_general = fields.Float(string='Alicuota General')
    alicuota_reducida = fields.Float(string='Alicuota Reducida')
    alicuota_adicional = fields.Float(string='Alicuota General + Reducida')

    retenido_general = fields.Float(string='retenido General')
    retenido_reducida = fields.Float(string='retenido Reducida')
    retenido_adicional = fields.Float(string='retenido General + Reducida')    

    #tax_id = fields.Many2one('account.tax', string='Tipo de Impuesto')

    total_valor_iva = fields.Float(string='Total IVA')

    tipo_doc = fields.Char()
    fecha_fact= fields.Datetime(string="Fecha Cierre")

    nro_doc = fields.Char(string="Nro de documentos")
    nro_doc_nc = fields.Char(string="Nro de nota credito")
    reg_maquina = fields.Char(string="Registro de Máquina Fiscal")
    nro_rep_z = fields.Char(string="Número Reporte Z")

    base_imponible_nc = fields.Float(string="Base Imponible NC")
    alicuota_nc =  fields.Float(string='Alicuota NC')
    total_nc= fields.Float(string="Total NC",default=0)
    fact_afectada = fields.Char()

class PosSession(models.Model):
    _inherit = 'pos.session'

    #stop_at = fields.Date(string='Closing Date', readonly=False, copy=False)

    def action_pos_session_closing_control(self):
        super().action_pos_session_closing_control()
        #self.asigna_nro_fact()
        nro_rep_z=self.suma_alicuota_iguales_iva()
        self.suma_alicuota_iguales_iva_devolucion(nro_rep_z)

    def conv_div_bs(self,valor):
        return valor


    def asigna_nro_fact(self):
        if self.config_id.ordenes_impr==True:
            lista_pos_order = self.env['pos.order'].search([('session_id','=',self.id),('status_impresora','=','si')],order="id asc")
        if self.config_id.ordenes_impr==False:
            lista_pos_order = self.env['pos.order'].search([('session_id','=',self.id)],order="id asc")
        for det in lista_pos_order:
            nro=nroc=0000
            if det.state=="done" and det.nro_fact_seniat==0:
                if det.amount_total>0:
                    nro=self.nro_factu_seniat()
                if det.amount_total<0:
                    nroc=self.nro_ncr_seniat()
            self.env['pos.order'].browse(det.id).write({
                'nro_fact_seniat': nro,#valor_ret,
                'nro_nc_seniat':nroc,
                })

    def nro_factu_seniat(self):
        '''metodo que crea el Nombre del asiento contable si la secuencia no esta creada, crea una con el
        nombre: 'l10n_ve_cuenta_retencion_iva'''

        self.ensure_one()
        nb_pos=self.config_id.name
        SEQUENCE_CODE = 'l10n_ve_nro_factura_seniat'+nb_pos
        company_id = self.env.company.id
        IrSequence = self.env['ir.sequence'].with_context(force_company=company_id)
        name = IrSequence.next_by_code(SEQUENCE_CODE)
        # si aún no existe una secuencia para esta empresa, cree una
        if not name:
            IrSequence.sudo().create({
                'prefix': '00',
                'name': 'Localización Venezolana Correlativo factura seniat %s' % nb_pos,
                'code': SEQUENCE_CODE,
                'implementation': 'no_gap',
                'padding': 4,
                'number_increment': 1,
                'company_id': company_id,
            })
            name = IrSequence.next_by_code(SEQUENCE_CODE)
        #self.invoice_number_cli=name
        #raise UserError(_('name:%s')%name)
        return name

    def nro_ncr_seniat(self):

        self.ensure_one()
        nb_pos=self.config_id.name
        SEQUENCE_CODE = 'l10n_ve_nro_nota_credito_seniat'+nb_pos
        company_id = self.env.company.id
        IrSequence = self.env['ir.sequence'].with_context(force_company=company_id)
        name = IrSequence.next_by_code(SEQUENCE_CODE)

        # si aún no existe una secuencia para esta empresa, cree una
        if not name:
            IrSequence.sudo().create({
                'prefix': '00',
                'name': 'Localización Venezolana Correlativo nota credito seniat %s' % nb_pos,
                'code': SEQUENCE_CODE,
                'implementation': 'no_gap',
                'padding': 4,
                'number_increment': 1,
                'company_id': company_id,
            })
            name = IrSequence.next_by_code(SEQUENCE_CODE)
        #self.invoice_number_cli=name
        return name

    def suma_alicuota_iguales_iva(self):
        type_tax_use='sale'
        lista_impuesto = self.env['account.tax'].search([('type_tax_use','=',type_tax_use)])
        base=0
        total=0
        total_impuesto=0
        total_exento=0
        alicuota_adicional=0
        alicuota_reducida=0
        alicuota_general=0
        base_general=0
        base_reducida=0
        base_adicional=0
        retenido_general=0
        retenido_reducida=0
        retenido_adicional=0
        valor_iva=0
        #raise UserError(_('lista_impuesto:%s')%lista_impuesto)
        for det_tax in lista_impuesto:
            tipo_alicuota=det_tax.aliquot
            if self.config_id.ordenes_impr==True:
                lin=self.env['pos.order.line'].search([('status_impresora','=','si')])
            if self.config_id.ordenes_impr==False:
                lin=self.env['pos.order.line'].search([])
            if lin:
                for det_lin in lin:
                    if det_lin.order_id.session_id.id==self.id:
                        alicuota_product=det_lin.tax_ids_after_fiscal_position.aliquot
                        if det_lin.tax_ids_after_fiscal_position.aliquot==False:
                            alicuota_product="exempt" # AQUI SIRVE SI AL PRODUCTO NO LE INDICARON EL TIPO DE ALICUOTA, ASUME QUE ES EXENTO
                        if tipo_alicuota==alicuota_product:
                            if det_lin.tipo=="venta":
                                base=base+det_lin.price_subtotal
                                total=total+det_lin.price_subtotal_incl
                                total_impuesto=total_impuesto+(det_lin.price_subtotal_incl-det_lin.price_subtotal)
                                if alicuota_product=="general":
                                    alicuota_general=alicuota_general+(det_lin.price_subtotal_incl-det_lin.price_subtotal)
                                    base_general=base_general+det_lin.price_subtotal
                                if alicuota_product=="reduced":
                                    alicuota_reducida=alicuota_reducida+(det_lin.price_subtotal_incl-det_lin.price_subtotal)
                                    base_reducida=base_reducida+det_lin.price_subtotal
                                if alicuota_product=="additional":
                                    alicuota_adicional=alicuota_adicional+(det_lin.price_subtotal_incl-det_lin.price_subtotal)
                                    base_adicional=base_adicional+det_lin.price_subtotal
                                if alicuota_product=="exempt":
                                    total_exento=total_exento+det_lin.price_subtotal
            #raise UserError(_('det_lin:%s')%det_lin)
        nro_rep_z=self.get_nro_rep_z()
        values={
            'total_con_iva':self.conv_div_bs(total),
            'total_base':self.conv_div_bs(base),
            'total_valor_iva':self.conv_div_bs(total_impuesto),
            'alicuota_general':self.conv_div_bs(alicuota_general),
            'base_general':self.conv_div_bs(base_general),
            'total_exento':self.conv_div_bs(total_exento),
            'alicuota_reducida':self.conv_div_bs(alicuota_reducida),
            'alicuota_adicional':self.conv_div_bs(alicuota_adicional),
            'base_adicional':self.conv_div_bs(base_adicional),
            'base_reducida':self.conv_div_bs(base_reducida),
            'session_id':self.id,
            'fecha_fact':self.stop_at,
            'reg_maquina':self.config_id.reg_maquina,
            'nro_rep_z':nro_rep_z,
            'nro_doc':self.rango_nro_factura(),
            'nro_doc_nc':self.rango_nro_nc()
            }
        self.env['pos.order.line.resumen'].create(values)
        return nro_rep_z

    def suma_alicuota_iguales_iva_devolucion(self,nro_rep_z):
        un_order=self.env['pos.order'].search([('tipo','=','devolucion')])
        #raise UserError(_('un_order:%s')%un_order)
        if un_order:
            for rec in un_order:
                type_tax_use='sale'
                lista_impuesto = self.env['account.tax'].search([('type_tax_use','=',type_tax_use)])
                base=0
                total=0
                total_impuesto=0
                total_exento=0
                alicuota_adicional=0
                alicuota_reducida=0
                alicuota_general=0
                base_general=0
                base_reducida=0
                base_adicional=0
                retenido_general=0
                retenido_reducida=0
                retenido_adicional=0
                valor_iva=0
                for det_tax in lista_impuesto:
                    tipo_alicuota=det_tax.aliquot
                    if self.config_id.ordenes_impr==True:
                        lin=self.env['pos.order.line'].search([('order_id','=',rec.id),('status_impresora','=','si'),('tipo','=','devolucion')])
                    if self.config_id.ordenes_impr==False:
                        lin=self.env['pos.order.line'].search([('order_id','=',rec.id),('tipo','=','devolucion')])
                    if lin:
                        #raise UserError(_('lin:%s')%lin)
                        for det_lin in lin:
                            if det_lin.order_id.session_id.id==self.id:
                                alicuota_product=det_lin.tax_ids_after_fiscal_position.aliquot
                                if det_lin.tax_ids_after_fiscal_position.aliquot==False:
                                    alicuota_product="exempt" # AQUI SIRVE SI AL PRODUCTO NO LE INDICARON EL TIPO DE ALICUOTA, ASUME QUE ES EXENTO
                                if tipo_alicuota==alicuota_product:
                                    base=base+det_lin.price_subtotal
                                    total=total+det_lin.price_subtotal_incl
                                    total_impuesto=total_impuesto+(det_lin.price_subtotal_incl-det_lin.price_subtotal)
                                    if alicuota_product=="general":
                                        alicuota_general=alicuota_general+(det_lin.price_subtotal_incl-det_lin.price_subtotal)
                                        base_general=base_general+det_lin.price_subtotal
                                    if alicuota_product=="reduced":
                                        alicuota_reducida=alicuota_reducida+(det_lin.price_subtotal_incl-det_lin.price_subtotal)
                                        base_reducida=base_reducida+det_lin.price_subtotal
                                    if alicuota_product=="additional":
                                        alicuota_adicional=alicuota_adicional+(det_lin.price_subtotal_incl-det_lin.price_subtotal)
                                        base_adicional=base_adicional+det_lin.price_subtotal
                                    if alicuota_product=="exempt":
                                        total_exento=total_exento+det_lin.price_subtotal

                values={
                
                'session_id':self.id,
                'fecha_fact':self.stop_at,
                'reg_maquina':self.config_id.reg_maquina,
                'nro_rep_z':nro_rep_z,
                #'nro_doc':self.rango_nro_factura(),
                'nro_doc_nc':rec.nro_nc_seniat,
                'base_imponible_nc':self.conv_div_bs(base),
                'alicuota_nc':self.conv_div_bs(total-base),
                'total_nc':self.conv_div_bs(total),
                'fact_afectada':self.fact_afectada(rec.id_order_afectado),
                }
                self.env['pos.order.line.resumen'].create(values)


    def fact_afectada(self,id_afectado):
        valor=0
        busca=self.env['pos.order'].search([('id','=',id_afectado)])
        if busca:
            for det in busca:
                valor=det.nro_fact_seniat
        return valor

    def rango_nro_factura(self):
        valor_ini=valor_fin=0
        lista_pos_order = self.env['pos.order']
        lista=lista_pos_order.search([('session_id','=',self.id),('amount_total','>',0)],order="id desc")
        lista2=lista_pos_order.search([('session_id','=',self.id),('amount_total','>',0)],order="id asc")
        for dett in lista:
            valor_ini=dett.nro_fact_seniat
        for det in lista2:
            valor_fin=det.nro_fact_seniat
        resultado="Desde "+str(valor_ini)+" Hasta "+str(valor_fin)
        return resultado

    def rango_nro_nc(self):
        valor_ini=valor_fin=0
        lista_pos_order = self.env['pos.order']
        if self.config_id.ordenes_impr==True:
            lista=lista_pos_order.search([('session_id','=',self.id),('amount_total','<',0),('status_impresora','=','si')],order="id desc")
        if self.config_id.ordenes_impr==False:
            lista=lista_pos_order.search([('session_id','=',self.id),('amount_total','<',0)],order="id desc")
        if self.config_id.ordenes_impr==True:
            lista2=lista_pos_order.search([('session_id','=',self.id),('amount_total','<',0),('status_impresora','=','si')],order="id asc")
        if self.config_id.ordenes_impr==False:
            lista2=lista_pos_order.search([('session_id','=',self.id),('amount_total','<',0)],order="id asc")
        for dett in lista:
            valor_ini=dett.nro_nc_seniat
        for det in lista2:
            valor_fin=det.nro_nc_seniat
        if valor_ini!=0:
            resultado="Desde "+str(valor_ini)+" Hasta "+str(valor_fin)
        if valor_ini==0:
            resultado="-----"
        return resultado

    def ejecuta_resumen(self):
        self.env['pos.order.line.resumen'].search([]).unlink()
        session = self.env['pos.session'].search([('state','=','closed')])
        #raise UserError(_('lista_session=%s')%lista_session)
        for selff in session:
            type_tax_use='sale'
            lista_impuesto = selff.env['account.tax'].search([('type_tax_use','=',type_tax_use)])
            base=0
            total=0
            total_impuesto=0
            total_exento=0
            alicuota_adicional=0
            alicuota_reducida=0
            alicuota_general=0
            base_general=0
            base_reducida=0
            base_adicional=0
            retenido_general=0
            retenido_reducida=0
            retenido_adicional=0
            valor_iva=0
            #raise UserError(_('lista_impuesto:%s')%lista_impuesto)
            for det_tax in lista_impuesto:
                tipo_alicuota=det_tax.aliquot
                if selff.config_id.ordenes_impr==True:
                    lin=selff.env['pos.order.line'].search([('status_impresora','=','si')])
                if selff.config_id.ordenes_impr==False:
                    lin=selff.env['pos.order.line'].search([])
                if lin:
                    for det_lin in lin:
                        if det_lin.order_id.session_id.id==selff.id:
                            alicuota_product=det_lin.tax_ids_after_fiscal_position.aliquot
                            if det_lin.tax_ids_after_fiscal_position.aliquot==False:
                                alicuota_product="exempt"
                            if tipo_alicuota==alicuota_product:
                                base=base+det_lin.price_subtotal
                                total=total+det_lin.price_subtotal_incl
                                total_impuesto=total_impuesto+(det_lin.price_subtotal_incl-det_lin.price_subtotal)
                                if alicuota_product=="general":
                                    alicuota_general=alicuota_general+(det_lin.price_subtotal_incl-det_lin.price_subtotal)
                                    base_general=base_general+det_lin.price_subtotal
                                if alicuota_product=="reduced":
                                    alicuota_reducida=alicuota_reducida+(det_lin.price_subtotal_incl-det_lin.price_subtotal)
                                    base_reducida=base_reducida+det_lin.price_subtotal
                                if alicuota_product=="additional":
                                    alicuota_adicional=alicuota_adicional+(det_lin.price_subtotal_incl-det_lin.price_subtotal)
                                    base_adicional=base_adicional+det_lin.price_subtotal
                                if alicuota_product=="exempt":
                                    total_exento=total_exento+det_lin.price_subtotal
                #raise UserError(_('det_lin:%s')%det_lin)
            values={
                'total_con_iva':total,
                'total_base':base,
                'total_valor_iva':total_impuesto,
                'alicuota_general':alicuota_general,
                'base_general':base_general,
                'total_exento':total_exento,
                'alicuota_reducida':alicuota_reducida,
                'alicuota_adicional':alicuota_adicional,
                'base_adicional':base_adicional,
                'base_reducida':base_reducida,
                'session_id':selff.id,
                'fecha_fact':selff.stop_at,
                'reg_maquina':selff.config_id.reg_maquina,
                'nro_rep_z':selff.get_nro_rep_z(),
                }
            selff.env['pos.order.line.resumen'].create(values)

    def get_nro_rep_z(self):
        '''metodo que crea el Nombre del asiento contable si la secuencia no esta creada, crea una con el
        nombre: 'l10n_ve_cuenta_retencion_iva'''

        self.ensure_one()
        nb_pos=self.config_id.name
        SEQUENCE_CODE = 'l10n_ve_nro_reporte_z_'+nb_pos
        company_id = self.env.company.id
        IrSequence = self.env['ir.sequence'].with_context(force_company=company_id)
        name = IrSequence.next_by_code(SEQUENCE_CODE)

        # si aún no existe una secuencia para esta empresa, cree una
        if not name:
            IrSequence.sudo().create({
                'prefix': 'ZZA',
                'name': 'Localización Venezolana Correlativo Reporte Z %s' % nb_pos,
                'code': SEQUENCE_CODE,
                'implementation': 'no_gap',
                'padding': 4,
                'number_increment': 1,
                'company_id': company_id,
            })
            name = IrSequence.next_by_code(SEQUENCE_CODE)
        #self.invoice_number_cli=name
        return name
