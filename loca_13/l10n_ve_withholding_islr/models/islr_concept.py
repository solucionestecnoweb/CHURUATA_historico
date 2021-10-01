# -*- coding: utf-8 -*-


from odoo import api, fields, models, _ 
from odoo.addons import decimal_precision as dp



class IslrRate(models.Model):
        _name = 'islr.rates'

        name = fields.Char(string='Rate', store=True)
        # name = fields.Char(string='Rate', compute='_get_name', store=True)
        code = fields.Char(string='Cod. Concepto', size=3, required=True, help="Concept code")
        subtotal = fields.Float(
                'No tax amount', required=True,
                help=" '%' of the amount on which to apply the retention",
                digits=dp.get_precision('Retention ISLR'))
        min = fields.Float(
                'Minimum Amount', required=True,
                digits=dp.get_precision('Retention ISLR'),
                help="Minimum amount, from which it will determine whether you"
                        " withholded")
        retention_percentage = fields.Float(
                'Cantidad %', required=True,
                digits=dp.get_precision('Retention ISLR'),
                help="The percentage to apply to taxable withold income throw the"
                        " amount to withhold")
        subtract = fields.Float(string='Subtraendos', required=True, digits=dp.get_precision('Retention ISLR'))
        residence = fields.Boolean(
                'Residence',
                help="Indicates whether a person is resident, compared with the"
                        " direction of the Company")
        natural_person =fields.Boolean(
                'Nature', help="Indicates whether a person is nature or legal")
        
        islr_concept_id = fields.Many2one('islr.concepts', 'Retention  Concept', ondelete='cascade', help="Retention concept associated with this rate")
        
        rate2 = fields.Boolean('Rate 2', help='Rate Used for Foreign Entities')
        people_type = fields.Selection(string='Tipo Persona', selection=[
        ('resident_nat_people','PNRE'),
        ('non_resit_nat_people','PNNR'),
        ('domi_ledal_entity','PJDO'),
        ('legal_ent_not_domicilied','PJND'),
        ('legal_entity_not_incorporated','PJNCD'),
        ])



class IsrlConcepts(models.Model):
        """ We can create concept for ISLR Venezuela."""
        _name = 'islr.concept'


        name = fields.Char(string='Retention concept', required=True, help="Name of Retention Concept, Example: Profesional fees")
        retentioned = fields.Boolean(string='Withhold', default=True, help="Check if the concept  withholding is withheld or not.")
        purchase_account_id = fields.Many2one('account.account', 
                string="Purchase income retention account", 
                help="""This account will be used as the account where the withheld
                amounts shall be charged in full (Purchase) of income tax
                for this concept""")
        sales_accountt_id = fields.Many2one(
        'account.account',
        string="Sale account withhold income",
        required=False,
        help="This account will be used as the account in sale retention")
        rate_ids = fields.One2many(
        'islr.rates', 'islr_concept_id', 'Rate',
        help="Retention Concept rate", required=False)


class TaxUnit(models.Model):
        _inherit = 'tax.unit'


        @api.model
        def create(self, vals):
                t = super(TaxUnit, self).create(vals)
                concept = self.env['islr.rates'].search([])
                for item in concept :
                        if item.subtract > 0:
                                item.subtract = t.tax_unit_amount * 83.3334  * (item.retention_percentage /100)
                return t