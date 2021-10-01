# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta

class MrpProduction(models.Model):
    _inherit = "mrp.production"


    def button_mark_done(self):
        self.picking_mrp()
        return super(MrpProduction, self).button_mark_done()

    def picking_mrp(self):
        
        tipo_salida = self.env['type.operation.kardex'].search([('code','=','10')])
        for t in self.move_raw_ids:
            t.type_operation_sunat_id = tipo_salida[0].id

        tipo_entrada = self.env['type.operation.kardex'].search([('code','=','19')])
        for k in self.move_finished_ids:
            k.type_operation_sunat_id = tipo_entrada[0].id