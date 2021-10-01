# -*- coding: utf-8 -*-

import logging
from datetime import datetime, date
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger("__name__")


class PeriodMonth(models.Model):
    _name = 'period.month'
    _rec_name = 'months_number'

    name = fields.Char(string='Months')
    months_number = fields.Char(string='Number')


class PeriodYear(models.Model):
    _name = 'period.year'

    name = fields.Char(string='year')


class MuniWhConcept(models.Model):
    _name = 'muni.wh.concept'

    name = fields.Char(string="Description", required=True)
    code = fields.Char(string='Activity code', required=True)
    aliquot = fields.Float(string='Aliquot', required=True)
    month_ucim = fields.Char(string='UCIM per month')
    year_ucim = fields.Char(string='UCIM per year')



class MunicipalityTaxLine(models.Model):
    _name = 'municipality.tax.line'

    concept_id = fields.Many2one('muni.wh.concept', string="Retention concept", Copy=False)
    code = fields.Char(string='Activity code', store=True)
    aliquot = fields.Float(string='Aliquot')
    base_tax = fields.Float(string='Base Tax')
    wh_amount = fields.Float(compute="_compute_wh_amount", string='Withholding Amount', store=True)
    type = fields.Selection(selection=[('purchase', 'Purchase'), ('service', 'Service'), ('dont_apply','Does not apply')],string='Type of transaction')
    municipality_tax_id = fields.Many2one('municipality.tax', string='Municipality')
    move_id = fields.Many2one(string='Account entry')
    invoice_id = fields.Many2one('account.move', string='Invoice')
    invoice_date = fields.Date(string="Invoice Date")
    invoice_number = fields.Char(string="Invoice Number")
    invoice_ctrl_number = fields.Char(string="Invoice Control Number")

    def float_format(self,valor):
        #valor=self.base_tax
        if valor:
            result = '{:,.2f}'.format(valor)
            result = result.replace(',','*')
            result = result.replace('.',',')
            result = result.replace('*','.')
        else:
        	result="0,00"
        return result


    """@api.depends('base_tax', 'aliquot')
    def _compute_wh_amount(self):
        # for line in self.act_code_ids:
        # if self.base_tax and self.aliquot:
        _logger.info("\n\n\n\n Se esta realizando el calculo \n\n\n\n")
        retention = ((self.base_tax * self.aliquot) / 100)
        _logger.info("\n\n\n retention %s\n\n\n", retention)
        self.wh_amount = retention
        muni_tax = self.env['municipality.tax'].browse(self.municipality_tax_id.id)
        withheld_amount = self.base_tax
        amount = retention
        if muni_tax:
            muni_tax.write({'withheld_amount': withheld_amount, 'amount': retention})"""

    @api.depends('base_tax', 'aliquot')
    def _compute_wh_amount(self):
        # for line in self.act_code_ids:
        # if self.base_tax and self.aliquot:
        withheld_amount=0
        amount=0
        for item in self:        
            _logger.info("\n\n\n\n Se esta realizando el calculo \n\n\n\n")
            retention = ((item.base_tax * item.aliquot) / 100)
            _logger.info("\n\n\n retention %s\n\n\n", retention)
            item.wh_amount = retention
            muni_tax = self.env['municipality.tax'].browse(item.municipality_tax_id.id)
            #withheld_amount = item.base_tax
            #amount = amount+retention
            withheld_amount = withheld_amount+item.base_tax # correccion darrell se transformo en acumulador
            amount = amount+item.wh_amount # correccion darrell se transformo en acumulador
            if muni_tax:
                muni_tax.write({'withheld_amount': withheld_amount, 'amount': amount})
                #muni_tax.write({'withheld_amount': withheld_amount, 'amount': retention})


