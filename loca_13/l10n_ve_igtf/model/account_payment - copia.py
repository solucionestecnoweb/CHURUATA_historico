# coding: utf-8
###########################################################################

import logging

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError

#_logger = logging.getLogger(__name__)
class account_payment(models.Model):
    _name = 'account.payment'
    _inherit = 'account.payment'

    move_itf_id = fields.Many2one('account.move', 'Asiento contable')


    def button_organizar_ref(self):        

        company_id=self._get_company().id
        lista_company=self.env['res.company'].search([('id','=',company_id)])
        for det_company in lista_company:
            porcentage_igtf=det_company.wh_porcentage
            cuenta_igtf=det_company.account_wh_itf_id
            habilita_igtf=det_company.calculate_wh_itf

        if habilita_igtf==True:
            lista_pago= self.env['account.payment'].search([('id','=',4)])
            for det_pago in lista_pago:
                id_pago=det_pago.id
                move_name=det_pago.move_name
                tipo_pago=det_pago.payment_type
                if tipo_pago=='outbound':
                     lista_move= self.env['account.move'].search([('name','=',move_name)])
                     for det_move in lista_move:
                        monto_total=det_move.amount_total
                        state=det_move.state
                        date=det_move.date
                     id_move=self.registro_movimiento_pago(porcentage_igtf,monto_total)
                     idv_move=id_move.id
                     valor=self.registro_movimiento_linea_pago(porcentage_igtf,idv_move,monto_total)
                if tipo_pago!='outbound':
                     raise UserError(_('No se puede generar este Asiento.Solo sirve para tipo de pagos Envviar Dinero'))

        if habilita_igtf==False:
            raise UserError(_('La compañia no esta habilitada para hacer Asientos de Tipo IGTF . Dirijace al módulo de compañia y habilitela'))


    def registro_movimiento_pago(self,igtf_porcentage,total_monto):
        name = self.get_name()
        amount_itf = round(float(total_monto) * float((igtf_porcentage / 100.00)),2)
        #raise UserError(_('monto xx = %s')%amount_itf)
        value = {
            'name': name,
            'date': self.payment_date,
            'journal_id': self.journal_id.id,
            'line_ids': False,
            'state': 'draft',
            #'amount_total':amount_itf,# revisar
            #'amount_total_signed':amount_itf,# revisar
            'partner_id': self.partner_id.id,
            'ref': "Comisión del %s %% del pago %s por comisión" % (igtf_porcentage,name),
            #'name': "Comisión del %s %% del pago %s por comisión" % (igtf_porcentage,name),

        }
        move_obj = self.env['account.move']
        move_id = move_obj.create(value)     
        return move_id

    def registro_movimiento_linea_pago(self,igtf_porcentage,id_movv,total_monto):
        #raise UserError(_('ID MOVE = %s')%id_movv)
        amount_itf = round(float(total_monto) * float((igtf_porcentage / 100.00)),2)
        valores=amount_itf
        name = self.get_name()        
        #raise UserError(_('valores = %s')%valores)
        value = {
             'name': name,
             'ref' : "Comisión del %s %% del pago %s por comisión" % (igtf_porcentage,name),
             'move_id': int(id_movv),
             'date': self.payment_date,
             'partner_id': self.partner_id.id,
             'journal_id': self.journal_id.id,
             'account_id': self.journal_id.default_debit_account_id.id,
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

        value['account_id'] = self._get_company().account_wh_itf_id.id
        value['credit'] = 0.0 # aqui va cero
        value['debit'] = valores
        value['balance'] = valores


        move_line_id2 = move_line_obj.create(value)

        

    @api.model
    def check_partner(self):
        '''metodo que chequea el rif de la empresa y la compañia si son diferentes
        retorna True y si son iguales retorna False'''
        idem = False
        company_id = self._get_company()
        for pago in self:
            if pago.partner_id.vat != company_id.partner_id.vat:
                idem = True
                return idem
        return idem

    def _get_company_itf(self):
        '''Método que retorna verdadero si la compañia debe retener el impuesto ITF'''
        company_id = self._get_company()
        if company_id.calculate_wh_itf:
            return True
        return False

    @api.model
    def _get_company(self):
        '''Método que busca el id de la compañia'''
        company_id = self.env['res.users'].browse(self.env.uid).company_id
        return company_id

    @api.model
    def check_payment_type(self):
        '''metodo que chequea que el tipo de pago si pertenece al tipo outbound'''
        type_bool = False
        for pago in self:
            type_payment = pago.payment_type
            if type_payment == 'outbound':
                type_bool = True
        return type_bool

    def get_name(self):
        '''metodo que crea el Nombre del asiento contable si la secuencia no esta creada, crea una con el
        nombre: 'l10n_account_withholding_itf'''

        self.ensure_one()
        SEQUENCE_CODE = 'l10n_ve_cuenta_retencion_itf'
        company_id = self._get_company()
        IrSequence = self.env['ir.sequence'].with_context(force_company=company_id.id)
        name = IrSequence.next_by_code(SEQUENCE_CODE)

        # si aún no existe una secuencia para esta empresa, cree una
        if not name:
            IrSequence.sudo().create({
                'prefix': 'WITF',
                'name': 'Localización Venezolana impuesto ITF %s' % company_id.id,
                'code': SEQUENCE_CODE,
                'implementation': 'no_gap',
                'padding': 8,
                'number_increment': 1,
                'company_id': company_id.id,
            })
            name = IrSequence.next_by_code(SEQUENCE_CODE)
        return name  