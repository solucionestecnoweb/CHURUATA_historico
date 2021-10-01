# -*- coding: utf-8 -*-

import logging
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


_logger = logging.getLogger('__name__')

"""class AccountMoveReversal(models.TransientModel):
   
    _name = 'account.move.reversal'
    _description = 'Account Move Reversal'


    def reverse_moves(self):
        super().reverse_moves()
        raise UserError(_(' DArrell Sojo y Angel sojo'))"""


class AccountMove(models.Model):
    _inherit = 'account.move'    

    vat_ret_id = fields.Many2one('vat.retention', string='VAT withheld', readonly="True", copy=False, help='VAT retention voucher')
    rif = fields.Char(compute='_concatena', string='RIF')
    #rif = fields.Char(related='partner_id.vat', string='RIF', store=True)

    @api.depends('partner_id')
    def _concatena(self):
        if self.partner_id.doc_type=="v":
            tipo_doc="V"
        if self.partner_id.doc_type=="e":
            #self.partner_id.doc_type="E"
            tipo_doc="E"
        if self.partner_id.doc_type=="g":
            tipo_doc="G"
        if self.partner_id.doc_type=="j":
            tipo_doc="J"
        if self.partner_id.doc_type=="p":
            tipo_doc="P"
        if self.partner_id.doc_type=="c":
            tipo_doc="C"
        if not self.partner_id.doc_type:
            tipo_doc="?"
        if not self.partner_id.vat:
            vat=str(00000000)
        else:
            vat=self.partner_id.vat
        self.rif=str(tipo_doc)+"-"+str(vat)

    # Main Function
    def action_post(self):
        super().action_post()
        # Acciones a realizar validar fechas contables en la factura
        # Verificar si existe el impuesto al iva (lo voy a crear y cargar en xml)
        # Verificar si la empresa como el cliente o proveedor son agentes de retencion
        
        # si es agente de retencion
        self.funcion_numeracion_fac()
        #raise UserError(_('tipo fact = %s')%self.type)
        if self.type=="out_invoice" or self.type=="out_refund" or self.type=="out_receipt":
            tipo_fact="cliente"
            if self.partner_id.ret_agent:
                ban=0
                ban=self.verifica_exento_iva()
                if ban>0:
                    self.action_create_vat_retention(tipo_fact)
                    id_vat_ret=self.vat_ret_id.id
                    self.actualiza_voucher(id_vat_ret,tipo_fact)

        if self.type=="in_invoice" or self.type=="in_refund" or self.type=="in_receipt":
            tipo_fact="proveedor"
            if self.company_id.confg_ret_proveedores=="c":
                if self.company_id.partner_id.ret_agent:
                    ban=0
                    ban=self.verifica_exento_iva()
                    if ban>0:
                        self.action_create_vat_retention(tipo_fact)
                        id_vat_ret=self.vat_ret_id.id
                        self.actualiza_voucher(id_vat_ret,tipo_fact) #self.asiento_retencion(self.id,id_vat_ret) #funtcion darrell
            if self.company_id.confg_ret_proveedores=="p":
                if self.partner_id.ret_agent:
                    ban=0
                    ban=self.verifica_exento_iva()
                    if ban>0:
                        self.action_create_vat_retention(tipo_fact)
                        id_vat_ret=self.vat_ret_id.id
                        self.actualiza_voucher(id_vat_ret,tipo_fact)


    def funcion_numeracion_fac(self):
        if self.type=="in_invoice":
            busca_correlativos = self.env['account.move'].search([('invoice_number','=',self.invoice_number_pro),('id','!=',self.id)])
            for det_corr in busca_correlativos:
                if det_corr.invoice_number:
                    raise UserError(_(' El valor :%s ya se uso en otro documento')%det_corr.invoice_number)

            busca_correlativos2 = self.env['account.move'].search([('invoice_ctrl_number','=',self.invoice_ctrl_number_pro),('id','!=',self.id)])
            for det_corr2 in busca_correlativos2:
                if det_corr2.invoice_ctrl_number:
                    raise UserError(_(' El nro de control :%s ya se uso en otro documento')%det_corr2.invoice_ctrl_number)
            
            self.invoice_number=self.invoice_number_pro
            self.invoice_ctrl_number=self.invoice_ctrl_number_pro
            partners='pro' # aqui si es un proveedor

        if self.type=="in_refund" or self.type=="in_receipt":
            busca_correlativos = self.env['account.move'].search([('invoice_number','=',self.refuld_number_pro),('id','!=',self.id)])
            for det_corr in busca_correlativos:
                if det_corr.invoice_number:
                    raise UserError(_(' El valor :%s ya se uso en otro documento')%det_corr.invoice_number)

            busca_correlativos2 = self.env['account.move'].search([('invoice_ctrl_number','=',self.refund_ctrl_number_pro),('id','!=',self.id)])
            for det_corr2 in busca_correlativos2:
                if det_corr2.invoice_ctrl_number:
                    raise UserError(_(' El nro de control :%s ya se uso en otro documento')%det_corr2.invoice_ctrl_number)
                    
            self.invoice_number=self.refuld_number_pro
            self.invoice_ctrl_number=self.refund_ctrl_number_pro
            partners='cli' # aqui si es un cliente

        if self.type=="out_invoice":
            if self.nr_manual==False:
                self.invoice_number_cli=self.get_invoice_number_cli()
                self.invoice_number=self.invoice_number_cli #self.get_invoice_number_cli()
                self.invoice_ctrl_number_cli=self.get_invoice_ctrl_number_cli()
                self.invoice_ctrl_number=self.invoice_ctrl_number_cli #self.get_invoice_ctrl_number_cli()
            else:
                self.invoice_number=self.invoice_number_cli
                self.invoice_ctrl_number=self.invoice_ctrl_number_cli

        if self.type=="out_refund":
            if self.nr_manual==False:
                self.refuld_number_cli=self.get_refuld_number_cli()
                self.invoice_number=self.refuld_number_cli #self.get_refuld_number_cli()
                self.refund_ctrl_number_cli=self.get_refuld_ctrl_number_cli()
                self.invoice_ctrl_number=self.refund_ctrl_number_cli #self.get_refuld_ctrl_number_cli()
            else:
                self.invoice_number=self.refuld_number_cli
                self.invoice_ctrl_number=self.refund_ctrl_number_cli

        if self.type=="out_receipt":
            if self.nr_manual==False:
                self.refuld_number_cli=self.get_refuld_number_pro()
                self.invoice_number=self.refuld_number_cli #self.get_refuld_number_cli()
                self.refund_ctrl_number_cli=self.get_refuld_ctrl_number_pro()
                self.invoice_ctrl_number=self.refund_ctrl_number_cli #self.get_refuld_ctrl_number_cli()
                #self.invoice_number=self.get_nro_cliente()
            else:
                self.invoice_number=self.refuld_number_cli
                self.invoice_ctrl_number=self.refund_ctrl_number_cli

    def action_create_vat_retention(self,tipo_factt):
        "This function created the VAT retention Voucher"

        # si existe una retencion lo logico es que no agregue otra
        #self.create_voucher() #quitar despues
        if self.vat_ret_id:
            if self.vat_ret_id.state == 'draft':
                pass
            #else:
            #    raise ValidatioError('The invoice already has an associated VAT retention')
        
        else:
            # Aqui puede ir tu funcion Darrel
            self.create_voucher(tipo_factt)
            # se crean los asientos
            #self.asiento_retencion(self.id)

    def conv_div_nac(self,valor):
        self.currency_id.id
        fecha_contable_doc=self.date
        monto_factura=self.amount_total
        valor_aux=0
        #raise UserError(_('moneda compañia: %s')%self.company_id.currency_id.id)
        if self.currency_id.id!=self.company_id.currency_id.id:
            tasa= self.env['res.currency.rate'].search([('currency_id','=',self.currency_id.id),('name','<=',self.date)],order="name asc")
            for det_tasa in tasa:
                if fecha_contable_doc>=det_tasa.name:
                    valor_aux=det_tasa.rate
            rate=round(1/valor_aux,2)  # LANTA
            #rate=round(valor_aux,2)  # ODOO SH
            resultado=valor*rate
        else:
            resultado=valor
        return resultado

    def create_voucher(self,tipo_facttt):
        retention = self.env['vat.retention']
        _logger.info("\n\n\n retention %s\n\n\n", retention)
        vals = {
            'rif': self.rif,
            'partner_id': self.partner_id.id,
            'accouting_date': self.date, #datetime.now(),
            'invoice_number': self.invoice_number,
            'invoice_id': self.id,
            #'amount_untaxed': self.amount_untaxed,
            #'retention_line_ids':  [(0, 0, values)],
            'type':self.type,
            #'partners':self.type,
        }
        ret = retention.create(vals)

        if tipo_facttt=="cliente":
            por_ret=self.partner_id.vat_retention_rate
            type_tax_use='sale'

        if tipo_facttt=="proveedor":
            if self.company_id.confg_ret_proveedores=="p":
                #raise UserError(_('proveedor'))
                por_ret=self.partner_id.vat_retention_rate
            if self.company_id.confg_ret_proveedores=="c":
                #raise UserError(_('compañia'))
                por_ret=self.company_id.partner_id.vat_retention_rate
            type_tax_use='purchase'

        #lista_movline = self.env['account.move.line'].search([('move_id','=',self.id)])
        lista_movline = self.invoice_line_ids
        #raise UserError(_('lista_movline = %s')%lista_movline)
        for det_mov_line in lista_movline:
            if det_mov_line.product_id:
                importe_base=det_mov_line.price_subtotal
                monto_total=det_mov_line.price_total
                monto_iva=(monto_total-importe_base)
                monto_retenido=(monto_iva*por_ret/100)
                #raise UserError(_('self.tax_ids = %s')%det_mov_line.tax_ids.id)
                ret_lines = self.env['vat.retention.invoice.line']
                values = {
                'name': self.name,
                'invoice_id': self.id,
                'move_id': self.id,
                'invoice_number': self.invoice_number,
                'amount_untaxed': self.conv_div_nac(importe_base),
                'retention_amount':self.conv_div_nac(monto_retenido),
                'amount_vat_ret':self.conv_div_nac(monto_iva),
                'retention_rate':por_ret,
                'retention_id':ret.id,
                'tax_id':det_mov_line.tax_ids.id,
                }
                """if monto_iva!=0:
                    ret_line = ret_lines.create(values)""" # codigo que excluye las lineas exentas
                ret_line = ret_lines.create(values) #  Codigo 2 este incluye las lineas exentas
        self.write({'vat_ret_id':ret.id})
        # NUEVO CODIGO
        self.unifica_alicuota_iguales_iva(type_tax_use)
        return ret

    # FUNCION LA CUAL TOMA LINEAS DE FACTURAS DE ALICUOTAS IGUALES Y LAS UNIFICA PARA SER UNA SOLA LINEA POR ALICUOTA EN LOS COMPROBANTES
    def unifica_alicuota_iguales_iva(self,type_tax_use):
        lista_impuesto = self.env['account.tax'].search([('type_tax_use','=',type_tax_use)])
        #raise UserError(_('lista_impuesto = %s')%lista_impuesto)
        for det_tax in lista_impuesto:
            #raise UserError(_('det_tax.id = %s')%det_tax.id)
            lista_mov_line = self.env['vat.retention.invoice.line'].search([('move_id','=',self.id),('tax_id','=',det_tax.id)])
            #raise UserError(_('lista_mov_line = %s')%lista_mov_line)
            amount_untaxed=0
            amount_vat_ret=0
            retention_amount=0
            if lista_mov_line:
                for det_mov_line in lista_mov_line:                
                    amount_untaxed=amount_untaxed+det_mov_line.amount_untaxed
                    amount_vat_ret=amount_vat_ret+det_mov_line.amount_vat_ret
                    retention_amount=retention_amount+det_mov_line.retention_amount

                    nombre=det_mov_line.name
                    #raise UserError(_('nombre1 = %s')%nombre)
                    retention_id=det_mov_line.retention_id.id
                    invoice_number=det_mov_line.invoice_number
                    rate=det_mov_line.retention_rate
                    move_id=det_mov_line.move_id.id
                    invoice_id=det_mov_line.invoice_id.id
                    tax_id=det_tax.id
                #raise UserError(_('nombre2 = %s')%nombre)
                lista_mov_line.unlink()
                move_obj = self.env['vat.retention.invoice.line']
                valor={
                'name':nombre,
                'retention_id':retention_id,
                'invoice_number':invoice_number,
                'retention_rate':rate,
                'move_id':move_id,
                'invoice_id':invoice_id,
                'tax_id':tax_id,
                'amount_untaxed':amount_untaxed,
                'amount_vat_ret':amount_vat_ret,
                'retention_amount':retention_amount,
                }
                move_obj.create(valor)


    def actualiza_voucher(self,ret_id,tipo_factt):
        
        id_factura=self.id # USAR        
        #imponible_base=self.amount_untaxed
        #impuesto_ret_id=self.partner_id.vat_tax_account_id.id # no USAR
        agente_ret=self.partner_id.ret_agent # USAR AQUI INDICA SI ES O NO AGENTE DE RETENCION
        if tipo_factt=="cliente":
            porcentaje_ret=self.partner_id.vat_retention_rate #usar para meterlo en la tabla vat.retention
            cuenta_ret_cobrar=self.partner_id.account_ret_receivable_id.id # USAR PARA COMPARAR CON EL CAMPO ACCOUNT_ID DE LA TABLA ACCOUNT_MOVE_LINE
            cuenta_ret_pagar = self.partner_id.account_ret_payable_id.id # USAR PARA COMPARAR CON EL CAMPO ACCOUNT_ID DE LA TABLA ACCOUNT_MOVE_LINE
            cuenta_clien_cobrar=self.partner_id.property_account_receivable_id.id
            cuenta_prove_pagar = self.partner_id.property_account_payable_id.id
        if tipo_factt=="proveedor":
            if self.company_id.confg_ret_proveedores=="c":
                porcentaje_ret=self.company_id.partner_id.vat_retention_rate #usar para meterlo en la tabla vat.retention
                cuenta_ret_cobrar=self.company_id.partner_id.account_ret_receivable_id.id # USAR PARA COMPARAR CON EL CAMPO ACCOUNT_ID DE LA TABLA ACCOUNT_MOVE_LINE
                cuenta_ret_pagar = self.company_id.partner_id.account_ret_payable_id.id # USAR PARA COMPARAR CON EL CAMPO ACCOUNT_ID DE LA TABLA ACCOUNT_MOVE_LINE
                cuenta_clien_cobrar=self.company_id.partner_id.property_account_receivable_id.id
                cuenta_prove_pagar = self.company_id.partner_id.property_account_payable_id.id
            if self.company_id.confg_ret_proveedores=="p":
                porcentaje_ret=self.partner_id.vat_retention_rate #usar para meterlo en la tabla vat.retention
                cuenta_ret_cobrar=self.partner_id.account_ret_receivable_id.id # USAR PARA COMPARAR CON EL CAMPO ACCOUNT_ID DE LA TABLA ACCOUNT_MOVE_LINE
                cuenta_ret_pagar = self.partner_id.account_ret_payable_id.id # USAR PARA COMPARAR CON EL CAMPO ACCOUNT_ID DE LA TABLA ACCOUNT_MOVE_LINE
                cuenta_clien_cobrar=self.partner_id.property_account_receivable_id.id
                cuenta_prove_pagar = self.partner_id.property_account_payable_id.id
        #raise UserError(_('id_factura = %s')%id_factura) 
        valor_iva=self.amount_tax # ya este valo ya no me sirve segun la nueva metodologia
        valor_ret=round(float(valor_iva*porcentaje_ret/100),2)
        valores=valor_ret
        #raise UserError(_('valor_iva = %s')%valor_iva)
        if self.type=="in_invoice":
        #if self.partner_id.supplier_rank!=0:
            partnerr='pro' # aqui si es un proveedor
            id_account=cuenta_ret_pagar
        if self.type=="out_refund":
            id_account=cuenta_ret_cobrar
        if self.type=="out_invoice":
        #if self.partner_id.customer_rank!=0:
            partnerr='cli' # aqui si es un cliente
            id_account=cuenta_ret_cobrar
        if self.type=="in_refund":
            id_account=cuenta_ret_pagar
        #raise UserError(_('id_factura = %s')%id_factura)
        retencion=self.amount_tax
        retencion=abs(retencion) # es el monto

        imponible_base=retencion # +valor_iva
        acum_base=0
        acum_rete=0
        lista_account_retention_line = self.env['vat.retention.invoice.line'].search([('retention_id','=',ret_id)])
        #raise UserError(_('lista_account_retention_line = %s')%valor_iva)
        for det_line_retention in lista_account_retention_line:
            acum_base=acum_base+det_line_retention.amount_vat_ret
            acum_rete=acum_rete+det_line_retention.retention_amount

            """self.env['vat.retention.invoice.line'].browse(det_line_retention.id).write({
                'retention_amount': valor_ret,
                'retention_rate':porcentaje_ret,
                'move_id':id_factura,
                'amount_vat_ret':valor_iva,
                })"""
        lista_account_retention = self.env['vat.retention'].search([('id','=',ret_id)])
        for det_retention in lista_account_retention:
            self.env['vat.retention'].browse(det_retention.id).write({
                'vat_retentioned': acum_rete,#valor_ret,
                'journal_id':self.journal_id.id,
                'amount_untaxed':acum_base, #imponible_base,
                'move_id':id_factura,
                'type':self.type,
                'voucher_delivery_date': self.date,
                'manual':False,
                })
        # PUNTO D
       

    def get_invoice_number_cli(self):
        '''metodo que crea el Nombre del asiento contable si la secuencia no esta creada, crea una con el
        nombre: 'l10n_ve_cuenta_retencion_iva'''

        self.ensure_one()
        SEQUENCE_CODE = 'l10n_ve_nro_factura_cliente'
        company_id = 1
        IrSequence = self.env['ir.sequence'].with_context(force_company=1)
        name = IrSequence.next_by_code(SEQUENCE_CODE)

        # si aún no existe una secuencia para esta empresa, cree una
        if not name:
            IrSequence.sudo().create({
                'prefix': 'FACT/',
                'name': 'Localización Venezolana Factura cliente %s' % 1,
                'code': SEQUENCE_CODE,
                'implementation': 'no_gap',
                'padding': 4,
                'number_increment': 1,
                'company_id': 1,
            })
            name = IrSequence.next_by_code(SEQUENCE_CODE)
        #self.invoice_number_cli=name
        return name

    def get_invoice_ctrl_number_cli(self):
        '''metodo que crea el Nombre del asiento contable si la secuencia no esta creada, crea una con el
        nombre: 'l10n_ve_cuenta_retencion_iva'''

        self.ensure_one()
        SEQUENCE_CODE = 'l10n_ve_nro_control_factura_cliente'
        company_id = 1
        IrSequence = self.env['ir.sequence'].with_context(force_company=1)
        name = IrSequence.next_by_code(SEQUENCE_CODE)

        # si aún no existe una secuencia para esta empresa, cree una
        if not name:
            IrSequence.sudo().create({
                'prefix': '00-',
                'name': 'Localización Venezolana nro control Factura cliente %s' % 1,
                'code': SEQUENCE_CODE,
                'implementation': 'no_gap',
                'padding': 4,
                'number_increment': 1,
                'company_id': 1,
            })
            name = IrSequence.next_by_code(SEQUENCE_CODE)
        #self.invoice_number_cli=name
        return name

    def get_refuld_number_cli(self):# nota de credito cliente
        '''metodo que crea el Nombre del asiento contable si la secuencia no esta creada, crea una con el
        nombre: 'l10n_ve_cuenta_retencion_iva'''

        self.ensure_one()
        SEQUENCE_CODE = 'l10n_ve_nro_factura_nota_credito_cliente'
        company_id = 1
        IrSequence = self.env['ir.sequence'].with_context(force_company=1)
        name = IrSequence.next_by_code(SEQUENCE_CODE)

        # si aún no existe una secuencia para esta empresa, cree una
        if not name:
            IrSequence.sudo().create({
                'prefix': 'NCC/',
                'name': 'Localización Venezolana Nota Credito Cliente %s' % 1,
                'code': SEQUENCE_CODE,
                'implementation': 'no_gap',
                'padding': 4,
                'number_increment': 1,
                'company_id': 1,
            })
            name = IrSequence.next_by_code(SEQUENCE_CODE)
        #self.refuld_number_cli=name
        return name

    def get_refuld_ctrl_number_cli(self):
        '''metodo que crea el Nombre del asiento contable si la secuencia no esta creada, crea una con el
        nombre: 'l10n_ve_cuenta_retencion_iva'''

        self.ensure_one()
        SEQUENCE_CODE = 'l10n_ve_nro_control_nota_credito_cliente'
        company_id = 1
        IrSequence = self.env['ir.sequence'].with_context(force_company=1)
        name = IrSequence.next_by_code(SEQUENCE_CODE)

        # si aún no existe una secuencia para esta empresa, cree una
        if not name:
            IrSequence.sudo().create({
                'prefix': '00-',
                'name': 'Localización Venezolana nro control Nota Credito Cliente %s' % 1,
                'code': SEQUENCE_CODE,
                'implementation': 'no_gap',
                'padding': 4,
                'number_increment': 1,
                'company_id': 1,
            })
            name = IrSequence.next_by_code(SEQUENCE_CODE)
        #self.refuld_number_cli=name
        return name

    def get_refuld_number_pro(self): #nota de debito Cliente
        '''metodo que crea el Nombre del asiento contable si la secuencia no esta creada, crea una con el
        nombre: 'l10n_ve_cuenta_retencion_iva'''

        self.ensure_one()
        SEQUENCE_CODE = 'l10n_ve_nro_factura_nota_debito_cliente'
        company_id = 1
        IrSequence = self.env['ir.sequence'].with_context(force_company=1)
        name = IrSequence.next_by_code(SEQUENCE_CODE)

        # si aún no existe una secuencia para esta empresa, cree una
        if not name:
            IrSequence.sudo().create({
                'prefix': 'NDC/',
                'name': 'Localización Venezolana Nota Debito Cliente %s' % 1,
                'code': SEQUENCE_CODE,
                'implementation': 'no_gap',
                'padding': 4,
                'number_increment': 1,
                'company_id': 1,
            })
            name = IrSequence.next_by_code(SEQUENCE_CODE)
        #self.refuld_number_pro=name
        return name

    def get_refuld_ctrl_number_pro(self):
        '''metodo que crea el Nombre del asiento contable si la secuencia no esta creada, crea una con el
        nombre: 'l10n_ve_cuenta_retencion_iva'''

        self.ensure_one()
        SEQUENCE_CODE = 'l10n_ve_nro_control_nota_debito_cliente'
        company_id = 1
        IrSequence = self.env['ir.sequence'].with_context(force_company=1)
        name = IrSequence.next_by_code(SEQUENCE_CODE)

        # si aún no existe una secuencia para esta empresa, cree una
        if not name:
            IrSequence.sudo().create({
                'prefix': '00-',
                'name': 'Localización Venezolana Nro control Nota debito cliente %s' % 1,
                'code': SEQUENCE_CODE,
                'implementation': 'no_gap',
                'padding': 4,
                'number_increment': 1,
                'company_id': 1,
            })
            name = IrSequence.next_by_code(SEQUENCE_CODE)
        #self.refuld_number_pro=name
        return name

    def _check_balanced(self):
        ''' Assert the move is fully balanced debit = credit.
        An error is raised if it's not the case.
        '''
        moves = self.filtered(lambda move: move.line_ids)
        if not moves:
            return

        # /!\ As this method is called in create / write, we can't make the assumption the computed stored fields
        # are already done. Then, this query MUST NOT depend of computed stored fields (e.g. balance).
        # It happens as the ORM makes the create with the 'no_recompute' statement.
        self.env['account.move.line'].flush(['debit', 'credit', 'move_id'])
        self.env['account.move'].flush(['journal_id'])
        self._cr.execute('''
            SELECT line.move_id, ROUND(SUM(debit - credit), currency.decimal_places)
            FROM account_move_line line
            JOIN account_move move ON move.id = line.move_id
            JOIN account_journal journal ON journal.id = move.journal_id
            JOIN res_company company ON company.id = journal.company_id
            JOIN res_currency currency ON currency.id = company.currency_id
            WHERE line.move_id IN %s
            GROUP BY line.move_id, currency.decimal_places
            HAVING ROUND(SUM(debit - credit), currency.decimal_places) != 0.0;
        ''', [tuple(self.ids)])

        query_res = self._cr.fetchall()
        if query_res:
            ids = [res[0] for res in query_res]
            sums = [res[1] for res in query_res]
            #raise UserError(_("Cannot create unbalanced journal entry. Ids: %s\nDifferences debit - credit: %s") % (ids, sums))

    def _reverse_moves(self, default_values_list=None, cancel=False):

        # CODIGO DARRELL  VALORES DE LA FACTURA A REVERSAR
        fact_org=self.invoice_number
        id_fact_org=self.id
        # FIN CODIGO DARRELL
        
        if not default_values_list:
            default_values_list = [{} for move in self]

        if cancel:
            lines = self.mapped('line_ids')
            # Avoid maximum recursion depth.
            if lines:
                lines.remove_move_reconcile()

        reverse_type_map = {
            'entry': 'entry',
            'out_invoice': 'out_refund',
            'out_refund': 'entry',
            'in_invoice': 'in_refund',
            'in_refund': 'entry',
            'out_receipt': 'entry',
            'in_receipt': 'entry',
        }

        move_vals_list = []
        for move, default_values in zip(self, default_values_list):
            default_values.update({
                'type': reverse_type_map[move.type],
                'reversed_entry_id': move.id,
            })
            move_vals_list.append(move._reverse_move_vals(default_values, cancel=cancel))
        
        reverse_moves = self.env['account.move'].create(move_vals_list)

        # CODOGO DARRELL AQUI BUSCA LA ID DE LA NUEVA FACTURA RECTIFICATIVA
        id_fact_rec=reverse_moves.id
        # FIN CODIGO DARRELL

        for move, reverse_move in zip(self, reverse_moves.with_context(check_move_validity=False)):
            # Update amount_currency if the date has changed.
            if move.date != reverse_move.date:
                for line in reverse_move.line_ids:
                    if line.currency_id:
                        line._onchange_currency()
            reverse_move._recompute_dynamic_lines(recompute_all_taxes=False)
        reverse_moves._check_balanced()

        # Reconcile moves together to cancel the previous one.
        """if cancel:
            reverse_moves.with_context(move_reverse_cancel=cancel).post()
            for move, reverse_move in zip(self, reverse_moves):
                accounts = move.mapped('line_ids.account_id') \
                    .filtered(lambda account: account.reconcile or account.internal_type == 'liquidity')
                for account in accounts:
                    (move.line_ids + reverse_move.line_ids)\
                        .filtered(lambda line: line.account_id == account and line.balance)\
                        .reconcile()"""

        # CODIGO DARRELL AQUI COLOCA EN EL CAMPO DE REFERENCIA LA FACTURA AFECTADA
        lista_move = self.env['account.move'].search([('id','=',id_fact_rec)])
        for det in lista_move:
            self.env['account.move'].browse(det.id).write({
                'ref': fact_org,
                })
        # FIN CODIGO DARRELL
        return reverse_moves

    def verifica_exento_iva(self):
        acum=0
        #raise UserError(_('self = %s')%self.id)
        puntero_move_line = self.env['account.move.line'].search([('move_id','=',self.id)])
        for det_puntero in puntero_move_line:
            acum=acum+det_puntero.tax_line_id.amount
        return acum