class MUnicipalityTax(models.Model):
    _name = 'municipality.tax'

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

    def float_format2(self,valor):
        #valor=self.base_tax
        if valor:
            result = '{:,.2f}'.format(valor)
            result = result.replace(',','*')
            result = result.replace('.',',')
            result = result.replace('*','.')
        else:
        	result="0,00"
        return result


    @api.model
    def _type(self):
        """Return invoice type."""
        origin = self._context.get('type') 
        if self._context.get('type'):
            return self._context.get('type')


    name = fields.Char(string='Voucher number', default='New')
    state = fields.Selection(selection=[
            ('draft', 'Draft'),
            ('posted', 'Posted'),
            ('cancel', 'Cancelled')
        ], string='Status', readonly=True, copy=False, tracking=True,
        default='draft')
    transaction_date = fields.Date(string='Transacción Date', default=datetime.now())
    #period fields
    date_start = fields.Many2one('period.month', string='Date start')
    date_end = fields.Many2one('period.year', string='Date end')
    rif = fields.Char(string='RIF')
    #rif = fields.Char(related='invoice_id.rif',string='RIF')
    # address
    address = fields.Char(compute="_get_address", string='Address')
    # partner data
    partner_id = fields.Many2one('res.partner', string='Partner')
    act_code_ids = fields.One2many('municipality.tax.line', 'municipality_tax_id', string='Activities code')
    # campos de ubicacion politico territorial
    city = fields.Char(string='City')
    state_id = fields.Many2one('res.country.state', string='State', tracking=True)
    municipality_id = fields.Many2one('res.country.state.municipality', string='Municipality')
    invoice_id = fields.Many2one('account.move', string='Invoice')
    amount = fields.Float(string='Amount')
    withheld_amount = fields.Float(string='Withheld Amount')
    type = fields.Selection(selection=[
        ('out_invoice', 'Customer Invoice'),
        ('in_invoice','Supplier Invoince'),
        ('in_refund','Suplier Refund'),
        ('out_refund','Customer Refund'),
        ('in_receipt','Nota Debito cliente'),
        ('out_receipt','Nota Debito proveedor'),
        ], string="Type invoice", store=True, default=_type)
    
    # We need this field for the reports
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company)
    move_id = fields.Many2one('account.move', string='Id del movimiento')
    invoice_number=fields.Char(string='Nro de Factura')

    #@api.depends('invoice_id')
    def _factura_prov_cli(self):
    	self.invoice_number="...."
        #factura= self.env['account.move'].search([('name','=',self.invoice_id.id)])
        #for det in factura:
            #invoice_number=det.invoice_number
        #self.invoice_number= str(invoice_number)

    @api.onchange('partner_id')
    def _rif(self):
        if self.partner_id:
            #self.rif = self.partner_id.vat
            self.rif = str(self.partner_id.doc_type)+"-"+str(self.partner_id.vat)


    @api.depends('partner_id')
    def _get_address(self):
        location = ''
        streets = ''
        if self.partner_id:
            location = self._get_state_and_city()
            streets = self._get_streets()
            self.address = streets + " " + location
        else:
            self.address = ''


    def _get_state_and_city(self):
        state = ''
        city = ''
        if self.partner_id.state_id:
            state = "Edo." + " " + str(self.partner_id.state_id.name or '')
        if self.partner_id.city:
            city = str(self.partner_id.city or '')
        result = city + " " + state
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
        if self.company_id.city:
            city = str(self.company_id.city or '')
        result = city + " " + state
        return  result



    def action_post(self):
       """Confirmed the municipal retention voucher."""
       if not self.transaction_date:
            raise ValidationError("Debe establecer una fecha de Transacción")
       self.state = 'posted'
       nombre_ret_municipal = self.get_name()
       id_move=self.registro_movimiento_retencion(nombre_ret_municipal)
       idv_move=id_move.id
       valor=self.registro_movimiento_linea_retencion(idv_move,nombre_ret_municipal)
       moves= self.env['account.move'].search([('id','=',idv_move)])
       moves.filtered(lambda move: move.journal_id.post_at != 'bank_rec').post()


    def action_cancel(self):
        self.state = 'cancel'



    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            _logger.info("\n\n\n vals.get.tpye %s \n\n\n", vals.get('type', 'in_invoice'))
            #if vals.get('type', 'in_invoice') == 'in_invoice':
            #raise UserError(_('TIPO yy = %s')%vals['type'])
            if vals['type']=="in_invoice" or vals['type']=="in_refund" or vals['type']=="in_receipt":
                    vals['name'] = self.env['ir.sequence'].next_by_code('purchase.muni.wh.voucher.number') or '/'
                    _logger.info("\n\n\n vals[name] %s \n\n\n",vals['name'])
            else:
                #vals['name'] = '/'
                vals['name'] = '00000000'
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
        name = consecutivo_asiento
        signed_amount_total=0
        #raise UserError(_('self.move_id.name = %s')%self.invoice_id.name)
        if self.type=="in_invoice":
            signed_amount_total=self.amount #self.conv_div_extranjera(self.amount)
        if self.type=="out_invoice":
            signed_amount_total=-1*self.amount #(-1*self.conv_div_extranjera(self.amount))

        if self.type=="out_invoice" or self.type=="out_refund" or self.type=="out_receipt":
            id_journal=self.partner_id.purchase_jrl_id.id
        if self.type=="in_invoice" or self.type=="in_refund" or self.type=="in_receipt":
            if self.company_id.confg_ret_proveedores=="c":
                id_journal=self.company_id.partner_id.purchase_jrl_id.id
            if self.company_id.confg_ret_proveedores=="p":
                id_journal=self.partner_id.purchase_jrl_id.id

        value = {
            'name': name,
            'date': self.transaction_date,#listo
            #'amount_total':self.vat_retentioned,# LISTO
            'partner_id': self.partner_id.id, #LISTO
            'journal_id':id_journal,
            'ref': "Retencion del Impuesto Municipal de la Factura %s" % (self.invoice_id.name),
            #'amount_total':self.vat_retentioned,# LISTO
            #'amount_total_signed':signed_amount_total,# LISTO
            'type': "entry",# estte campo es el que te deja cambiar y almacenar valores
            'wh_muni_id': self.id,
        }
        move_obj = self.env['account.move']
        move_id = move_obj.create(value)    
        return move_id


    def registro_movimiento_linea_retencion(self,id_movv,consecutivo_asiento):
        name = consecutivo_asiento
        valores = self.amount #self.conv_div_extranjera(self.amount) #VALIDAR CONDICION
        cero = 0.0
        if self.type=="out_invoice" or self.type=="out_refund" or self.type=="out_receipt":
            cuenta_ret_cliente=self.partner_id.account_ret_muni_receivable_id.id# cuenta retencion cliente
            cuenta_ret_proveedor=self.partner_id.account_ret_muni_payable_id.id#cuenta retencion proveedores
            cuenta_clien_cobrar=self.partner_id.property_account_receivable_id.id
            cuenta_prove_pagar = self.partner_id.property_account_payable_id.id

        if self.type=="in_invoice" or self.type=="in_refund" or self.type=="in_receipt":
            if self.company_id.confg_ret_proveedores=="c":
                cuenta_ret_cliente=self.company_id.partner_id.account_ret_muni_receivable_id.id# cuenta retencion cliente
                cuenta_ret_proveedor=self.company_id.partner_id.account_ret_muni_payable_id.id#cuenta retencion proveedores
                cuenta_clien_cobrar=self.company_id.partner_id.property_account_receivable_id.id
                cuenta_prove_pagar = self.company_id.partner_id.property_account_payable_id.id
            if self.company_id.confg_ret_proveedores=="p":
                cuenta_ret_cliente=self.partner_id.account_ret_muni_receivable_id.id# cuenta retencion cliente
                cuenta_ret_proveedor=self.partner_id.account_ret_muni_payable_id.id#cuenta retencion proveedores
                cuenta_clien_cobrar=self.partner_id.property_account_receivable_id.id
                cuenta_prove_pagar = self.partner_id.property_account_payable_id.id

        tipo_empresa=self.type
        #raise UserError(_('darrell = %s')%tipo_empresa)
        if tipo_empresa=="in_invoice" or tipo_empresa=="in_receipt":#aqui si la empresa es un proveedor
            cuenta_haber=cuenta_ret_proveedor
            cuenta_debe=cuenta_prove_pagar
            #raise UserError(_(' pantalla 1'))
            #raise UserError(_('cuentas = %s')%cuenta_debe)

        if tipo_empresa=="in_refund":
            cuenta_haber=cuenta_prove_pagar
            cuenta_debe=cuenta_ret_proveedor
            #raise UserError(_(' pantalla 2'))

        if tipo_empresa=="out_invoice" or tipo_empresa=="out_receipt":# aqui si la empresa es cliente
            cuenta_haber=cuenta_clien_cobrar
            cuenta_debe=cuenta_ret_cliente
            #raise UserError(_(' pantalla 3'))

        if tipo_empresa=="out_refund":
            cuenta_haber=cuenta_ret_cliente
            cuenta_debe=cuenta_clien_cobrar
            #raise UserError(_(' pantalla 4'))
        balances=cero-valores
        #raise UserError(_('cuenta = %s')%cuenta_ret_cliente)
        value = {
             'name': name,
             'ref' : "Retencion Impuesto Municipal de la Factura %s" % (self.invoice_id.name),
             'move_id': int(id_movv),
             'date': self.transaction_date,
             'partner_id': self.partner_id.id,
             'account_id': cuenta_haber,
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



    def get_name(self):
        '''metodo que crea el Nombre del asiento contable si la secuencia no esta creada, crea una con el
        nombre: 'l10n_ve_cuenta_retencion_iva'''

        self.ensure_one()
        SEQUENCE_CODE = 'l10n_ve_cuenta_retencion_municipal'
        company_id = 1
        IrSequence = self.env['ir.sequence'].with_context(force_company=1)
        name = IrSequence.next_by_code(SEQUENCE_CODE)

        # si aún no existe una secuencia para esta empresa, cree una
        if not name:
            IrSequence.sudo().create({
                'prefix': 'RET_MUN/',
                'name': 'Localización Venezolana Retenciones Municipales %s' % 1,
                'code': SEQUENCE_CODE,
                'implementation': 'no_gap',
                'padding': 8,
                'number_increment': 1,
                'company_id': 1,
            })
            name = IrSequence.next_by_code(SEQUENCE_CODE)
        return name
