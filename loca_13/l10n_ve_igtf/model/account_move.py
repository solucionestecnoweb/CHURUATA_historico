# -*- coding: utf-8 -*-
import logging

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError

class AccontPartialReconcile(models.Model):
    _inherit = "account.partial.reconcile"

    consi_secu_move_id=fields.Many2one('account.move', string='Asiento secundario de la factura')

class AccountMove(models.Model):
    _name = "account.move"
    _inherit = "account.move"

    #_rec_name = payment_id

    payment_id = fields.Many2one('account.payment', string='Anticipos Pendientes Bs.')
    monto_anticipo = fields.Monetary(string='Anticipo Disponible', compute='_compute_monto')
    payment_ids = fields.Many2many('account.payment', string='Anticipos')
    usar_anticipo = fields.Boolean(defaul=False)

    #rel_field = fields.Char(string='Name', related='payment_id.amount')

    def _compute_monto(self):
        self.monto_anticipo = self.payment_id.saldo_disponible
        #return monto_retencion

    def action_post(self):
        super().action_post()
        # Acciones a realizar validar fechas contables en la factura
        # Verificar si existe el impuesto al iva (lo voy a crear y cargar en xml)
        # Verificar si la empresa como el cliente o proveedor son agentes de retencion
        #if self.payment_id.id:
        if self.usar_anticipo==True:
            if not self.payment_ids:
                raise UserError(_('Debe agregar Lineas de Pagos de Anticipo'))
            cont=0
            acum=0
            for det in self.payment_ids:
                cont=cont+1
                acum=acum+det.saldo_disponible
                nombre_anti=self.get_name_anticipo()
                monto_factura=self.amount_residual #self.amount_total
                #if cont==2:
                    #raise UserError(_('monto_factura = %s')%monto_factura)
                #monto_anticipo=self.payment_id.amount
                monto_anticipo=det.saldo_disponible #*************
                id_move=self.registro_movimiento_anticipo(monto_anticipo,nombre_anti)
                idv_move=id_move.id
                valor=self.registro_movimiento_linea_anticipo(idv_move,monto_anticipo,nombre_anti,det,acum)
                moves= self.env['account.move'].search([('id','=',idv_move)])
                #self.valida_saldo_pendiente(det)
                moves.filtered(lambda move: move.journal_id.post_at != 'bank_rec').post()
                self.concilio_saldo_pendiente_anti(idv_move,det,cont,acum)
                cursor_payment = self.env['account.payment'].search([('id','=',det.id)])
                if monto_anticipo<monto_factura:
                    usuado=True
                    disponible=0.0
                if monto_anticipo>monto_factura:
                    usuado=False
                    disponible=(monto_anticipo-monto_factura)
                    self.invoice_payment_state='paid'
                if monto_anticipo==monto_factura:
                    usuado=True
                    disponible=0.0
                    self.invoice_payment_state='paid'
                #raise UserError(_('disponible = %s')%disponible)
                for det_payment in cursor_payment:
                    self.env['account.payment'].browse(det_payment.id).write({
                                'usado':usuado,
                                'anticipo_move_id':idv_move,
                                'saldo_disponible':disponible,
                                'move_id':self.id,
                                })
            #raise UserError(_('monto_anticipo = %s')%monto_anticipo)

    def registro_movimiento_anticipo(self,total_monto,anti_nombre):
        name = anti_nombre
        #raise UserError(_('monto xx = %s')%amount_itf)
        value = {
            'name': name,
            'date': self.date,
            'journal_id': self.journal_id.id,
            'line_ids': False,
            'state': 'draft',
            'type': 'entry',# estte campo es el que te deja cambiar y almacenar valores 
            'amount_total':total_monto,# revisar
            'amount_total_signed':total_monto,# revisar
            'partner_id': self.partner_id.id,
            #'partner_id': 45,
            'ref': "Pago de Anticipo Documento Nro: %s " % (self.name),
            #'name': "Comisión del %s %% del pago %s por comisión" % (igtf_porcentage,name),

        }
        if self.amount_residual>0:

            move_obj = self.env['account.move']
            move_id = move_obj.create(value)     
            return move_id
        else:
            move_id=self.env['account.move'].search([('id','=',0)])
            return move_id

    def registro_movimiento_linea_anticipo(self,id_movv,total_monto,anti_nombre,id_payment,acum_anti):
        cuenta_anti_cliente = self.partner_id.account_anti_receivable_id.id
        cuenta_anti_proveedor = self.partner_id.account_anti_payable_id.id
        cuenta_cobrar = self.partner_id.property_account_receivable_id.id
        cuenta_pagar = self.partner_id.property_account_payable_id.id
        tipo_persona=self.type

        factura_monto=self.amount_total #self.amount_total
        anticipo_monto=id_payment.saldo_disponible

        #residual=anticipo_monto  # funciona cuando el anticipor < factura

        if acum_anti<factura_monto:  #funciona cundo anticipo > factura
            residual=anticipo_monto
        if acum_anti>=factura_monto:
            residual=anticipo_monto+(factura_monto-acum_anti)

        """if anticipo_monto<=factura_monto:
            residual=anticipo_monto
        if anticipo_monto>factura_monto:
            residual=factura_monto"""

        #valores=total_monto
        valores=residual
        name = anti_nombre
        #raise UserError(_('tipo_persona = %s')%tipo_persona)
        if tipo_persona=="in_invoice":
            cuenta_a=cuenta_anti_proveedor
            cuenta_b=cuenta_pagar
        if tipo_persona=="out_invoice":
            cuenta_a=cuenta_cobrar
            cuenta_b=cuenta_anti_cliente
        #raise UserError(_('cuenta_a = %s')%cuenta_a)
        if self.amount_residual>0:
            value = {
                 'name': name,
                 'ref' : "Pago de Anticipo Documento Nro: %s " % (self.name),
                 'move_id': int(id_movv),
                 'date': self.date,
                 'partner_id': self.partner_id.id,
                 #'partner_id': 45,
                 'journal_id': self.journal_id.id,
                 'account_id': cuenta_a,# aqui va cuenta de anticipo 
                 'amount_currency': 0.0,
                 'date_maturity': False,
                 #'credit': float(amount_itf),
                 #'debit': 0.0,
                 'credit': valores,
                 'debit': 0.0, # aqi va cero
                 'balance':-valores,

            }
            

            move_line_obj = self.env['account.move.line']
            move_line_id1 = move_line_obj.create(value)

            value['account_id'] = cuenta_b # aqui va cuenta pxp proveedores
            value['credit'] = 0.0 # aqui va cero
            value['debit'] = valores
            value['balance'] = valores
            move_line_id2 = move_line_obj.create(value)


    def valida_saldo_pendiente(self,id_payment):
        factura_monto=self.amount_residual #self.amount_total
        anticipo_monto=id_payment.saldo_disponible
        if anticipo_monto<factura_monto:
            residual=(anticipo_monto-factura_monto)
        if anticipo_monto>=factura_monto:
            residual=0.0
        #raise UserError(_('residual:%s')%residual)
        cursor_move = self.env['account.move'].search([('id','=',self.id)])
        for det_mov in cursor_move:
            self.env['account.move'].browse(det_mov.id).write({
                            'amount_residual':-1*residual,
                            'amount_residual_signed':residual,
                            })
    
    def button_draft(self):
        super().button_draft()
        #raise UserError(_('Mi Bebe:%s')%self)
        # LINEA DE CODIGO QUE ELIMINA LAS CONSILIACIONES SECUNDARIAS DE ANTICIPO
        for selff in self:
            conciliacion=selff.env['account.partial.reconcile'].search([('consi_secu_move_id','=',selff.id)])
            #raise UserError(_('Mi Bebe:%s')%conciliacion)
            conciliacion.with_context(force_delete=True).unlink()
            # FIN LINEA DE CODIGO QUE ELIMINA LAS CONSILIACIONES SECUNDARIAS DE ANTICIPO

            monto_factura=selff.amount_total
            monto_residual=selff.amount_residual
            saldo_actual=selff.payment_id.saldo_disponible
            #saldo_inicial=monto_factura-monto_residual
            if selff.type!="entry":
                #raise UserError(_('Mi Bebe2:'))
                #raise UserError(_('Mi Bebe:%s')%self.payment_id.anticipo)
                #if self.payment_id.anticipo==True:
                cursor_payment = selff.env['account.payment'].search([('move_id','=',selff.id)])
                #raise UserError(_('Mi Bebe:%s')%cursor_payment)
                if cursor_payment:
                    for det_payment in cursor_payment:
                        id_mov_anti=det_payment.anticipo_move_id.id
                        #raise UserError(_('Mi Bebe:%s')%det_payment.amount)
                        saldo_inicial=det_payment.anticipo_move_id.amount_total+saldo_actual
                        selff.env['account.payment'].browse(det_payment.id).write({
                                        'usado':False,
                                        #'saldo_disponible':saldo_inicial,
                                        'saldo_disponible':det_payment.amount,
                                        })
                        cursor_anticipo = selff.env['account.move'].search([('id','=',id_mov_anti)])
                        #cursor_anticipo.filtered(lambda move: move.state == 'posted').button_draft()
                        cursor_anticipo.with_context(force_delete=True).unlink()


