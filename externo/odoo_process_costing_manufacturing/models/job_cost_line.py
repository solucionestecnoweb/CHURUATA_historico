# -*- coding: utf-8 -*-

from odoo import models, fields, api

class JobCostLine(models.Model): 
    _name = 'mrp.job.cost.line'
    _rec_name = 'description'
    
    @api.depends('product_qty','cost_price')
    def _compute_total_cost(self):
        for rec in self:
            rec.total_cost = rec.product_qty * rec.cost_price
    
    @api.depends('actual_quantity','cost_price')
    def _compute_mrp_actual_total_cost(self):
        for rec in self:
            rec.total_actual_cost = rec.actual_quantity * rec.cost_price
    
    routing_workcenter_id = fields.Many2one(
        'mrp.routing.workcenter',
        'Operation',
        copy=True,
        required=True,
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        copy=False,
        required=True,
    )
    description = fields.Char(
        string='Description',
        copy=False,
    )
    reference = fields.Char(
        string='Reference',
        copy=False,
    )
    date = fields.Date(
        string='Date',
        required=False,
        copy=False,
    )
    product_qty = fields.Float(
        string='Planned Qty',
        copy=False,
        required=True,
    )
    uom_id = fields.Many2one(
        'uom.uom',#product.uom
        string='UOM',
        required=True,
    )
    cost_price = fields.Float(
        string='Cost / Unit',
        copy=False,
    )
    total_cost = fields.Float(
        string='Total Cost',
        compute="_compute_total_cost",
        store=True,
    )
    currency_id = fields.Many2one(
        'res.currency', 
        related='mrp_id.custom_currency_id',
        string='Currency', 
        store=True,
        readonly=True
    )
    job_type = fields.Selection(
        selection=[('material','Material'),
                    ('labour','Labour'),
                    ('overhead','Overhead')],
        string="Process Cost Type",
        required=False,
    )
    bom_id = fields.Many2one(
        'mrp.bom',
        related='mrp_id.bom_id',
        store=True,
        string="Bill of Material",
    )
    mrp_id = fields.Many2one(
        'mrp.production',
        string="Manufacturing Order",
    )
    company_id = fields.Many2one(
        'res.company',
        related='mrp_id.company_id',
        store=True,
        string="Company",
    )
    routing_id = fields.Many2one(
        'mrp.routing',
        related='mrp_id.routing_id',
        store=True,
        string="Routing",
    )
    work_order_line_id = fields.Many2one(
        'workorder.job.cost.line',
        'Workorder Job Cost Line'
     )
    actual_quantity = fields.Float(
        string='Actual Qty',
        related='work_order_line_id.actual_quantity',
        store=True,
        readonly=True,
    )
    total_actual_cost = fields.Float(
        string='Total Actual Cost',
        compute="_compute_mrp_actual_total_cost",
    )
#     material_workorder_id = fields.Many2one(
#         'mrp.workorder',
#         string='Workorder',
#     )
#     labour_workorder_id = fields.Many2one(
#         'mrp.workorder',
#         string='Workorder',
#     )
#     overhead_workorder_id = fields.Many2one(
#         'mrp.workorder',
#         string='Workorder',
#     )
    to_produse_product = fields.Many2one(
        'product.product',
        string='Produced Product',
        related='mrp_id.product_id',
        store=True,
    )
    to_produse_qty = fields.Float(
        string='To Produce Qty',
        related='mrp_id.product_qty',
        store=True,
    )
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        for rec in self:
            rec.product_qty = 1.0
            rec.cost_price = rec.product_id.standard_price
            rec.uom_id = rec.product_id.uom_id

