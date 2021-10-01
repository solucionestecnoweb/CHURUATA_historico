# -*- coding: utf-8 -*-


from odoo import api, fields, models, _




class Partners(models.Model):
    _name = 'account.history.invoice'

    invoice_id = fields.Many2one('account.move', string='ID Factura')
    nro_comprobante_iva = fields.Char(string='Nro de comprobante iva')
    nro_asiento_iva = fields.Char(string='Nro de Asiento Iva')
    nro_comprobante_municipal = fields.Char(string='Nro de comprobante municipal')
    nro_asiento_municipal = fields.Char(string='Nro de Asiento Municipal')
    nro_comprobante_islr = fields.Char(string='Nro de comprobante ISLR')
    nro_asiento_islr = fields.Char(string='Nro de Asiento ISLR')
    existe_doc_iva= fields.Boolean(defaul=False)
    existe_doc_muni= fields.Boolean(defaul=False)
    existe_doc_islr= fields.Boolean(defaul=False)