#************ funcionpara que funcione en lanta *************
    def concilio_saldo_pendiente_anti(self,id_move_conci,id_payment,cont2,acum_anti):
        #id_retention=self.id
        #raise UserError(_('yujuuuuu'))
        id_move=self.id
        #raise UserError(_('ID Factura=%s')%self.id)
        #raise UserError(_('id_move_conci=%s')%id_move_conci)
        factura_monto=self.amount_total #self.amount_total
        anticipo_monto=id_payment.saldo_disponible
        if acum_anti<factura_monto:
            monto=anticipo_monto
        if acum_anti>=factura_monto:
            monto=anticipo_monto+(factura_monto-acum_anti)
        #if cont2==3:
        #raise UserError(_('self.amount_residual = %s')%self.amount_residual)

        if self.amount_residual>0:

            tipo_empresa=self.type
            if tipo_empresa=="in_invoice" or tipo_empresa=="out_refund":#aqui si la empresa es un proveedor
                type_internal="payable"
            if tipo_empresa=="out_invoice" or tipo_empresa=="in_refund":# aqui si la empresa es un cliente
                type_internal="receivable"
            busca_movimientos = self.env['account.move'].search([('id','=',id_move)])
            for det_movimientos in busca_movimientos:
                busca_line_mov1 = self.env['account.move.line'].search([('move_id','=',id_move),('account_internal_type','=',type_internal),('parent_state','!=','cancel')])
                #raise UserError(_('busca_line_mov1 = %s')%busca_line_mov1)
                for det_line_move1 in busca_line_mov1:
                    if det_line_move1.credit==0:
                        id_move_debit=det_line_move1.id
                        monto_debit=det_line_move1.debit
                    if det_line_move1.debit==0:
                        id_move_credit=det_line_move1.id
                        monto_credit=det_line_move1.credit

                busca_line_mov2 = self.env['account.move.line'].search([('move_id','=',id_move_conci),('account_internal_type','=',type_internal),('parent_state','!=','cancel')])
                #raise UserError(_('busca_line_mov2 = %s')%busca_line_mov2)
                cont=0
                for det_line_move2 in busca_line_mov2:
                    cont=cont+1
                    if det_line_move1.debit==0:
                        if det_line_move2.credit==0:
                            id_move_debit=det_line_move2.id
                            monto_debit=det_line_move2.debit
                    if det_line_move1.credit==0:
                        if det_line_move2.debit==0:
                            id_move_credit=det_line_move2.id
                            monto_credit=det_line_move2.credit

                    #if det_line_move2.debit==0:
                        #id_move_credit=det_line_move2.id
                        #monto_credit=det_line_move2.credit
                    #if cont==2:
                        #pass
                        #raise UserError(_('cont=%s, det_line_move2.debit = %s')%(cont,det_line_move2.parent_state))

            #raise UserError(_('monto_credit = %s, monto_debit= %s ')%(monto_credit,monto_debit))       
            if tipo_empresa=="in_invoice" or tipo_empresa=="out_refund":
                monto=monto_debit
            if tipo_empresa=="out_invoice" or tipo_empresa=="in_refund":
                monto=monto_credit
            value = {
                 'debit_move_id':id_move_debit,
                 'credit_move_id':id_move_credit,
                 'amount':monto,
                 'max_date':self.date,
            }
            #raise UserError(_('value = %s')%value)
            self.env['account.partial.reconcile'].create(value)

            # NUEVO CODIGO PARA CONCILIAR MOVIMIENTOS SECUNDARIOS 
            id_payment.id
            busca_line_mov3 = self.env['account.move.line'].search([('payment_id','=',id_payment.id),('account_internal_type','=',type_internal),('parent_state','!=','cancel')])
            for det_line_move3 in busca_line_mov3:
                if det_line_move3.credit==0:
                    id_move_debit=det_line_move3.id
                    monto_debit=det_line_move3.debit
                if det_line_move3.debit==0:
                    id_move_credit=det_line_move3.id
                    monto_credit=det_line_move3.credit
            busca_line_mov4 = self.env['account.move.line'].search([('move_id','=',id_move_conci),('account_internal_type','=',type_internal),('parent_state','!=','cancel')])
            for det_line_move4 in busca_line_mov4:
                if det_line_move3.debit==0:
                    if det_line_move4.credit==0:
                        id_move_debit=det_line_move4.id
                        monto_debit=det_line_move4.debit
                if det_line_move3.credit==0:
                    if det_line_move4.debit==0:
                        id_move_credit=det_line_move4.id
                        monto_credit=det_line_move4.credit

            if tipo_empresa=="in_invoice" or tipo_empresa=="out_refund":
                monto=monto_debit
            if tipo_empresa=="out_invoice" or tipo_empresa=="in_refund":
                monto=monto_credit
            value = {
            'debit_move_id':id_move_debit,
            'credit_move_id':id_move_credit,
            'amount':monto,
            'max_date':self.date,
            'consi_secu_move_id':self.id,
            }
            self.env['account.partial.reconcile'].create(value)
            #raise UserError(_('value = %s')%self.env['account.partial.reconcile'].create(value))

