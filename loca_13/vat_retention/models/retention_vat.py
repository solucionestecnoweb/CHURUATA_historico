# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


_logger = logging.getLogger('__name__')



class InvoiceLineInherit(models.Model):
    _inherit = 'account.move.line'

    retention_id = fields.Many2one('vat.retention', string='VAT Retention')


class VatRetentionTaxLines(models.Model):
    """This model is about tax withheld in a invoice."""
    _name = 'vat.retention.tax.lines'

    name = fields.Char(string='Tax name', size=40)
    tax_id = fields.Many2one('account.tax', string="Tax")
    company_id = fields.Many2one('res.company', string='Company')
    vat_ret_line_id = fields.Many2one('vat.retention.invoice.line', ondelete="cascade",string='vat_ret_line_id')
    base_tax = fields.Float(string='Base tax')
    tax_amount = fields.Float(string='Tax amount')
    amount_withheld = fields.Float(string='Amount withheld')



class VatRetentionInvoiceLine(models.Model):
    """This model is for a line invoices withholed."""
    _name = 'vat.retention.invoice.line'

    def formato_fecha(self):
        fecha = str(self.invoice_id.invoice_date)
        fecha_aux=fecha
        ano=fecha_aux[0:4]
        mes=fecha[5:7]
        dia=fecha[8:10]  
        resultado=dia+"/"+mes+"/"+ano
        return resultado

    def float_format(self,valor):
        #valor=self.base_tax
        if valor:
            result = '{:,.2f}'.format(valor)
            result = result.replace(',','*')
            result = result.replace('.',',')
            result = result.replace('*','.')
        else:
            result = "0,00"
        return result

    def valida_excento(self,id_tax,id_retention):
        tipo=self.tax_id.aliquot
        valor_excento=0
        cant_reduced=0
        cant_general=0
        cant_additional=0
        resultado=''
        lista_det = self.env['vat.retention.invoice.line'].search([('retention_id','=',self.retention_id.id)])
        for det in lista_det:
            if det.tax_id.amount==0:
                valor_excento=valor_excento+det.amount_untaxed

            if det.tax_id.aliquot=='reduced':
                cant_reduced=cant_reduced+1
            if det.tax_id.aliquot=='general':
                cant_general=cant_general+1
            if det.tax_id.aliquot=='additional':
                cant_additional=cant_additional+1

        if tipo=='general' and cant_general>0:
            resultado=str(self.float_format(valor_excento))
        if tipo=='reduced' and cant_reduced>0 and cant_general==0:
            resultado=str(self.float_format(valor_excento))
        if tipo=='additional' and cant_additional>0 and cant_reduced==0 and cant_general==0:
            resultado=str(self.float_format(valor_excento))

        return str(resultado)

 

    #@api.depends('amount_vat_ret', 'retention_rate')
    def _compute_amount_withheld(self):
        return 0
        """This function compute the VAT retention."""
        #amount = (self.amount_vat_ret * self.retention_rate) / 100
        #_logger.info('\n\n\n amount %s \n\n\n', amount)
        #self.retention_amount = amount
        #voucher = self.env['vat.retention'].search([('id', '=', self.retention_id.id)])
        #_logger.info("\n\n\n voucher %s\n\n\n",voucher)
        #voucher.vat_retentioned = amount
    


    name = fields.Char(string='Description')
    retention_id = fields.Many2one('vat.retention', string='Vat retention')
    amount_untaxed = fields.Float(string='Amount untaxed')

    invoice_number = fields.Char(string='Invoice number')
    amount_vat_ret = fields.Float(string='Amount tax')
    retention_amount = fields.Float(string='Retention', readonly=True, store=True)
    retention_rate = fields.Float(string='Rate', help="The retention rate can vary between 75% al 100% depending on the taxpayer.")
    
    move_id = fields.Many2one('account.move', string='Asiento')
    invoice_id = fields.Many2one('account.move', string='Invoice', ondelete='restrict', help="Retention invoice")

    tax_line_ids = fields.One2many('vat.retention.tax.lines', 'vat_ret_line_id', string='tax lines')
    #campo por agregar
    # tax_book_id = fields.Many2one('tax.book', string="Tax book")

    # campos a ser eliminados
    tax_id = fields.Many2one('account.tax', string='Tax')

    # sql constrain por agregar
    # _sql_constraints = [
    #     ('one_name', 'unique (invoice_id)', 'message')
    # ]




