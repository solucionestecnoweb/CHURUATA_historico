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
                'date_start': self.id_mes(),
                'date_end': self.id_year(),
                'invoice_number': self.invoice_number,

                })
        #cursor_municipality = self.env['municipality.tax'].search([('id','=',self.wh_muni_id.id)])
        class MUnicipalityTax(models.Model):
            _inherit = 'municipality.tax'

            if self.type=="in_invoice" or self.type=="in_refund" or self.type=="in_receipt":
                #raise UserError(_('self2 = %s')%cursor_municipality)
                cursor_municipality.action_post()

# *************** RUTINA PARA EL COMPROBANTE DE RETENCION IVA *************
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
        class RetentionVat(models.Model):
         _inherit = 'vat.retention'
         if self.type=="in_invoice" or self.type=="in_refund" or self.type=="in_receipt":
            #raise UserError(_('self2 = %s')%lista_account_retention)
            lista_account_retention.action_posted()
        # FIN PUNTO D

    def id_mes(self):
        fecha=str(self.date)
        mes=fecha[5:7]
        cur_mes = self.env['period.month'].search([('months_number','=',mes)])
        for det in cur_mes:
            id_periodo_mes=det.id
        return id_periodo_mes

    def id_year(self):
        fecha=str(self.date)
        ano=fecha[0:4]
        cur_year = self.env['period.year'].search([('name','=',ano)])
        for det in cur_year:
            id_periodo_year=det.id
        return id_periodo_year