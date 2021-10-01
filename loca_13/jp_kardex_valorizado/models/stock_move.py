# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta

import logging
_logger = logging.getLogger(__name__)

class StockMove(models.Model):
    _inherit = 'stock.move'

    kardex_price_unit = fields.Float(string='Kardex Price Unit', default=0) # digits=(total, decimal)
    type_operation_sunat_id = fields.Many2one('type.operation.kardex','Tipo de Transacción')
    valoracion = fields.One2many(comodel_name='stock.valuation.layer', inverse_name='stock_move_id', string='Valoracion')
    
    def set_kardex_price_unit(self):
        total = 0 
        for item in self.valoracion : 
            total += item.value
        self.kardex_price_unit = total / (self.product_qty+0.0000000000000000000000000001) 
        self.kardex_price_unit =  self.kardex_price_unit - self.price_unit 
        
    def _create_in_svl(self, forced_quantity=None):
        res = super(StockMove, self)._create_in_svl()
        for valuation in res:
            # Si existen ajustes de inventario inicial
            if valuation.stock_move_id.inventory_id:
                for line in valuation.stock_move_id.inventory_id.line_ids:
                    if line.product_id == valuation.product_id and line.location_id == valuation.stock_move_id.location_dest_id and line.is_initial:
                        valuation.update({
                            'unit_cost': line.initial_cost,
                            'value': line.initial_cost * valuation.quantity,
                            'remaining_value': line.initial_cost * valuation.quantity
                            })
                        line.product_id.standard_price = line.initial_cost
            else:
                if valuation.stock_move_id.purchase_line_id:
                    price_unit = valuation.stock_move_id.purchase_line_id.price_unit
                else:
                    if valuation.stock_move_id.origin_returned_move_id:
                        vl = self.env['stock.valuation.layer'].search([('stock_move_id','=', valuation.stock_move_id.origin_returned_move_id.id),('product_id','=',valuation.stock_move_id.product_id.id)])
                        price_unit = vl.unit_cost
                    else:
                        # TODO pensar como hacer para mover productos de una almacen a otro
                        # que pueden tener costo valorizados distintos
                        price_unit = valuation.stock_move_id.product_id.standard_price
                if valuation.stock_move_id.purchase_line_id.currency_id and valuation.stock_move_id.purchase_line_id.currency_id != self.env.user.company_id.currency_id:
                    rate = valuation.currency_id._get_conversion_rate(valuation.stock_move_id.purchase_line_id.currency_id, self.env.user.company_id.currency_id, self.env.user.company_id, valuation.stock_move_id.picking_id.kardex_date if valuation.stock_move_id.picking_id.use_kardex_date else valuation.stock_move_id.picking_id.scheduled_date)
                    if valuation.stock_move_id.picking_id.invoice_id: # or valuation.stock_move_id.picking_id.invoice_id_purchase:
                        # if valuation.stock_move_id.picking_id.invoice_id:
                        if valuation.stock_move_id.picking_id.invoice_id.tc_per:
                            price_unit = price_unit * valuation.stock_move_id.picking_id.invoice_id.currency_rate
                        else:
                            price_unit = price_unit * rate
                    else:
                        price_unit = price_unit * rate
                valuation.update({
                    'unit_cost': price_unit,
                    'value': price_unit * valuation.quantity,
                    'remaining_value': price_unit * valuation.quantity  
                })
        return res

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    kardex_id = fields.One2many(comodel_name='product.product.kardex.line', inverse_name='template', string='Kardex')