#************ funcionpara que funcione en odoo sh *************
    """def concilio_saldo_pendiente_anti(self,id_move_conci,id_payment,cont2,acum_anti):
        #id_retention=self.id
        #raise UserError(_('yujuuuuu'))
        id_move=self.id
        factura_monto=self.amount_total #self.amount_total
        anticipo_monto=id_payment.saldo_disponible
        if acum_anti<factura_monto:
            monto=anticipo_monto
        if acum_anti>=factura_monto:
            monto=anticipo_monto+(factura_monto-acum_anti)
        #if cont2==3:
        #raise UserError(_('self.amount_residual = %s')%self.amount_residual)

        if self.amount_residual>0:

            tipo_empresa=self.type
            if tipo_empresa=="in_invoice" or tipo_empresa=="out_refund":#aqui si la empresa es un proveedor
                type_internal="payable"
            if tipo_empresa=="out_invoice" or tipo_empresa=="in_refund":# aqui si la empresa es cliente
                type_internal="receivable"
            busca_movimientos = self.env['account.move'].search([('id','=',id_move)])
            for det_movimientos in busca_movimientos:
                busca_line_mov = self.env['account.move.line'].search([('move_id','in',(det_movimientos.id,id_move_conci)),('account_internal_type','=',type_internal)])
                #raise UserError(_('busca_line_mov = %s')%busca_line_mov)
                for det_line_move in busca_line_mov:
                    if det_line_move.credit==0:
                        id_move_debit=det_line_move.id
                        monto_debit=det_line_move.debit
                    if det_line_move.debit==0:
                        id_move_credit=det_line_move.id
                        monto_credit=det_line_move.credit
            if tipo_empresa=="in_invoice" or tipo_empresa=="out_refund":
                monto=monto_debit
            if tipo_empresa=="out_invoice" or tipo_empresa=="in_refund":
                monto=monto_credit
            value = {
                 'debit_move_id':id_move_debit,
                 'credit_move_id':id_move_credit,
                 'amount':monto,
                 'max_date':self.date,
            }
            self.env['account.partial.reconcile'].create(value)"""

    def get_name_anticipo(self):
        '''metodo que crea el Nombre del asiento contable si la secuencia no esta creada, crea una con el
        nombre: 'l10n_account_withholding_itf'''

        self.ensure_one()
        SEQUENCE_CODE = 'l10n_ve_cuenta_anticipo'
        company_id = self.company_id
        IrSequence = self.env['ir.sequence'].with_context(force_company=company_id.id)
        name = IrSequence.next_by_code(SEQUENCE_CODE)

        # si aún no existe una secuencia para esta empresa, cree una
        if not name:
            IrSequence.sudo().create({
                'prefix': 'Anticipo/',
                'name': 'Localización Venezolana Pagos de anticipos %s' % company_id.id,
                'code': SEQUENCE_CODE,
                'implementation': 'no_gap',
                'padding': 8,
                'number_increment': 1,
                'company_id': company_id.id,
            })
            name = IrSequence.next_by_code(SEQUENCE_CODE)
        return name


    """def unlink(self):
        for move in self:
            if move.name != '/' and not self._context.get('force_delete'):
                raise UserError(_("hgghgh"))
            move.line_ids.unlink()
        return super(AccountMove, self).unlink()"""
 

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