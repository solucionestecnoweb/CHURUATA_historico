import logging
from odoo import fields, models, api, exceptions, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger('__name__')


class AccountInherit(models.Model):
    """This model add fields need in the invoice for accounting in Venezuela."""
    _inherit = 'purchase.order'

    rif = fields.Char(compute='_concatena', string='RIF')

    @api.depends('partner_id')
    def _concatena(self):
        if not self.partner_id.vat:
            aux="0000000000"
        else:
            aux= self.partner_id.vat
        if self.partner_id.doc_type=="v":
            tipo_doc="V"
        if self.partner_id.doc_type=="e":
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
        #self.rif=str(tipo_doc)+"-"+str(self.partner_id.vat)
        self.rif=str(tipo_doc)+"-"+str(aux)

class AccountInheritSale(models.Model):
    """This model add fields need in the invoice for accounting in Venezuela."""
    _inherit = 'sale.order'

    rif = fields.Char(compute='_concatena', string='RIF')

    @api.depends('partner_id')
    def _concatena(self):
        if not self.partner_id.vat:
            aux="0000000000"
            #self.partner_id.vat="E00010000"
        else:
            aux= self.partner_id.vat
        if self.partner_id.doc_type=="v":
            tipo_doc="V"
        if self.partner_id.doc_type=="e":
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
        #self.rif=str(tipo_doc)+"-"+str(self.partner_id.vat)
        self.rif=str(tipo_doc)+"-"+str(aux)