class RetentionVat(models.Model):
    """This is a main model for rentetion vat control."""
    _name = 'vat.retention'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    journal_id=fields.Char(string='journal_id')
    move_id = fields.Many2one('account.move', string='Id del movimiento')

    """def unlink(self):
        for vat in self:
            if vat.state=='posted':
                raise UserError(_("El comprobante de retencion IVA ya esta Publicado, No se puede eliminar"))
        return super(RetentionVat,self).unlink() """     

    def formato_fecha2(self):
        fecha = str(self.voucher_delivery_date)
        fecha_aux=fecha
        ano=fecha_aux[0:4]
        mes=fecha[5:7]
        dia=fecha[8:10]  
        resultado=dia+"/"+mes+"/"+ano
        return resultado

    def periodo(self):
        fecha = str(self.voucher_delivery_date)
        fecha_aux=fecha
        ano=fecha_aux[0:4]
        mes=fecha[5:7]
        dia=fecha[8:10]  
        resultado=ano+"-"+mes
        return resultado

    def float_format2(self,valor):
        #valor=self.base_tax
        if valor:
            result = '{:,.2f}'.format(valor)
            result = result.replace(',','*')
            result = result.replace('.',',')
            result = result.replace('*','.')
        else:
            result = "0,00"
        return result

    def doc_cedula(self,aux):
        #nro_doc=self.partner_id.vat
        busca_partner = self.env['res.partner'].search([('id','=',aux)])
        for det in busca_partner:
            tipo_doc=busca_partner.doc_type
            nro_doc=str(busca_partner.vat)
        nro_doc=nro_doc.replace('V','')
        nro_doc=nro_doc.replace('v','')
        nro_doc=nro_doc.replace('E','')
        nro_doc=nro_doc.replace('e','')
        nro_doc=nro_doc.replace('G','')
        nro_doc=nro_doc.replace('g','')
        nro_doc=nro_doc.replace('J','')
        nro_doc=nro_doc.replace('j','')
        nro_doc=nro_doc.replace('P','')
        nro_doc=nro_doc.replace('p','')
        nro_doc=nro_doc.replace('-','')
        
        if tipo_doc=="v":
            tipo_doc="V"
        if tipo_doc=="e":
            tipo_doc="E"
        if tipo_doc=="g":
            tipo_doc="G"
        if tipo_doc=="j":
            tipo_doc="J"
        if tipo_doc=="p":
            tipo_doc="P"
        resultado=str(tipo_doc)+"-"+str(nro_doc)
        return resultado
        #raise UserError(_('cedula: %s')%resultado)


    #@api.depends('retention_line_ids.retention_amount')
    def _amount_all(self):
        """ It shows total in this form view"""
        return 0
        #amount = 0
        #retention = 0
        #for invoice in self.retention_line_ids:
        #   amount += invoice.amount_untaxed
        #   retention += invoice.retention_amount
        #self.amount_untaxed = amount
        #self.vat_retentioned = retention

    @api.model
    def _type(self):
        """Return invoice type."""
        
        return self._context.get('type', 'in_refund')

    
    # CORRELATIVO Segun indicaciones del seniat
    name = fields.Char(string='Voucher number', default='New')
    # datos del proveedor
    partner_id = fields.Many2one('res.partner', string='Partner')
    rif = fields.Char(string='RIF')
    # datos de emision y entrega del comprobante
    accouting_date = fields.Date(string='Accounting date', help='Voucher generation date', readonly="True")
    voucher_delivery_date = fields.Date(string='Voucher delivery date')
    # datos de la factura
    invoice_id = fields.Many2one('account.move', string="Invoice")
    invoice_number = fields.Char(string='Invoice Number')
    invoice_ctrl_num = fields.Char(string='Invoice control number')

    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company)

    # retenciones aplicadas
    retention_line_ids = fields.One2many('vat.retention.invoice.line', 'retention_id', string='Retention')
    
    # totales
    amount_untaxed = fields.Float(string='Importe Base', help='This concept is tax base')
    vat_retentioned = fields.Float(string='VAT retentioned')

    #datos contables
    # journal_id = fields.Many2one('account.journal', string='Journal')
    currency_id = fields.Many2one('res.currency', string='Currency')
    account_id = fields.Many2one('account.account', string='Account')

    manual=fields.Boolean(default=True)
    
    line_ids = fields.One2many('account.move.line', 'retention_id', string='Invoice lines',
        copy=True, readonly=True,
        states={'draft': [('readonly', False)]})
    
    type = fields.Selection(selection=[
        ('out_invoice', 'Customer Invoice'),
        ('in_invoice','Supplier Invoince'),
        ('in_refund','Suplier Refund'),
        ('out_refund','Customer Refund'),
        ('in_receipt','Nota Debito cliente'),
        ('out_receipt','Nota Debito proveedor'),
        ], string="Type invoice", store=True, default=_type)

    # otra informacion
    state = fields.Selection(selection=[
            ('draft', 'Draft'),
            ('posted', 'Posted'),
            # ('done', 'Done'),
            ('cancel', 'Cancelled')
        ], string='Status', readonly=True, copy=False, tracking=True,
        default='draft')

    is_supplier = fields.Boolean(string='Supplier')
    is_customer = fields.Boolean(string='Customer')
    description = fields.Char(string="Description", help="Description about this voucher.")

    @api.onchange('partner_id')
    def _rif(self):
        if self.partner_id:
            _logger.info("\n\n\n RIF \n\n\n")
            self.rif = self.partner_id.vat
        else:
            self.rif = ''
    



    def action_cancel(self):
        if self.invoice_id.state == 'cancel':
            self.write({'state': 'cancel'})
        else:
            raise ValidationError("Debe cancelar primero la factura")

    #@api.model
    def cargar_fact(self):

        if not self.invoice_id.id:
            raise UserError(_(' Debe Seleccionar una Factura Interna'))
        if self.invoice_id.id:
            map_id = self.env['account.move'].search([('id','=',self.invoice_id.id)],order="id asc")
        #raise UserError(_(' map_id:%s')%map_id)
        #self.rif=map_id.name # ojo aqui esta la clave
        if not map_id.partner_id.ret_agent:
            raise UserError(_(' La empresa %s no esta configurada como agente de retencion iva')%map_id.partner_id.name)
        else:
            if map_id.vat_ret_id.id:
                raise UserError(_(' Esta Factura ya tiene asignado un comprobante de retencion'))
            if not map_id.vat_ret_id:
                acum_iva=0
                acum_mon_ret=0
                retention = self.env['vat.retention']
                self.rif=map_id.rif
                self.partner_id=map_id.partner_id.id
                self.accouting_date=datetime.now()
                self.voucher_delivery_date=datetime.now()
                self.invoice_number=map_id.invoice_number
                self.move_id= self.invoice_id.id,
                self.journal_id=self.invoice_id.journal_id.id
                self.type=self.invoice_id.type
                self.invoice_ctrl_num=self.invoice_id.invoice_ctrl_number
                self.manual=False
                lista_movline = self.env['account.move.line'].search([('move_id','=',self.invoice_id.id)])
                for det_mov_line in lista_movline:
                    importe_base=det_mov_line.price_subtotal
                    monto_total=det_mov_line.price_total

                    monto_iva=(monto_total-importe_base)
                    acum_iva=acum_iva+monto_iva

                    monto_retenido=(monto_iva*map_id.partner_id.vat_retention_rate/100)
                    acum_mon_ret=acum_mon_ret+monto_retenido

                    ret_lines = self.env['vat.retention.invoice.line']
                    values = {
                    'name': self.invoice_id.name,
                    'invoice_id': self.invoice_id.id,
                    'move_id': self.invoice_id.id,
                    'invoice_number': map_id.invoice_number,
                    'amount_untaxed': importe_base,
                    'retention_amount':monto_retenido,
                    'amount_vat_ret':monto_iva,
                    'retention_rate':map_id.partner_id.vat_retention_rate,
                    'retention_id':self.id,
                    'tax_id':det_mov_line.tax_ids.id,
                    }
                    if monto_iva!=0:
                        ret_line = ret_lines.create(values)
                self.amount_untaxed=acum_iva
                self.vat_retentioned=acum_mon_ret
                map_id.write({
                    'vat_ret_id':self.id,

                    })
    



    def action_posted(self):
        #raise UserError(_('ID MOVE = %s')%self)
        if not self.voucher_delivery_date:
            raise ValidationError("Debe establecer una fecha de entrega")
        
        self.state = 'posted'
        nombre_ret_iva = self.get_name()
        id_move=self.registro_movimiento_retencion(nombre_ret_iva)
        idv_move=id_move.id
        valor=self.registro_movimiento_linea_retencion(idv_move,nombre_ret_iva)
        
        moves= self.env['account.move'].search([('id','=',idv_move)])
        moves.filtered(lambda move: move.journal_id.post_at != 'bank_rec').post()
        #self.concilio_saldo_pendiente()
        

    def action_draft(self):
        #self.state = 'draft'
        for item in self:
            _logger.info("\n\n\n\n self %s \n\n\n\n", type(self))
            _logger.info("\n\n\n self %s \n\n\n", self)

    
    # @api.onchange('partner_id')
    def get_address_partner(self):
        location = ''
        streets = ''
        if self.partner_id:
            location = self._get_state_and_city()
            streets = self._get_streets()
        return (streets + " " + location)


    def _get_state_and_city(self):
        state = ''
        city = ''
        if self.partner_id.state_id:
            state = "Edo." + " " + str(self.partner_id.state_id.name or '')
            _logger.info("\n\n\n state %s \n\n\n", state)
        if self.partner_id.city:
            city = str(self.partner_id.city or '')
            # _logger.info("\n\n\n city %s\n\n\n", city)
        result = city + " " + state
        _logger.info("\n\n\n result %s \n\n\n", result)
        return  result 


    def _get_streets(self):
        street2 = ''
        av = ''
        if self.partner_id.street:
            av = str(self.partner_id.street or '')
        if self.partner_id.street2:
            street2 = str(self.partner_id.street2 or '')
        result = av + " " + street2
        return result

    def get_company_address(self):
        location = ''
        streets = ''
        if self.company_id:
            streets = self._get_company_street()
            location = self._get_company_state_city()
        _logger.info("\n\n\n street %s location %s\n\n\n", streets, location)
        return  (streets + " " + location)


    def _get_company_street(self):
        street2 = ''
        av = ''
        if self.company_id.street:
            av = str(self.company_id.street or '')
        if self.company_id.street2:
            street2 = str(self.company_id.street2 or '')
        result = av + " " + street2
        return result


    def _get_company_state_city(self):
        state = ''
        city = ''
        if self.company_id.state_id:
            state = "Edo." + " " + str(self.company_id.state_id.name or '')
            _logger.info("\n\n\n state %s \n\n\n", state)
        if self.company_id.city:
            city = str(self.company_id.city or '')
            _logger.info("\n\n\n city %s\n\n\n", city)
        result = city + " " + state
        _logger.info("\n\n\n result %s \n\n\n", result)
        return  result

   
    #def unlink(self):
        """Throw an exception if the retention voucher is not in cancel state."""
        #for voucher in self:
            #raise ValidationError(_("No se pueden eliminar comprobantes"))


    @api.model
    def create(self, vals):
        partners=vals['type']
        #partners=vals['partners']
        #del vals['partners']

        if vals.get('name', 'New') == 'New':
            _logger.info("\n\n\n vals.get.tpye %s \n\n\n", vals.get('type', 'in_invoice'))
            if partners=='in_invoice' or partners=='in_refund' or partners=='in_receipt':
                vals['name'] = self.env['ir.sequence'].next_by_code('purchase.vat.retention.voucher.number') or '/'
                _logger.info("\n\n\n vals[name] %s \n\n\n",vals['name'])
            else:
                vals['name']= '00000000'
        return super().create(vals)

    def conv_div_extranjera(self,valor):
        self.invoice_id.currency_id.id
        fecha_contable_doc=self.invoice_id.date
        monto_factura=self.invoice_id.amount_total
        valor_aux=0
        #raise UserError(_('moneda compañia: %s')%self.company_id.currency_id.id)
        if self.invoice_id.currency_id.id!=self.company_id.currency_id.id:
            tasa= self.env['res.currency.rate'].search([('currency_id','=',self.invoice_id.currency_id.id),('name','<=',self.invoice_id.date)],order="name asc")
            for det_tasa in tasa:
                if fecha_contable_doc>=det_tasa.name:
                    valor_aux=det_tasa.rate
            rate=round(1/valor_aux,2)  # LANTA
            #rate=round(valor_aux,2)  # ODOO SH
            resultado=valor/rate
        else:
            resultado=valor
        return resultado

    def registro_movimiento_retencion(self,consecutivo_asiento):
        #raise UserError(_('darrell = %s')%self.partner_id.vat_retention_rate)
        name = consecutivo_asiento
        signed_amount_total=0
        amont_totall=self.vat_retentioned #self.conv_div_extranjera(self.vat_retentioned)
        #amount_itf = round(float(total_monto) * float((igtf_porcentage / 100.00)),2)
        if self.type=="in_invoice" or self.type=="in_receipt":
            signed_amount_total=amont_totall
        if self.type=="out_invoice" or self.type=="out_receipt":
            signed_amount_total=(-1*amont_totall)

        if self.type=="out_invoice" or self.type=="out_refund" or self.type=="out_receipt":
            id_journal=self.partner_id.ret_jrl_id.id
            rate_valor=self.partner_id.vat_retention_rate
        if self.type=="in_invoice" or self.type=="in_refund" or self.type=="in_receipt":
            if self.company_id.confg_ret_proveedores=="c":
                id_journal=self.company_id.partner_id.ret_jrl_id.id
                rate_valor=self.company_id.partner_id.vat_retention_rate
            if self.company_id.confg_ret_proveedores=="p":
                id_journal=self.partner_id.ret_jrl_id.id
                rate_valor=self.partner_id.vat_retention_rate
        #raise UserError(_('papa = %s')%signed_amount_total)
        value = {
            'name': name,
            'date': self.move_id.date,#listo
            #'amount_total':self.vat_retentioned,# LISTO
            'partner_id': self.partner_id.id, #LISTO
            'journal_id':id_journal,
            'ref': "Retención del %s %% IVA de la Factura %s" % (rate_valor,self.move_id.name),
            #'amount_total':self.vat_retentioned,# LISTO
            #'amount_total_signed':signed_amount_total,# LISTO
            'type': "entry",# estte campo es el que te deja cambiar y almacenar valores
            'vat_ret_id': self.id,
            #'currency_id':self.invoice_id.currency_id.id,
        }
        #raise UserError(_('value= %s')%value)
        move_obj = self.env['account.move']
        move_id = move_obj.create(value)    
        #raise UserError(_('move_id= %s')%move_id) 
        return move_id

    def registro_movimiento_linea_retencion(self,id_movv,consecutivo_asiento):
        #raise UserError(_('ID MOVE = %s')%id_movv)
        name = consecutivo_asiento
        valores = self.vat_retentioned #self.conv_div_extranjera(self.vat_retentioned) #VALIDAR CONDICION
        #raise UserError(_('valores = %s')%valores)
        cero = 0.0
        if self.type=="out_invoice" or self.type=="out_refund" or self.type=="out_receipt":
            cuenta_ret_cliente=self.partner_id.account_ret_receivable_id.id# cuenta retencion cliente
            cuenta_ret_proveedor=self.partner_id.account_ret_payable_id.id#cuenta retencion proveedores
            cuenta_clien_cobrar=self.partner_id.property_account_receivable_id.id
            cuenta_prove_pagar = self.partner_id.property_account_payable_id.id
            rate_valor=self.partner_id.vat_retention_rate
        if self.type=="in_invoice" or self.type=="in_refund" or self.type=="in_receipt":
            if self.company_id.confg_ret_proveedores=="c":
                cuenta_ret_cliente=self.company_id.partner_id.account_ret_receivable_id.id# cuenta retencion cliente
                cuenta_ret_proveedor=self.company_id.partner_id.account_ret_payable_id.id#cuenta retencion proveedores
                cuenta_clien_cobrar=self.company_id.partner_id.property_account_receivable_id.id
                cuenta_prove_pagar = self.company_id.partner_id.property_account_payable_id.id
                rate_valor=self.company_id.partner_id.vat_retention_rate
            if self.company_id.confg_ret_proveedores=="p":
                cuenta_ret_cliente=self.partner_id.account_ret_receivable_id.id# cuenta retencion cliente
                cuenta_ret_proveedor=self.partner_id.account_ret_payable_id.id#cuenta retencion proveedores
                cuenta_clien_cobrar=self.partner_id.property_account_receivable_id.id
                cuenta_prove_pagar = self.partner_id.property_account_payable_id.id
                rate_valor=self.partner_id.vat_retention_rate

        tipo_empresa=self.move_id.type
        #raise UserError(_('papa = %s')%tipo_empresa)
        if tipo_empresa=="in_invoice" or tipo_empresa=="in_receipt":#aqui si la empresa es un proveedor
            cuenta_haber=cuenta_ret_proveedor
            cuenta_debe=cuenta_prove_pagar

        if tipo_empresa=="in_refund":
            cuenta_haber=cuenta_prove_pagar
            cuenta_debe=cuenta_ret_proveedor

        if tipo_empresa=="out_invoice" or tipo_empresa=="out_receipt":# aqui si la empresa es cliente
            cuenta_haber=cuenta_clien_cobrar
            cuenta_debe=cuenta_ret_cliente

        if tipo_empresa=="out_refund":
            cuenta_haber=cuenta_ret_cliente
            cuenta_debe=cuenta_clien_cobrar
        balances=cero-valores
        value = {
             'name': name,
             'ref' : "Retención del %s %% IVA de la Factura %s" % (rate_valor,self.move_id.name),
             'move_id': int(id_movv),
             'date': self.move_id.date,
             'partner_id': self.partner_id.id,
             'account_id': cuenta_haber,
             #'currency_id':self.invoice_id.currency_id.id,
             #'amount_currency': 0.0,
             #'date_maturity': False,
             'credit': valores,
             'debit': 0.0, # aqi va cero   EL DEBITO CUNDO TIENE VALOR, ES QUE EN ACCOUNT_MOVE TOMA UN VALOR
             'balance':-valores, # signo negativo
             'price_unit':balances,
             'price_subtotal':balances,
             'price_total':balances,

        }

        move_line_obj = self.env['account.move.line']
        move_line_id1 = move_line_obj.create(value)

        balances=valores-cero
        value['account_id'] = cuenta_debe
        value['credit'] = 0.0 # aqui va cero
        value['debit'] = valores
        value['balance'] = valores
        value['price_unit'] = balances
        value['price_subtotal'] = balances
        value['price_total'] = balances

        move_line_id2 = move_line_obj.create(value)

    def concilio_saldo_pendiente(self):
        id_retention=self.id
        tipo_empresa=self.move_id.type
        if tipo_empresa=="in_invoice" or tipo_empresa=="out_refund":#aqui si la empresa es un proveedor
            type_internal="payable"
        if tipo_empresa=="out_invoice" or tipo_empresa=="in_refund":# aqui si la empresa es cliente
            type_internal="receivable"
        busca_movimientos = self.env['account.move'].search([('vat_ret_id','=',id_retention)])
        for det_movimientos in busca_movimientos:
            busca_line_mov = self.env['account.move.line'].search([('move_id','=',det_movimientos.id),('account_internal_type','=',type_internal)])
            if busca_line_mov.credit==0:
                id_move_debit=busca_line_mov.id
                monto_debit=busca_line_mov.debit
            if busca_line_mov.debit==0:
                id_move_credit=busca_line_mov.id
                monto_credit=busca_line_mov.credit
        if tipo_empresa=="in_invoice" or tipo_empresa=="out_refund":
            monto=monto_debit
        if tipo_empresa=="out_invoice" or tipo_empresa=="in_refund":
            monto=monto_credit
        value = {
             'debit_move_id':id_move_debit,
             'credit_move_id':id_move_credit,
             'amount':monto,
             'max_date':self.accouting_date,
        }
        self.env['account.partial.reconcile'].create(value)

        #raise UserError(_('concilia = %s')%busca_movimientos)

    def get_name(self):
        '''metodo que crea el Nombre del asiento contable si la secuencia no esta creada, crea una con el
        nombre: 'l10n_ve_cuenta_retencion_iva'''

        self.ensure_one()
        SEQUENCE_CODE = 'l10n_ve_cuenta_retencion_iva'
        company_id = 1
        IrSequence = self.env['ir.sequence'].with_context(force_company=1)
        name = IrSequence.next_by_code(SEQUENCE_CODE)

        # si aún no existe una secuencia para esta empresa, cree una
        if not name:
            IrSequence.sudo().create({
                'prefix': 'RET_IVA/',
                'name': 'Localización Venezolana Retenciones IVA %s' % 1,
                'code': SEQUENCE_CODE,
                'implementation': 'no_gap',
                'padding': 8,
                'number_increment': 1,
                'company_id': 1,
            })
            name = IrSequence.next_by_code(SEQUENCE_CODE)
        return name


    