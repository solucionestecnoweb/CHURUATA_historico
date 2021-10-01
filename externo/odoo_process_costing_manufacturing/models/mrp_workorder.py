# -*- coding: utf-8 -*-

from odoo import api, fields, models

class MrpWorkOrder(models.Model):
    _inherit = 'mrp.workorder'
    
    @api.depends(
        'direct_material_ids.total_cost',
        'overhead_cost_ids.total_cost',
        'labour_cost_ids.total_cost',
    )
    def _compute_material_total(self):
        for rec in self:
            rec.material_total = sum([p.total_cost for p in rec.direct_material_ids])
            rec.overhead_total = sum([p.total_cost for p in rec.overhead_cost_ids])
            rec.labor_total = sum([p.total_cost for p in rec.labour_cost_ids])
    
    @api.depends(
        'direct_material_ids.total_actual_cost',
        'overhead_cost_ids.total_actual_cost',
        'labour_cost_ids.total_actual_cost',
    )
    def _compute_total_actual_cost(self):
        for rec in self:
            rec.total_actual_material_cost = sum([p.total_actual_cost for p in rec.direct_material_ids])
            rec.total_actual_labour_cost = sum([p.total_actual_cost for p in rec.labour_cost_ids])
            rec.total_actual_overhead_cost = sum([p.total_actual_cost for p in rec.overhead_cost_ids])
    
    @api.depends(
        'total_actual_material_cost',
        'total_actual_labour_cost',
        'total_actual_overhead_cost',
        'material_total','overhead_total','labor_total'
    )
    def _compute_total_final_cost(self):
        for rec in self:
            rec.final_total_cost = rec.material_total + rec.labor_total + rec.overhead_total
            rec.final_total_actual_cost = rec.total_actual_material_cost + rec.total_actual_labour_cost + rec.total_actual_overhead_cost
    
    direct_material_ids = fields.One2many(
        'workorder.job.cost.line',
        'workorder_id',
        string="Direct Material",
        domain=[('job_type','=','material')],
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}, 
    )
    labour_cost_ids = fields.One2many(
        'workorder.job.cost.line',
        'workorder_id',
        string="Direct Labour",
        domain=[('job_type','=','labour')],
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}, 
    )
    overhead_cost_ids = fields.One2many(
        'workorder.job.cost.line',
        'workorder_id',
        string="Direct Overhead",
        domain=[('job_type','=','overhead')],
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}, 
    )
    labor_total = fields.Float(
        string='Total Labour Cost',
        compute='_compute_material_total',
        store=True,
    )
    overhead_total = fields.Float(
        string='Total Overhead Cost',
        compute='_compute_material_total',
        store=True,
    )
    material_total = fields.Float(
        string='Total Material Cost',
        compute='_compute_material_total',
        store=True,
    )
    total_actual_labour_cost = fields.Float(
        string='Total Actual Labour Cost',
        compute='_compute_total_actual_cost',
        store=True,
    )
    total_actual_material_cost = fields.Float(
        string='Total Actual Material Cost',
        compute='_compute_total_actual_cost',
        store=True,
    )
    total_actual_overhead_cost = fields.Float(
        string='Total Actual Overhead Cost',
        compute='_compute_total_actual_cost',
        store=True,
    )
    final_total_cost = fields.Float(
        string='Total Cost',
        compute='_compute_total_final_cost',
        store=True,
    )
    final_total_actual_cost = fields.Float(
        string='Total Actual Cost',
        compute='_compute_total_final_cost',
        store=True,
    )
    custom_currency_id = fields.Many2one(
        'res.currency', 
        default=lambda self: self.env.user.company_id.currency_id, 
        string='Currency', 
        readonly=True
    )
    
    #@api.multi
    def write(self, vals):
        rec = super(MrpWorkOrder, self).write(vals)
        if vals.get('qty_producing'):
            for order in self:
                for bom_material in order.production_id.bom_id.direct_material_ids:
                    material_id = order.direct_material_ids.filtered(lambda material: material.product_id == bom_material.product_id)
                    if material_id:
                        for material in material_id:
                            material.product_qty = (bom_material.product_qty * order.qty_production) / order.production_id.bom_id.product_qty
                            material.actual_quantity = (bom_material.product_qty * order.qty_production) / order.production_id.bom_id.product_qty
                
                for bom_labour in order.production_id.bom_id.labour_cost_ids:
                    labour_id = order.labour_cost_ids.filtered(lambda labour: labour.product_id == bom_labour.product_id)
                    if labour_id:
                        for labour in labour_id:
                            labour.product_qty = (bom_labour.product_qty * order.qty_production) / order.production_id.bom_id.product_qty
                            labour.actual_quantity = (bom_labour.product_qty * order.qty_production) / order.production_id.bom_id.product_qty
    #                   
                for bom_overhead in order.production_id.bom_id.overhead_cost_ids:
                    overhead_id = order.overhead_cost_ids.filtered(lambda overhead: overhead.product_id == bom_overhead.product_id)
                    if overhead_id:
                        for overhead in overhead_id:
                            overhead.product_qty = (bom_overhead.product_qty * order.qty_production) / order.production_id.bom_id.product_qty
                            overhead.actual_quantity = (bom_overhead.product_qty * order.qty_production) / order.production_id.bom_id.product_qty
                
        return rec
