# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _


# **************** RUTINA´PARA LOS COMPROBANTES DE RETENCION MUNICIPAL ***********
class MunicipalityTaxLine(models.Model):
    _inherit = 'municipality.tax.line'

    wh_amount = fields.Float(string='Withholding Amount', store=True)

    def _compute_wh_amount(self):
        # for line in self.act_code_ids:
        # if self.base_tax and self.aliquot:
        return 0

class AccountMove(models.Model):
    _inherit = 'account.move'

    def actualiza_voucher_wh(self):
        #super().actualiza_voucher_wh()
        #raise UserError(_('mama = %s')%self)
        withheld_amount=0
        amount=0
        cursor_line_muni = self.env['municipality.tax.line'].search([('municipality_tax_id','=',self.wh_muni_id.id)])
        for det_line in cursor_line_muni:
            ret=(det_line.base_tax*det_line.aliquot/100)
            withheld_amount=withheld_amount+det_line.base_tax
            amount=amount+ret
            self.env['municipality.tax.line'].browse(det_line.id).write({
                'wh_amount': ret,
                })

        cursor_municipality = self.env['municipality.tax'].search([('id','=',self.wh_muni_id.id)])
        for det in cursor_municipality:
            self.env['municipality.tax'].browse(det.id).write({
                'type': self.type,
                'amount': amount,
                'withheld_amount':withheld_amount,

                })
        #cursor_municipality = self.env['municipality.tax'].search([('id','=',self.wh_muni_id.id)])
        class MUnicipalityTax(models.Model):
            _inherit = 'municipality.tax'

            if self.type=="in_invoice" or self.type=="in_refund" or self.type=="in_receipt":
                #raise UserError(_('self2 = %s')%cursor_municipality)
                cursor_municipality.action_post()

# *************** RUTINA PARA EL COMPROBANTE DE RETENCION IVA *************
    def actualiza_voucher(self,ret_id):
        
        id_factura=self.id # USAR        
        #imponible_base=self.amount_untaxed
        #impuesto_ret_id=self.partner_id.vat_tax_account_id.id # no USAR
        agente_ret=self.partner_id.ret_agent # USAR AQUI INDICA SI ES O NO AGENTE DE RETENCION
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
        lista_account_retention_line = self.env['vat.retention.invoice.line'].search([('retention_id','=',ret_id)])
        #raise UserError(_('lista_account_retention_line = %s')%valor_iva)
        for det_line_retention in lista_account_retention_line:
            self.env['vat.retention.invoice.line'].browse(det_line_retention.id).write({
                'retention_amount': valor_ret,
                'retention_rate':porcentaje_ret,
                'move_id':id_factura,
                'amount_vat_ret':valor_iva,
                })
        lista_account_retention = self.env['vat.retention'].search([('id','=',ret_id)])
        for det_retention in lista_account_retention:
            self.env['vat.retention'].browse(det_retention.id).write({
                'vat_retentioned': valor_ret,
                'journal_id':self.journal_id.id,
                'amount_untaxed':imponible_base,
                'move_id':id_factura,
                'type':self.type,
                'voucher_delivery_date': self.date,
                })
        # PUNTO D
        class RetentionVat(models.Model):
         _inherit = 'vat.retention'
         if self.type=="in_invoice" or self.type=="in_refund" or self.type=="in_receipt":
            #raise UserError(_('self2 = %s')%lista_account_retention)
            lista_account_retention.action_posted()
        # FIN PUNTO D