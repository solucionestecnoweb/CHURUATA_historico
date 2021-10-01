# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import datetime

class LandedCost(models.Model):
    _inherit = 'stock.landed.cost'
    
    company_id = fields.Many2one(comodel_name='res.company',default=(lambda self: self.env.user.company_id),required=True,string='Company')
    company_currency_id = fields.Many2one('res.currency', string='Company Currency', readonly=True, related='company_id.currency_id')
    foreign_currency_id = fields.Many2one('res.currency', store=True, readonly=True, tracking=True, required=True, string='Foreign Currency')
    amount_total_vendor = fields.Monetary(string='Total vendor bills', currency_field='foreign_currency_id')
    amount_total_vendor_signed = fields.Monetary(string='Total vendor bills', currency_field='company_currency_id')
    amount_total_expenses = fields.Monetary(string='Total expenses', currency_field='foreign_currency_id')
    amount_total_expenses_signed = fields.Monetary(string='Total expenses', currency_field='company_currency_id')
    amount_total_landed = fields.Monetary(string='Total landed cost', currency_field='foreign_currency_id')
    amount_total_landed_signed = fields.Monetary(string='Total landed cost', currency_field='company_currency_id')
    total_quantity = fields.Float(string='Total quantity', digits=(12, 2))
    unit_cost = fields.Float(string='Unit Cost', digits='Product Price')
    unit_cost_signed = fields.Float(string='Unit Cost', digits='Product Price')
    vendor_bill_ids = fields.One2many('account.move', 'vendor_landed_cost_id', string='Vendor bills')
    expenses_bill_ids = fields.One2many('account.move', 'expenses_landed_cost_id', string='Expenses bills')
    many_products = fields.Boolean(string='Many products', default = False)
    data_for_report_ids = fields.One2many('data.for.report', 'landed_id', string='Expenses bills')

    def button_validate(self):
        res = super(LandedCost, self).button_validate()
        stock_moves = self.env['stock.move'].search([('picking_id','in',self.picking_ids.ids)])
        for move in stock_moves:
            move.kardex_price_unit += self.amount_total / sum(stock_moves.mapped('product_uom_qty'))
        return res

    def populate_expenses_bill_ids(self):
        if self.expenses_bill_ids:
            vals = []
            for bill in self.expenses_bill_ids:
                for item in bill.invoice_line_ids:
                    if item.product_id:
                        if bill.currency_id != self.company_currency_id:                                                                        
                            price_unit = item.price_subtotal * bill.currency_rate
                            foreign_pu = item.price_subtotal
                        else:
                            price_unit = item.price_subtotal
                            foreign_pu = item.price_subtotal / bill.currency_id._get_conversion_rate(self.foreign_currency_id, self.company_currency_id, self.env.user.company_id, bill.invoice_date or  datetime.datetime.now())
                        val = {
                            'cost_id': self.id,
                            'product_id': item.product_id.id,
                            'name': item.name,
                            'account_id': item.account_id.id,
                            'price_unit': price_unit,
                            'foreign_pu': foreign_pu,
                            'split_method': 'by_quantity',
                            'expense_bill_id': bill.id
                        }
                        vals.append(val)
                    else:
                        raise UserError(_('There is no product selected in the expenses bill %s') %(bill.name))
            self.cost_lines.unlink()
            self.env['stock.landed.cost.lines'].create(vals)
    
    @api.onchange('expenses_bill_ids')
    def _onchange_expenses_bill_ids(self):
        total = total_signed = 0
        for inv in self.expenses_bill_ids:
            if inv.type == 'in_refund':
                sign = -1
            else:
                sign = 1
            if self.foreign_currency_id != inv.currency_id:
                if inv.tc_per:
                    total += inv.amount_untaxed / inv.currency_rate * sign
                else:
                    total += inv.amount_untaxed / inv.currency_id._get_conversion_rate(self.foreign_currency_id, inv.currency_id, self.company_id, inv.invoice_date or datetime.datetime.now()) * sign
                total_signed += abs(inv.amount_untaxed_signed) * sign
            else:
                total += inv.amount_untaxed * sign
                total_signed += abs(inv.amount_untaxed_signed) * sign
        self.amount_total_expenses = total
        self.amount_total_expenses_signed = total_signed
        self.get_total_landed_cost()
        # self.populate_expenses_bill_ids()

    def _check_quantity(self):
        inv_qty = 0
        pick_qty = 0
        for inv in self.vendor_bill_ids:
            for iline in inv.invoice_line_ids:
                inv_qty += iline.quantity
            for pick in inv.picking_ids:
                for pline in pick.move_ids_without_package:
                    pick_qty += pline.quantity_done
        if inv_qty != pick_qty:
            raise UserError(_('Quantities in invoices are not the same than quantities in invoice pickins.'))

    @api.onchange('vendor_bill_ids')
    def _onchange_vendor_bill_ids(self):
        self._check_quantity()
        picking_ids = []
        product_ids = []
        total = total_signed = quantity = 0
        for inv in self.vendor_bill_ids:
            if not inv.picking_ids:
                raise UserError(_('There is no pickings on this invoice %s.') %inv.name)
            total += inv.amount_untaxed
            total_signed += abs(inv.amount_untaxed_signed)
            if not self.foreign_currency_id:
                self.foreign_currency_id = inv.currency_id
            for picking in inv.picking_ids:
                picking_ids.append(picking.id) 
            for line in inv.invoice_line_ids:
                quantity += line.quantity
                if line.product_id.id not in product_ids and not self.many_products:
                    product_ids.append(line.product_id.id)
                    if len(product_ids) > 1:
                        self.many_products = True
                    else:
                        self.many_products = False
                else:
                    if len(product_ids) < 2:
                        self.many_products = False
        self.total_quantity = quantity
        self.amount_total_vendor = total
        self.amount_total_vendor_signed = total_signed
        self.picking_ids = [(6, 0, picking_ids)]
        self.get_total_landed_cost()
        if self.many_products:
            return {
                'warning': {
                    'title': _('Landed Cost Warning!'),
                    'message': _('This landed cost form will have more than one product')}
                }

    def get_total_landed_cost(self):
        self.amount_total_landed = self.amount_total_vendor + self.amount_total_expenses
        self.amount_total_landed_signed = self.amount_total_vendor_signed + self.amount_total_expenses_signed
        if self.total_quantity > 0:
            self.unit_cost = self.amount_total_landed / self.total_quantity
            self.unit_cost_signed = self.amount_total_landed_signed / self.total_quantity
        else:
            self.unit_cost = 0
            self.unit_cost_signed = 0

    #TODO modificar para el nuevo modelo desde la funcion heredada
    def compute_landed_cost(self):
        res = super(LandedCost, self).compute_landed_cost()
        vals = []
        for valuation in self.valuation_adjustment_lines:
            eb_id = valuation.cost_line_id.expense_bill_id
            # if eb_id.currency_id != self.env.user.company_id.currency_id:
            valuation.additional_landed_cost_foreign = valuation.additional_landed_cost / eb_id.currency_rate
            # else:
            #     valuation.additional_landed_cost_foreign = valuation.additional_landed_cost / eb_id.currency_id._get_conversion_rate(self.foreign_currency_id, self.company_currency_id, self.env.user.company_id, eb_id.invoice_date or  datetime.datetime.now())
        product_ids = []
        for pick in self.picking_ids:
            for line in pick.move_ids_without_package:
                if line.product_id.id not in product_ids:
                    product_ids.append(line.product_id.id)
        for product_id in product_ids:
            total_qty = sum(self.env['account.move.line'].search([('move_id','=', self.vendor_bill_ids.ids)]).filtered(lambda v: v.product_id.id == product_id).mapped('quantity'))
            val = {
                    'landed_id': self.id,
                    'product_id': product_id,
                    'product_qty': total_qty,
            }
            self.env['data.for.report'].search([('landed_id','=',self.id),('product_id','=', product_id)]).unlink()
            dfr = self.env['data.for.report'].create(val)
            for cost in self.cost_lines:
                add_lan_cos = sum(self.env['stock.valuation.adjustment.lines'].search([('cost_line_id','=', cost.id)]).filtered(lambda v: v.product_id.id == product_id).mapped('additional_landed_cost'))
                add_lan_cos_for = sum(self.env['stock.valuation.adjustment.lines'].search([('cost_line_id','=', cost.id)]).filtered(lambda v: v.product_id.id == product_id).mapped('additional_landed_cost_foreign'))
                val = {
                    'data_id': dfr.id,
                    'vendor_bill_id': False,
                    'expense_bill_id': cost.expense_bill_id.id,
                    'additional_landed_cost': add_lan_cos_for,
                    'additional_landed_cost_signed': add_lan_cos,
                }
                vals.append(val)
            for inv in self.vendor_bill_ids:
                if product_id in inv.invoice_line_ids.product_id.ids:
                    total_invoice = sum(self.env['account.move.line'].search([('move_id','=', inv.id)]).filtered(lambda v: v.product_id.id == product_id).mapped('price_subtotal'))
                    if inv.currency_id != inv.company_currency_id:
                        add_lan_cos = total_invoice * inv.currency_rate
                        add_lan_cos_for = total_invoice
                    else:
                        add_lan_cos_for = total_invoice / inv.currency_rate
                        add_lan_cos = total_invoice
                    val = {
                        'data_id': dfr.id,
                        'vendor_bill_id': inv.id,
                        'expense_bill_id': False,
                        'additional_landed_cost': add_lan_cos_for,
                        'additional_landed_cost_signed': add_lan_cos,
                    }
                    vals.append(val)
        self.env['data.for.report.line'].search([('data_id.landed_id','=',self.id)]).unlink()
        self.env['data.for.report.line'].create(vals)
        rec = self.env['data.for.report.line'].search([('data_id.landed_id','=',self.id)])
        return res

