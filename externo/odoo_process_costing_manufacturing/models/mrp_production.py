# -*- coding: utf-8 -*-

from odoo import api, fields, models

class MrpProduction(models.Model):
    _inherit = 'mrp.production'
    
    @api.model
    def create(self, vals):
        result = super(MrpProduction, self).create(vals)
        if not result.bom_id:
            return result
        material_list = []
        labour_list = []
        overhead_list = []
        job_cost_obj = self.env['mrp.job.cost.line']
        
        for material in result.bom_id.direct_material_ids:
               material_vals = {'routing_workcenter_id': material.routing_workcenter_id.id, 
                      'product_id': material.product_id.id, 
                      'product_qty': (result.product_qty * material.product_qty) / result.bom_id.product_qty,
                      'job_type':'material',
                      'uom_id': material.uom_id.id,
                      'cost_price': material.cost_price,
                      'total_cost': material.total_cost,
                      'actual_quantity': material.actual_quantity,
                      'mrp_id':result.id
                      }
               job_cost_obj.create(material_vals)
                
        for labour in result.bom_id.labour_cost_ids:
                labour_vals = {'routing_workcenter_id': labour.routing_workcenter_id.id, 
                      'product_id': labour.product_id.id, 
                      'product_qty': (result.product_qty * labour.product_qty) / result.bom_id.product_qty,
                      'job_type':'labour',
                      'uom_id': labour.uom_id.id,
                      'cost_price': labour.cost_price,
                      'total_cost': labour.total_cost,
                      'actual_quantity': labour.actual_quantity,
                      'mrp_id':result.id
                      }
                job_cost_obj.create(labour_vals)

        for overhead in result.bom_id.overhead_cost_ids:
                overhead_vals = {'routing_workcenter_id': overhead.routing_workcenter_id.id, 
                      'product_id': overhead.product_id.id, 
                      'product_qty': (result.product_qty * overhead.product_qty) / result.bom_id.product_qty,
                      'job_type':'overhead',
                      'uom_id': overhead.uom_id.id,
                      'cost_price': overhead.cost_price,
                      'total_cost': overhead.total_cost,
                      'actual_quantity': overhead.actual_quantity,
                      'mrp_id':result.id
                      }
                job_cost_obj.create(overhead_vals)
        return result
        
    
    @api.depends(
        'direct_material_ids.product_qty',
        'overhead_cost_ids.product_qty',
        'labour_cost_ids.product_qty',
    )
    def _compute_material_total(self):
        for rec in self:
            rec.material_total = sum([p.total_cost for p in rec.direct_material_ids])
            rec.overhead_total = sum([p.total_cost for p in rec.overhead_cost_ids])
            rec.labor_total = sum([p.total_cost for p in rec.labour_cost_ids])
    
    @api.depends(
        'direct_material_ids.actual_quantity',
        'overhead_cost_ids.actual_quantity',
        'labour_cost_ids.actual_quantity',
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
    
    @api.depends('product_qty')
    def _compute_everage_price(self):
        for rec in self:
            if rec.product_qty:
                rec.everage_price = rec.final_total_cost / rec.product_qty
            else:
                rec.everage_price = 0.0
    
    def _compute_unit_cost(self):
        for rec in self:
            if rec.product_qty:
                rec.unit_cost = rec.final_total_actual_cost / rec.product_qty
            else:
                rec.unit_cost = 0.0
        
    direct_material_ids = fields.One2many(
        'mrp.job.cost.line',
        'mrp_id',
        string="Direct Material",
        domain=[('job_type','=','material')],
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}, 
    )
    labour_cost_ids = fields.One2many(
        'mrp.job.cost.line',
        'mrp_id',
        string="Direct Material",
        domain=[('job_type','=','labour')],
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}, 
    )
    overhead_cost_ids = fields.One2many(
        'mrp.job.cost.line',
        'mrp_id',
        string="Direct Material",
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
    everage_price = fields.Float(
        string="Everage Cost of Product",
        compute="_compute_everage_price",
    )
    unit_cost = fields.Float(
        string='Unit Cost',
        compute='_compute_unit_cost'
    )
    custom_currency_id = fields.Many2one(
        'res.currency', 
        related='bom_id.custom_currency_id',
        default=lambda self: self.env.user.company_id.currency_id, 
        string='Currency', 
        readonly=True
    )
    """custom_currency_id = fields.Many2one(
        'res.currency', 
        default=lambda self: self.env.user.company_id.currency_id, 
        string='Currency', 
        #readonly=True
    )"""
    
    precio_venta = fields.Float(string="Precio de venta Producto", compute='_compute_precio_venta')

    @api.depends('final_total_cost')
    def _compute_precio_venta(self):
      for rec in self:
        rec.precio_venta=rec.final_total_cost+(rec.final_total_cost*rec.company_id.porcentaje_ganancia/100)
        rec.product_id.list_price=rec.final_total_cost+(rec.final_total_cost*rec.company_id.porcentaje_ganancia/100)
        rec.product_id.standard_price=rec.final_total_cost
        #rec.product_id.=rec.custom_currency_id.id

    #@api.multi
    def _generate_workorders(self, exploded_boms):
        result = super(MrpProduction, self)._generate_workorders(exploded_boms)
        workder_job_costline_obj = self.env['workorder.job.cost.line']
        for rec in self:
            for material in rec.direct_material_ids:
                for order in result:
                    if material.routing_workcenter_id.workcenter_id == order.workcenter_id:
                        material_vals = {'routing_workcenter_id': material.routing_workcenter_id.id, 
                              'product_id': material.product_id.id, 
                              'product_qty': material.product_qty,
                              'job_type':'material',
                              'uom_id': material.uom_id.id,
                              'cost_price': material.cost_price,
                              'total_cost': material.total_cost,
                              'actual_quantity': material.product_qty,
                               'workorder_id':order.id
                              }
                        workorder_materil = workder_job_costline_obj.create(material_vals)
                        material.work_order_line_id = workorder_materil
            for labour in rec.labour_cost_ids:
                for order in result:
                    if labour.routing_workcenter_id.workcenter_id == order.workcenter_id:
                        labour_vals = {'routing_workcenter_id': labour.routing_workcenter_id.id, 
                              'product_id': labour.product_id.id, 
                              'product_qty': labour.product_qty,
                              'job_type':'labour',
                              'uom_id': labour.uom_id.id,
                              'cost_price': labour.cost_price,
                              'total_cost': labour.total_cost,
                              'actual_quantity': labour.product_qty,
                               'workorder_id': order.id
                              }
                        workorder_labour = workder_job_costline_obj.create(labour_vals)
                        labour.work_order_line_id = workorder_labour
            for overhead in rec.overhead_cost_ids:
                for order in result:
                    if overhead.routing_workcenter_id.workcenter_id == order.workcenter_id:
                        overhead_vals = {'routing_workcenter_id': overhead.routing_workcenter_id.id, 
                              'product_id': overhead.product_id.id, 
                              'product_qty': overhead.product_qty,
                              'job_type':'overhead',
                              'uom_id': overhead.uom_id.id,
                              'cost_price': overhead.cost_price,
                              'total_cost': overhead.total_cost,
                              'actual_quantity': overhead.product_qty,
                              'workorder_id': order.id
                              }
                        workorder_overhead = workder_job_costline_obj.create(overhead_vals)
                        overhead.work_order_line_id = workorder_overhead
                        
        return result
    
    #@api.multi
    def write(self, vals):
        rec = super(MrpProduction, self).write(vals)
        if vals.get('product_qty'):
            for order in self:
                for bom_material in order.bom_id.direct_material_ids:
                    material_id = order.direct_material_ids.filtered(lambda material: material.product_id == bom_material.product_id)
                    if material_id:
                        for material in material_id:
                            material.product_qty = (bom_material.product_qty * order.product_qty) / order.bom_id.product_qty
                
                for bom_labour in order.bom_id.labour_cost_ids:
                    labour_id = order.labour_cost_ids.filtered(lambda labour: labour.product_id == bom_labour.product_id)
                    if labour_id:
                        for labour in labour_id:
                            labour.product_qty = (bom_labour.product_qty * order.product_qty) / order.bom_id.product_qty
                    
                for bom_overhead in order.bom_id.overhead_cost_ids:
                    overhead_id = order.overhead_cost_ids.filtered(lambda overhead: overhead.product_id == bom_overhead.product_id)
                    if overhead_id:
                        for overhead in overhead_id:
                            overhead.product_qty = (bom_overhead.product_qty * order.product_qty) / order.bom_id.product_qty
                
        return rec
