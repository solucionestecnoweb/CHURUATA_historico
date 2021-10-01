# -*- coding: utf-8 -*-

from odoo import models, fields, api

class MrpBom(models.Model):
    _inherit = 'mrp.bom'
    
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
        'bom.job.cost.line',
        'bom_id',
        string="Direct Material",
        domain=[('job_type','=','material')],
    )
    labour_cost_ids = fields.One2many(
        'bom.job.cost.line',
        'bom_id',
        string="Direct Material",
        domain=[('job_type','=','labour')],
    )
    overhead_cost_ids = fields.One2many(
        'bom.job.cost.line',
        'bom_id',
        string="Direct Material",
        domain=[('job_type','=','overhead')],
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
    )
    """custom_currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
        store=True,
        string='Currency',
    )"""