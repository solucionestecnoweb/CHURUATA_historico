# coding: utf-8
###########################################################################

from odoo import fields, models, api


class ResCompany(models.Model):
    _inherit = 'res.company'


    calculate_wh_itf= fields.Boolean(
            string='Retención automática de IGTF',
            help='Cuando es cierto, la retención de IGTF del proveedor se comprobará y '
                 'validar automáticamente', default=False)
    wh_porcentage = fields.Float(string="Percentage IGTF", help="El porcentaje a aplicar para retener ")

    account_wh_itf_id = fields.Many2one('account.account', string="Cuenta cuenta IGTF", help="Esta cuenta se usará en lugar de la predeterminada"
                                                       "uno como la cuenta por pagar para el socio actual")


    @api.onchange('calculate_wh_itf')
    def _onchange_check_itf(self):

        if not self.calculate_wh_itf:
            self.write({'wh_porcentage':0.0,
                        'account_wh_itf_id': 'False'})
        return