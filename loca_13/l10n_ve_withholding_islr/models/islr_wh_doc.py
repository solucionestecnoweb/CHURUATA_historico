# -*- coding: utf-8 -*-


from odoo import api, fields, models, _ 
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp 



class IsrlWhDoc(models.Model):
    _name = 'islr.wh.doc'
    _order = 'date_ret desc, number desc'


    name = fields.Char(string='Description', size=64, readonly=True)
    code = fields.Char(string='Code', size=64, readonly=True, help='Voucher Reference')
    number = fields.Char(string='Withholding number', size=32, readonly=True, help="Voucher reference")
    type = fields.Selection(selection=[
            ('out_invoice', 'Customer Invoice'),
            ('in_invoice', 'Supplier Invoice'),
            ('in_refund', 'Supplier Invoice Refund'),
            ('out_refund', 'Customer Invoice Refund'),
            ], string='Type', readonly=True,
            #default=lambda s: s._get_type(),
            help="Voucher type")
    state = fields.Selection([
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('done', 'Done'),
            ('cancel', 'Cancelled')
            ], string='State', readonly=True, default='draft',
            help="Voucher state")
    date_ret = fields.Date(
            'Accounting Date', readonly=True,
            states={'draft': [('readonly', False)]},
            help="Keep empty to use the current date")
    date_uid = fields.Date(
            'Withhold Date', readonly=True,
            states={'draft': [('readonly', False)]}, help="Voucher date")
    account_id = fields.Many2one(
            'account.account', 'Account', # required=True,
            readonly=True,
            states={'draft': [('readonly', False)]},
            help="Account Receivable or Account Payable of partner")
    partner_id = fields.Many2one(
            'res.partner', 'Partner', readonly=True, required=True,
            states={'draft': [('readonly', False)]},
            help="Partner object of withholding")
    currency_id = fields.Many2one(
            'res.currency', 'Currency', required=True, readonly=True,
            states={'draft': [('readonly', False)]},
            # default=lambda s: s._get_currency(),
            help="Currency in which the transaction takes place")
    journal_id= fields.Many2one(
            'account.journal', 'Journal', required=True, readonly=True,
            states={'draft': [('readonly', False)]},
            #default=lambda s: s._get_journal(),
            help="Journal where accounting entries are recorded")
    company_id = fields.Many2one(
            'res.company', 'Company', required=True,
            #default=lambda s: s._get_company(),
            help="Company")
    amount_total_ret = fields.Float(
            #compute='_get_amount_total', 
            store=True, string='Amount Total',
            #digits=dp.get_precision('Withhold ISLR'),
            help="Total Withheld amount")
    concept_ids = fields.One2many(
            'islr.wh.doc.line', 
            'islr_wh_doc_id', 'Income Withholding Concept',
            readonly=True, states={'draft': [('readonly', False)]},
            help='concept of income withholding')
    #invoice_ids = fields.One2many(
    #        'islr.wh.doc.invoices', 'islr_wh_doc_id', 'Withheld Invoices',
    #        readonly=True, states={'draft': [('readonly', False)]},
    #        help='invoices to be withheld')
    #islr_wh_doc_id = fields.One2many(
    #        'account.invoice', 'islr_wh_doc_id', 'Invoices',
    #        states={'draft': [('readonly', False)]},
    #        help='refers to document income withholding tax generated in'
    #             ' the bill')
    user_id = fields.Many2one(
            'res.users', 'Salesman', readonly=True,
            states={'draft': [('readonly', False)]},
            #default=lambda s: s._uid,
            help="Vendor user")
    automatic_income_wh = fields.Boolean(
            string='Automatic Income Withhold',
            default=False,
            help='When the whole process will be check automatically, '
                 'and if everything is Ok, will be set to done')