class ProductProduct(models.Model):
    _inherit = 'product.product'

    kardex_id = fields.One2many(comodel_name='product.product.kardex.line', inverse_name='name', string='Kardex')

    def ver_kardex(self):
        self.generate_kardex_gb()
        action = self.env.ref('jp_kardex_valorizado.kardex_line_action').read()[0]

        pickings = self.env['product.product.kardex.line'].search([])
        if len(pickings) > 1:
            action['domain'] = [('id', 'in', pickings.ids)]
        return action

    def generate_kardex_gb(self):
        movimientos = self.env['stock.valuation.layer'].search([
            ('product_id','=',self.id),
         #   ('account_move_id','!=', False),
        ])
        temp =  self.env['product.product.kardex.line'].search([])
        for t in temp:
            t.unlink()
        saldo = 0
        saldo_total = 0
        promedio = 0

        for line in movimientos :
            saldo +=  line.quantity
            saldo_total +=  line.value 
            promedio = saldo_total / saldo  if saldo > 0 else 0
            #
            if line.stock_move_id.type_operation_sunat_id.id:
                type_operation_sunat_id = line.stock_move_id.type_operation_sunat_id
            else : 
                type_operation_sunat_id = line.stock_move_id.picking_type_id.type_operation_sunat_id

            if line.quantity >= 0:
                self.env['product.product.kardex.line'].create({
                'name': self.id,
                'fecha': line.date,
                'type_operation_sunat_id' : type_operation_sunat_id.id,
                'cantidad_entradas':line.quantity,
                'costo_entradas':line.unit_cost,
                'total_bolivares_entradas': line.value,
                'total':saldo,
                'promedio':promedio,
                'total_bolivares':saldo_total
                })
            else :
                self.env['product.product.kardex.line'].create({
                'name': self.id,
                'fecha': line.date,
                'type_operation_sunat_id' : type_operation_sunat_id.id,
                'cantidad_salidas':line.quantity * -1 ,
                'costo_salidas': line.unit_cost , 
                'total_bolivares_salida': line.value * -1,
                'total':saldo,
                'promedio':  promedio,
                'total_bolivares':saldo_total
                })
       
    # def generate_kardex_gb(self):

        
    #     ingreso1= 0
    #     ingreso2= 0
    #     salida1= 0
    #     salida2= 0

    #     saldo = 0
    #     saldo_total = 0
    #     last_price = 0
    #     inicial = True
    #     movimientos =  self.movimientos()

       

    #     for line in movimientos :
            
    #         if line[16] :
    #             tipo = self.env['type.operation.kardex'].search([('id','=',line[16])])
    #         else :
    #             tipo = self.env['type.operation.kardex'].search([('name','=',line[3])])
    #         if len(tipo) > 0 :
    #             try:
                                       
    #                 if line[10]  > 0:
    #                     saldo +=  line[10]  if line[10] > 0 else 0
    #                     ing =  round(line[10] * line[12] if  line[12] else 0,2)
    #                     saldo_total +=  ing 
    #                     last_price = saldo_total / saldo if  saldo > 0 else last_price
                    
    #                 if line[11] > 0 :
    #                     saldo -=  line[11]  if line[11] > 0 else 0 
    #                     sal = round(last_price * line[11],2) if line[11] else 0
    #                     saldo_total -= sal

    #                 if line[10] > 0:
    #                     self.env['product.product.kardex.line'].create({
    #                     'name': self.id,
    #                     'fecha': line[8],
    #                     'type_operation_sunat_id' : tipo[0].id,
    #                     'cantidad_entradas':line[10],
    #                     'costo_entradas':line[12],
    #                     'total_bolivares_entradas': line[10] * line[12] if  line[12] else 0,
    #                     'total':saldo,
    #                     'promedio':last_price,
    #                     'total_bolivares':saldo_total
    #                     })
    #                 else :
    #                     self.env['product.product.kardex.line'].create({
    #                     'name': self.id,
    #                     'fecha': line[8],
    #                     'type_operation_sunat_id' : tipo[0].id,
    #                     'cantidad_salidas':line[11],
    #                     'costo_salidas': last_price , 
    #                     'total_bolivares_salida': line[11] * last_price,
    #                     'total':saldo,
    #                     'promedio':  last_price,
    #                     'total_bolivares':saldo_total
    #                     })
    #             except Exception as err:
    #                 _logger.error("%s", line)


    # def movimientos(self):
    #     cad = ""
    #     s_prod = [-1,-1,-1]
    #     s_loca = [-1,-1,-1]
    #     locat_ids = self.env['stock.location'].search( [('usage','in',('internal','inventory','transit','procurement','production'))] )
    #     lst_locations = locat_ids.ids

    #     lst_products  = [self.id]
    #     productos='{'
    #     almacenes='{'

    #     date_ini='2020-01-01'
    #     date_fin = fields.Date.today().strftime('%Y-%m-%d 23:59:59')

    #     if len(lst_products) == 0:
    #         raise osv.except_osv('Alerta','No existen productos seleccionados')

    #     for producto in lst_products:
    #         productos=productos+str(producto)+','
    #         s_prod.append(producto)
    #     productos=productos[:-1]+'}'
    #     for location in lst_locations:
    #         almacenes=almacenes+str(location)+','
    #         s_loca.append(location)
    #     almacenes=almacenes[:-1]+'}'

    #     import io
    #     from xlsxwriter.workbook import Workbook
    #     output = io.BytesIO()
    #     product = self.env['product.product'].browse(self.id)
    #     import datetime



    #     sql = """
    #     select
    #     slo.complete_name as "Ubicación Origen",
    #     sld.complete_name as "Ubicación Destino",
    #     sw.name as "Almacén",
    #     case
    #         when si.is_initial_sil = True then 'SALDO INICIAL'
    #         else
    #             case
    #                 when sm.inventory_id is not NULL then 'AJUSTE POR DIFERENCIA DE INVENTARIO'
    #                 else tok.name
    #             end
    #     end as "Tipo de Operación",
    #     pc.name as "Categoría",
    #     pt.name as "Producto",
    #     pp.default_code as "Código de Producto",
    #     uom.name as "Unidad",
    #     case
    #         when sp.invoice_id is not NULL then aml.invoice_date
    #         else
    #             case
    #                 when sp.use_kardex_date then sp.kardex_date
    #                 else 
    #                     case
    #                         when sm.inventory_id is NULL then sm.date
    #                         else
    #                             case
    #                                 when si.accounting_date is NULL then si.date
    #                                 else si.accounting_date
    #                             end
    #                     end
    #             end
    #     end as "Fecha",
    #     case
    #         when sp.invoice_id is not NULL then aml.invoice_name
    #         else
    #             case
    #                 when sp.name != '' then sp.name
    #                 else si.name
    #             end
    #     end as "Doc. Almacén",
    #             case 
    #         when sm.type_operation_sunat_id is  NULL then 
    #             case 
    #                 when spt.code = 'incoming' or coalesce(spt.code , '') = '' then sm.product_qty   
    #                 else  0
    #             end
    #         else 
    #             case 
    #                 when sm.type_operation_sunat_id = 10 or  sm.type_operation_sunat_id = 14 then 0
    #                 else sm.product_qty
    #             end
    #     end as "Entrada",
    #     case 
    #         when sm.type_operation_sunat_id is  NULL then  
    #             case
    #                 when spt.code = 'incoming' or coalesce(spt.code , '') = '' then 0
    #                 else sm.product_qty
    #             end
    #         else 
    #             case 
    #                 when sm.type_operation_sunat_id = 10 or  sm.type_operation_sunat_id = 14 then sm.product_qty
    #                 else 0
    #             end
    #     end as "Salida",
    #     svl.unit_cost + sm.kardex_price_unit as "Precio Unitario",
    #     sp.picking_type_id as "Tipo de Picking",
    #     sm.inventory_id as "Ajuste",
    #     si.is_initial_sil,
    #     sm.type_operation_sunat_id as "type_operation_sunat_id",
    #     sm.id "ID"
    #     from stock_move sm
    #     left join stock_move_line sml ON sm.id = sml.move_id
    #     left join stock_location slo ON sml.location_id = slo.id
    #     left join stock_location sld ON sml.location_dest_id = sld.id
    #     left join stock_warehouse sw ON sm.warehouse_id = sw.id
    #     left join stock_picking sp ON sp.id = sm.picking_id
    #     left join stock_picking_type spt ON sp.picking_type_id = spt.id
    #     left join type_operation_kardex tok ON tok.id = sp.type_operation_sunat_id
    #     left join product_product pp ON sm.product_id = pp.id
    #     left join product_template pt ON pp.product_tmpl_id = pt.id
    #     left join product_category pc ON pc.id = pt.categ_id
    #     left join uom_uom as uom ON uom.id = pt.uom_id
    #     left join stock_valuation_layer svl ON svl.stock_move_id = sm.id
    #     left join (select *, si.id as idsi, sil.is_initial as is_initial_sil from stock_inventory si
    #     left join stock_inventory_line sil ON sil.inventory_id = si.id where product_id in """ +str(tuple(s_prod))+ """ and si.state = 'done') si ON sm.inventory_id = si.idsi
    #     left join (select *, am.id as idam, am.ref as invoice_name from account_move am 
    #     left join account_move_line aml ON aml.move_id = am.id
    #     where aml.exclude_from_invoice_tab = false and aml.product_id in """ +str(tuple(s_prod))+ """) as aml ON sp.invoice_id = aml.idam
    #     where sm.product_id in """ +str(tuple(s_prod))+ """
    #     and sm.date >='""" + date_ini + """' and sm.date <='""" + date_fin + """'
    #     and (sml.location_id in """ +str(tuple(s_loca))+ """ or sml.location_dest_id in """ +str(tuple(s_loca))+ """)
    #     and svl.stock_landed_cost_id is NULL
    #     and sm.state = 'done'
    #     --and svl.unit_cost > 0
    #     order by "Fecha"
    #     """
    #     self.env.cr.execute(sql)
    #     #print(sql)
    #     return self.env.cr.fetchall()

