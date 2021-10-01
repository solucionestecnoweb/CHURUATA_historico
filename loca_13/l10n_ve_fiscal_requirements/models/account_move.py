# -*- coding: utf-8 -*-

from odoo import api, fields, models, _ 



class AccountInherit(models.Model):
    """This model add fields need in the invoice for accounting in Venezuela."""
    _inherit = 'account.move'

    rif = fields.Char(string='RIF', store=True)
    #rif = fields.Char(related='partner_id.vat', string='RIF', store=True)
    nr_manual= fields.Boolean(defaul=False)
    
    invoice_number = fields.Char(required=False)

    invoice_number_pro = fields.Char(required=False)# campo libre
    invoice_number_cli = fields.Char(required=False)
    refuld_number_pro = fields.Char(required=False)
    refuld_number_cli = fields.Char(required=False)
    #invoice_number = fields.Char(string='Invoice number', required=False)
    invoice_ctrl_number = fields.Char(required=False)

    invoice_ctrl_number_cli = fields.Char(required=False)
    invoice_ctrl_number_pro = fields.Char(required=False)
    refund_ctrl_number_cli = fields.Char(required=False)
    refund_ctrl_number_pro = fields.Char(required=False)
    #invoice_ctrl_number = fields.Char(string='Invoice control number', required=False)
    import_form_num = fields.Char(string='Import form number')
    import_dossier = fields.Char(string='Import dossier number')
    import_date = fields.Char(string='Import date')



class AccountTax(models.Model):
    _inherit = 'account.tax'

    aliquot = fields.Selection(selection=[
        ('no_tax_credit','No tax Credit'),
        ('exempt','Exempt'),
        ('general','General Aliquiot'),
        ('reduced','Reducted Aliquot'),
        ('additional','General Aliquiot + Additiona'),
        ], string='Aliquot', help='Specifies which aliquot is processed depending on the purchase book or sales book.')


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    type = fields.Selection(selection=[
        ('general','Generales'),
        ('sale','Sale'),
        ('purchase','Purchase'),
        ('sale_refund','Sale refund'),        
        ('purchase_refund','Purchase refund'),
        ('cash', 'Cash'),
        ('bank','Bank and Check'),
        ('situation', 'Opening/Closing situation'),
        ('sale_debit', 'Sale Debit'),
        ('purchase_debit', 'Purchase Debit'),
    ], string='type')
    note = fields.Text(string='Note about field type')