class BomJobCostLine(models.Model): 
    _name = 'bom.job.cost.line'
    _rec_name = 'description'
    
    @api.depends('product_qty','cost_price')
    def _compute_total_cost(self):
        for rec in self:
            rec.total_cost = rec.product_qty * rec.cost_price
    
    @api.depends('actual_quantity','cost_price')
    def _compute_actual_total_cost(self):
        for rec in self:
            rec.total_actual_cost = rec.actual_quantity * rec.cost_price
    
    routing_workcenter_id = fields.Many2one(
        'mrp.routing.workcenter',
        'Operation',
        copy=True,
        required=True,
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        copy=False,
        required=True,
    )
    description = fields.Char(
        string='Description',
        copy=False,
    )
    reference = fields.Char(
        string='Reference',
        copy=False,
    )
    date = fields.Date(
        string='Date',
        required=False,
        copy=False,
    )
    product_qty = fields.Float(
        string='Planned Qty',
        copy=False,
        required=True,
    )
    uom_id = fields.Many2one(
        'uom.uom',#'product.uom', 
        string='UOM',
        required=True,
    )
    cost_price = fields.Float(
        string='Cost / Unit',
        copy=False,
    )
    total_cost = fields.Float(
        string='Total Cost',
        compute="_compute_total_cost",
    )
    custom_currency_id = fields.Many2one(
        'res.currency', 
        related='bom_id.custom_currency_id',
        string='Currency', 
        store=True,
        readonly=True
    )
    job_type = fields.Selection(
        selection=[('material','Material'),
                    ('labour','Labour'),
                    ('overhead','Overhead')
                ],
        string="Type",
        required=False,
    )
    bom_id = fields.Many2one(
        'mrp.bom',
        string="BOM",
    )
    actual_quantity = fields.Float(
        string='Actual Qty',
    )
    total_actual_cost = fields.Float(
        string='Total Actual Cost Price',
#         compute="_compute_actual_mrp_total_cost",
    )
    
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        for rec in self:
            rec.product_qty = 1.0
            rec.cost_price = rec.product_id.standard_price
            rec.uom_id = rec.product_id.uom_id


class WorkJobCostLine(models.Model): 
    _name = 'workorder.job.cost.line'
    _rec_name = 'description'
    
    @api.depends('product_qty','cost_price')
    def _compute_total_cost(self):
        for rec in self:
            rec.total_cost = rec.product_qty * rec.cost_price
    
    @api.depends('actual_quantity','cost_price')
    def _compute_work_actual_total_cost(self):
        for rec in self:
            rec.total_actual_cost = rec.actual_quantity * rec.cost_price
    
    routing_workcenter_id = fields.Many2one(
        'mrp.routing.workcenter',
        'Operation',
        copy=True,
        required=True,
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        copy=False,
        required=True,
    )
    description = fields.Char(
        string='Description',
        copy=False,
    )
    reference = fields.Char(
        string='Reference',
        copy=False,
    )
    date = fields.Date(
        string='Date',
        required=False,
        copy=False,
    )
    product_qty = fields.Float(
        string='Planned Qty',
        copy=False,
        required=True,
    )
    uom_id = fields.Many2one(
        'uom.uom',#product.uom
        string='UOM',
        required=True,
    )
    cost_price = fields.Float(
        string='Cost / Unit',
        copy=False,
    )
    actual_qty = fields.Float(
        string='Actual Cost',
        copy=False,
    )
#     actual_total_cost = fields.Float(
#         string='Total Actual Cost Price',
#         compute="_compute_total_actual_cost",
#     )
    total_cost = fields.Float(
        string='Total Cost',
        compute="_compute_total_cost",
    )
    currency_id = fields.Many2one(
        'res.currency', 
        related='workorder_id.custom_currency_id',
        string='Currency', 
        store=True,
        readonly=True
    )
    job_type = fields.Selection(
        selection=[('material','Material'),
                    ('labour','Labour'),
                    ('overhead','Overhead')
                ],
        string="Type",
        required=False,
    )
    workorder_id = fields.Many2one(
        'mrp.workorder',
        string='Workorder',
    )
    actual_quantity = fields.Float(
        string='Actual Qty',
    )
    total_actual_cost = fields.Float(
        string='Total Actual Cost',
        compute="_compute_work_actual_total_cost",
    )
    
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        for rec in self:
            rec.product_qty = 1.0
            rec.cost_price = rec.product_id.standard_price
            rec.uom_id = rec.product_id.uom_id