class ProductKardexLine(models.TransientModel):
    _name = "product.product.kardex.line"

    template  = fields.Many2one(comodel_name='product.template', string='template')

    name  = fields.Many2one(comodel_name='product.product', string='Producto')
    type_operation_sunat_id = fields.Many2one('type.operation.kardex','Tipo de Transacción')

    fecha = fields.Date(string='Fecha')
    
    cantidad_inicial = fields.Float(string='Cantidad Incial')
    costo_intradas    = fields.Float(string='Costo de Inicial')
    total_bolivares_inicial   = fields.Float(string='Total Bolivares Inicial')

    category_id = fields.Many2one(comodel_name='product.category', string='Categoria')

    cantidad_entradas = fields.Float(string='Cantidad Entradas')
    costo_entradas    = fields.Float(string='Costo de Entradas')
    total_bolivares_entradas   = fields.Float(string='Total Bolivares ')

    cantidad_salidas  = fields.Float(string='Cantidad Salidas')
    costo_salidas     = fields.Float(string='Costo de Salidas')
    total_bolivares_salida     = fields.Float(string='Total Bolivares')

    total  = fields.Float(string='Total')
    promedio     = fields.Float(string='Promedio')
    total_bolivares     = fields.Float(string='Total Bolivares')
    
class StockScrap(models.Model):
    _inherit = 'stock.scrap'
  
    def action_validate(self):
        t = super(StockScrap, self).action_validate() 
        tipo = self.env['type.operation.kardex'].search([('id','=','14')])
        self.move_id.type_operation_sunat_id = tipo[0].id
        return t