class IslrWhDocLine(models.Model):
    _name = 'islr.wh.doc.line'
    _description = 'Lines of Document Income Withholding'


    def _amount_all(self):
        """ Return all amount relating to the invoices lines."""
        res = {}
        ut_obj = self.env['l10n.ut']
        for iwdl_brw in self.browse(self.ids):
            # Using a clousure to make this call shorter
            f_xc = ut_obj.sxc(
                iwdl_brw.invoice_id.company_id.currency_id.id,
                iwdl_brw.invoice_id.currency_id.id,
                iwdl_brw.islr_wh_doc_id.date_uid)

            res[iwdl_brw.id] = {
                'amount': (iwdl_brw.base_amount * (iwdl_brw.retencion_islr / 100.0)) or 0.0,
                'currency_amount': 0.0,
                'currency_base_amount': 0.0,
            }
            for xml_brw in iwdl_brw.xml_ids:
                res[iwdl_brw.id]['amount'] = xml_brw.wh
            res[iwdl_brw.id]['currency_amount'] = f_xc(
                res[iwdl_brw.id]['amount'])
            res[iwdl_brw.id]['currency_base_amount'] = f_xc(
                iwdl_brw.base_amount)
 


    def _retention_rate(self):
        """ Return the retention rate of each line."""
        res = {}
        for ret_line in self.browse(self.ids):
            if ret_line.invoice_id:
                pass
            else:
                res[ret_line.id] = 0.0
        return res


    name = fields.Char(
            'Description', size=64, help="Description of the voucher line")
    invoice_id = fields.Many2one(
            'account.invoice', 'Invoice', ondelete='set null',
            help="Invoice to withhold")
    #amount= fields.Float(compute='_amount_all', method=True, digits=(16, 2), string='Withheld Amount',
    #        multi='all', help="Amount withheld from the base amount")
    amount = fields.Float(string='Withheld Amount', digits=(16, 2), help="Amount withheld from the base amount")
    currency_amount= fields.Float(compute='_amount_all', method=True, digits=(16, 2),
            string='Foreign Currency Withheld Amount', multi='all',
            help="Amount withheld from the base amount")
    base_amount= fields.Float(
            'Base Amount', digits=dp.get_precision('Withhold ISLR'),
            help="Base amount")
    currency_base_amount= fields.Float(compute='_amount_all', method=True, digits=(16, 2),
            string='Foreign Currency Base amount', multi='all',
            help="Amount withheld from the base amount")
    raw_base_ut= fields.Float(
            'UT Amount', digits=dp.get_precision('Withhold ISLR'),
            help="UT Amount")
    raw_tax_ut= fields.Float(
            'UT Withheld Tax',
            digits=dp.get_precision('Withhold ISLR'),
            help="UT Withheld Tax")
    subtract = fields.Float(
            'Subtract', digits=dp.get_precision('Withhold ISLR'),
            help="Subtract")
    islr_wh_doc_id = fields.Many2one(
            'islr.wh.doc', 'Withhold Document', ondelete='cascade',
            help="Document Retention income tax generated from this bill")
    concept_id = fields.Many2one(
            'islr.wh.concept', 'Withholding Concept',
            help="Withholding concept associated with this rate")
    retencion_islr = fields.Float(
            'Withholding Rate',
            digits=dp.get_precision('Withhold ISLR'),
            help="Withholding Rate")
    retention_rate = fields.Float(compute=_retention_rate, method=True, string='Withholding Rate',
             help="Withhold rate has been applied to the invoice",
             digits=dp.get_precision('Withhold ISLR'))
    #xml_ids = fields.One2many(
    #        'islr.xml.wh.line', 'islr_wh_doc_line_id', 'XML Lines',
    #        help='XML withhold invoice line id')
    iwdi_id = fields.Many2one(
            'islr.wh.doc.invoices', 'Withheld Invoice', ondelete='cascade',
            help="Withheld Invoices")
    partner_id = fields.Many2one('res.partner', related='islr_wh_doc_id.partner_id', string='Partner', store=True)
    fiscalyear_id = fields.Many2one( 'account.fiscalyear', string='Fiscalyear',store=True)


class IslrWhHistoricalData(models.Model):
    _name = "islr.wh.historical.data"
    _description = 'Lines of Document Income Withholding'


    partner_id = fields.Many2one(
            'res.partner', 'Partner', readonly=False, required=True,
            help="Partner for this historical data")
    fiscalyear_id = fields.Many2one(
            'account.fiscalyear', 'Fiscal Year', readonly=False, required=True,
            help="Fiscal Year to applicable to this cumulation")
    concept_id = fields.Many2one(
            'islr.wh.concept', 'Withholding Concept', required=True,
            help="Withholding concept associated with this historical data")
    raw_base_ut = fields.Float(
            'Cumulative UT Amount', required=True,
            digits=dp.get_precision('Withhold ISLR'),
            help="UT Amount")
    raw_tax_ut = fields.Float(
            'Cumulative UT Withheld Tax', required=True,
            digits=dp.get_precision('Withhold ISLR'),
            help="UT Withheld Tax")
