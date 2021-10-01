# -*- coding: utf-8 -*-


import logging


from odoo import api, fields, models, _ 
from odoo.exceptions import UserError

_logger = logging.getLogger('__name__')

class ProductTemplate(models.Model):
    _inherit = 'product.template'


    islr_concept_id = fields.Many2one('islr.concept', string='ISLR Concept', help='Concept Income with')



class ProductProduct(models.Model):

    _inherit = "product.product"

    @api.onchange('type')
    def onchange_product_type(self):
        """ Add islr concept
        """
        concept_id = False
        if self.type != 'service':
            concept_obj = self.env['islr.concept']

            concept_id = concept_obj.search([('retentioned', '=', False)])
            concept_id = concept_id and concept_id[0] or False
            if not concept_id:
                raise UserError(
                    _('Invalid action !'),
                    _("Must create the concept of income withholding"))

        self.write({'islr_concept_id': concept_id or False})