class LandedCostLine(models.Model):
    _inherit = 'stock.landed.cost.lines'

    expense_bill_id = fields.Many2one('account.move', string='Expense Bill')
    foreign_pu = fields.Float(string='Foreign Currency Cost', digits='Product Price')

class AdjustmentLines(models.Model):
    _inherit = 'stock.valuation.adjustment.lines'

    additional_landed_cost_foreign = fields.Float(string='Foreign Currency Additional Landed Cost', digits='Product Price')

class DataForReport(models.Model):
    _name = 'data.for.report'
    _description = 'Data For Report'

    landed_id = fields.Many2one('stock.landed.cost', string='Stock Landed Cost')
    product_id = fields.Many2one('product.product', string='Product')
    product_qty = fields.Float(string='Quantity')
    line_ids = fields.One2many('data.for.report.line', 'data_id', string='Data For Report Line')

class DataForReportLine(models.Model):
    _name = 'data.for.report.line'
    _description = 'Data For Report Line'

    data_id = fields.Many2one('data.for.report', string='Data For Report')
    vendor_bill_id = fields.Many2one('account.move', string='Vendor Bill')
    expense_bill_id = fields.Many2one('account.move', string='Expense Bill')
    additional_landed_cost = fields.Float(string='Additional Landed Cost', digits='Product Price')
    additional_landed_cost_signed = fields.Float(string='Additional Landed Cost Signed', digits='Product Price')