# -*- coding: utf-8 -*-
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
import time
# import odoo.addons.decimal_precision as dp
from odoo.osv import osv
import base64
from odoo import models, fields, api
import codecs
import datetime
import pytz
import os

values = {}


class tree_view_kardex_fisico(models.Model):
    _name = 'tree.view.kardex.fisico'
    _auto = False

    u_origen = fields.Char('Ubicación Origen')
    u_destino = fields.Char('Ubicación Destino')
    almacen = fields.Char('Almacen')
    t_opera = fields.Char('Tipo de Operación')
    categoria = fields.Char('Categoría')
    producto = fields.Char('Producto')
    cod_pro = fields.Char('Código P.')
    unidad = fields.Char('Unidad')
    fecha = fields.Char('Fecha')
    doc_almacen = fields.Char('Doc. Almacén')
    entrada = fields.Char('Entrada')
    salida = fields.Char('Salida')
    orden_ubicacion = fields.Char('Ubicación')



class product_template(models.Model):
    _inherit = 'product.template'



    def get_kardex_fisico(self):
        products = self.env['product.product'].search([('product_tmpl_id','=',self.id)])
        if len(products)>1:
            raise osv.except_osv('Alerta','Existen variantes de productos, debe sacarse el kardex desde variante de producto.')
        return {
            'context':{'active_id':products[0].id},
            'name': 'Kardex Fisico',
            'type': 'ir.actions.act_window',
            'res_model': 'make.kardex.product',
            'view_mode': 'form',
            'views': [(False, 'form')],
            'target': 'new',
        }



class product_product(models.Model):
    _inherit = 'product.product'



    def get_kardex_fisico(self):
        return {
            'context':{'active_id':self.id},
            'name': 'Kardex Fisico',
            'type': 'ir.actions.act_window',
            'res_model': 'make.kardex.product',
            'view_mode': 'form',
            'views': [(False, 'form')],
            'target': 'new',
        }




class make_kardex(models.TransientModel):
    _name = "make.kardex"

    fini= fields.Date('Fecha inicial',required=True)
    ffin= fields.Date('Fecha final',required=True)
    products_ids=fields.Many2many('product.product','rel_wiz_kardex','product_id','kardex_id')
    location_ids=fields.Many2many('stock.location','rel_kardex_location','location_id','kardex_id','Ubicacion',required=True)
    allproducts=fields.Boolean('Todos los productos',default=True)
    destino = fields.Selection([('csv','CSV'),('crt','Pantalla')],'Destino')
    check_fecha = fields.Boolean('Editar Fecha')
    alllocations = fields.Boolean('Todos los almacenes',default=True)

    fecha_ini_mod = fields.Date('Fecha Inicial')
    fecha_fin_mod = fields.Date('Fecha Final')
    analizador = fields.Boolean('Analizador')

    @api.onchange('fecha_ini_mod')
    def onchange_fecha_ini_mod(self):
        self.fini = self.fecha_ini_mod


    @api.onchange('fecha_fin_mod')
    def onchange_fecha_fin_mod(self):
        self.ffin = self.fecha_fin_mod


    @api.model
    def default_get(self, fields):
        res = super(make_kardex, self).default_get(fields)
        import datetime
        fecha_hoy = str(datetime.datetime.now())[:10]
        fecha_inicial = fecha_hoy[:4] + '-01-01'
        res.update({'fecha_ini_mod':fecha_inicial})
        res.update({'fecha_fin_mod':fecha_hoy})
        res.update({'fini':fecha_inicial})
        res.update({'ffin':fecha_hoy})

        #locat_ids = self.pool.get('stock.location').search(cr, uid, [('usage','in',('internal','inventory','transit','procurement','production'))])
        locat_ids = self.env['stock.location'].search([('usage','in',('internal','inventory','transit','procurement','production'))])
        locat_ids = [elemt.id for elemt in locat_ids]
        res.update({'location_ids':[(6,0,locat_ids)]})
        return res

    @api.onchange('alllocations')
    def onchange_alllocations(self):
        if self.alllocations == True:
            locat_ids = self.env['stock.location'].search( [('usage','in',('internal','inventory','transit','procurement','production'))] )
            self.location_ids = [(6,0,locat_ids.ids)]
        else:
            self.location_ids = [(6,0,[])]



    def do_popup(self):		
        cad = ""
        s_prod = [-1,-1,-1]
        s_loca = [-1,-1,-1]
        if self.alllocations == True:
            locat_ids = self.env['stock.location'].search( [('usage','in',('internal','inventory','transit','procurement','production'))] )
            lst_locations = locat_ids.ids
        else:
            lst_locations = self.location_ids.ids
        lst_products  = self.products_ids.ids
        productos='{'
        almacenes='{'
        date_ini=self.fini.strftime("%Y-%m-%d")
        date_fin=self.ffin.strftime("%Y-%m-%d 23:59:59")
        if self.allproducts:
            lst_products = self.env['product.product'].with_context(active_test=False).search([]).ids

        else:
            lst_products = self.products_ids.ids

        if len(lst_products) == 0:
            raise osv.except_osv('Alerta','No existen productos seleccionados')

        for producto in lst_products:
            productos=productos+str(producto)+','
            s_prod.append(producto)
        productos=productos[:-1]+'}'
        for location in lst_locations:
            almacenes=almacenes+str(location)+','
            s_loca.append(location)
        almacenes=almacenes[:-1]+'}'


        self.env.cr.execute("""
        drop table if exists tree_view_kardex_fisico;
        create table tree_view_kardex_fisico AS
        select row_number() OVER () as id,
        slo.complete_name as u_origen,
        sld.complete_name as u_destino,
        sw.name as almacen,
        tok.name as t_opera,
        pc.name as categoria,
        pt.name as producto,
        pp.default_code as cod_pro,
        uom.name as unidad,
        case
            when sp.use_kardex_date then sp.kardex_date::timestamp without time zone
            else sm.date::timestamp without time zone
        end as fecha,
        case
            when sp.name != '' then sp.name
            else si.name
        end as doc_almacen,
        case 
            when spt.code = 'incoming' or coalesce(spt.code , '') = '' then sm.product_qty
            else 0
        end as entrada,
        case 
            when spt.code = 'incoming' or coalesce(spt.code , '') = '' then 0
            else sm.product_qty
        end as salida,
        case 
            when spt.code = 'incoming' or coalesce(spt.code , '') = '' then sld.complete_name
            else slo.complete_name
        end as orden_ubicacion		
        from stock_move sm
        left join stock_move_line sml ON sm.id = sml.move_id
        left join stock_location slo ON sml.location_id = slo.id
        left join stock_location sld ON sml.location_dest_id = sld.id
        left join stock_warehouse sw ON sm.warehouse_id = sw.id
        left join stock_picking sp ON sp.id = sm.picking_id
        left join stock_picking_type spt ON sp.picking_type_id = spt.id
        left join type_operation_kardex tok ON tok.id = sp.type_operation_sunat_id
        left join product_product pp ON sm.product_id = pp.id
        left join product_template pt ON pp.product_tmpl_id = pt.id
        left join product_category pc ON pc.id = pt.categ_id
        left join uom_uom as uom ON uom.id = pt.uom_id
        left join stock_valuation_layer svl ON svl.stock_move_id = sm.id
        left join stock_inventory si ON sm.inventory_id = si.id
        where sm.product_id in """ +str(tuple(s_prod))+ """
        and sm.date >='""" + date_ini + """' and sm.date <='""" + date_fin + """'
        and (sml.location_id in """ +str(tuple(s_loca))+ """ or sml.location_dest_id in """ +str(tuple(s_loca))+ """ and sm.product_id in """ +str(tuple(s_prod))+ """)
        and sm.product_id in """ +str(tuple(s_prod))+ """
        and svl.stock_landed_cost_id is NULL
        order by orden_ubicacion, fecha
        """)


# 		self.env.cr.execute("""
# 			drop table if exists tree_view_kardex_fisico;
# 			create table tree_view_kardex_fisico AS
# 			select row_number() OVER () as id,
# origen.complete_name AS u_origen,
# destino.complete_name AS u_destino,
# almacen.complete_name AS almacen,
# vstf.motivo_guia::varchar AS t_opera,
# pc.name as categoria,
# coalesce(it.value,pt.name) as producto,
# pp.default_code as cod_pro,
# pu.name as unidad,
# vstf.fecha as fecha,
# sp.name as doc_almacen,
# vstf.entrada as entrada,
# vstf.salida as salida
# from
# (
# select vst_kardex_fisico.date::date as fecha,vst_kardex_fisico.location_id as origen, vst_kardex_fisico.location_dest_id as destino, vst_kardex_fisico.location_dest_id as almacen, vst_kardex_fisico.product_qty as entrada, 0 as salida,vst_kardex_fisico.id  as stock_move,vst_kardex_fisico.guia as motivo_guia,vst_kardex_fisico.product_id,vst_kardex_fisico.estado from vst_kardex_fisico
# join stock_move sm on sm.id = vst_kardex_fisico.id
# join stock_picking sp on sm.picking_id = sp.id
# join stock_location l_o on l_o.id = vst_kardex_fisico.location_id
# join stock_location l_d on l_d.id = vst_kardex_fisico.location_dest_id
# where ( (l_o.usage = 'internal' and l_o.usage = 'internal' )  or ( l_o.usage != 'internal' or l_o.usage != 'internal' ) )
# union all
# select vst_kardex_fisico.date::date as fecha,vst_kardex_fisico.location_id as origen, vst_kardex_fisico.location_dest_id as destino, vst_kardex_fisico.location_id as almacen, 0 as entrada, vst_kardex_fisico.product_qty as salida,vst_kardex_fisico.id  as stock_move ,vst_kardex_fisico.guia as motivo_guia ,vst_kardex_fisico.product_id ,vst_kardex_fisico.estado from vst_kardex_fisico
# ) as vstf
# inner join stock_location origen on origen.id = vstf.origen
# inner join stock_location destino on destino.id = vstf.destino
# inner join stock_location almacen on almacen.id = vstf.almacen
# inner join product_product pp on pp.id = vstf.product_id
# inner join product_template pt on pt.id = pp.product_tmpl_id
# inner join product_category pc on pc.id = pt.categ_id
# inner join uom_uom pu on pu.id = pt.uom_id
# inner join stock_move sm on sm.id = vstf.stock_move
# inner join stock_picking sp on sp.id = sm.picking_id
# left join ir_translation it ON pt.id = it.res_id and it.name = 'product.template,name' and it.lang = 'es_PE' and it.state = 'translated'
# where vstf.fecha >='""" +str(date_ini)+ """' and vstf.fecha <='""" +str(date_fin)+ """'
# and vstf.product_id in """ +str(tuple(s_prod))+ """
# and vstf.almacen in """ +str(tuple(s_loca))+ """
# and vstf.estado = 'done'
# and almacen.usage = 'internal'
# order by
# almacen.id,pp.id,vstf.fecha,vstf.entrada desc;
# 		""")



        return {
            'name': 'Kardex Fisico',
            'type': 'ir.actions.act_window',
            'res_model': 'tree.view.kardex.fisico',
            'view_mode': 'tree',
            'target': 'main',
            'views': [(False, 'tree')],
        }




    def do_csvtoexcel(self):
        cad = ""

        s_prod = [-1,-1,-1]
        s_loca = [-1,-1,-1]
        if self.alllocations == True:
            locat_ids = self.env['stock.location'].search( [('usage','in',('internal','inventory','transit','procurement','production'))] )
            lst_locations = locat_ids.ids
        else:
            lst_locations = self.location_ids.ids
        lst_products  = self.products_ids.ids
        productos='{'
        almacenes='{'
        date_ini=self.fini.strftime("%Y-%m-%d")
        date_fin=self.ffin.strftime("%Y-%m-%d 23:59:59")
        if self.allproducts:
            lst_products = self.env['product.product'].with_context(active_test=False).search([]).ids

        else:
            lst_products = self.products_ids.ids

        if len(lst_products) == 0:
            raise osv.except_osv('Alerta','No existen productos seleccionados')

        for producto in lst_products:
            productos=productos+str(producto)+','
            s_prod.append(producto)
        productos=productos[:-1]+'}'
        for location in lst_locations:
            almacenes=almacenes+str(location)+','
            s_loca.append(location)
        almacenes=almacenes[:-1]+'}'



        import io
        from xlsxwriter.workbook import Workbook
        output = io.BytesIO()

        my_path = os.path.abspath(os.path.dirname(__file__))
        direccion = os.path.join(my_path, '../static/')

        # direccion = self.env['main.parameter'].search([])[0].dir_create_file
        workbook = Workbook(direccion +'kardex_producto.xlsx')
        worksheet = workbook.add_worksheet("Kardex")
        bold = workbook.add_format({'bold': True})
        bold.set_font_size(8)
        normal = workbook.add_format()
        boldbord = workbook.add_format({'bold': True})
        boldbord.set_border(style=2)
        boldbord.set_align('center')
        boldbord.set_align('vcenter')
        boldbord.set_text_wrap()
        boldbord.set_font_size(8)
        boldbord.set_bg_color('#DCE6F1')

        especial1 = workbook.add_format({'bold': True})
        especial1.set_align('center')
        especial1.set_align('vcenter')
        especial1.set_text_wrap()
        especial1.set_font_size(15)

        numbertres = workbook.add_format({'num_format':'0.000'})
        numberdos = workbook.add_format({'num_format':'0.00'})
        numberseis = workbook.add_format({'num_format':'0.000000'})
        numberseis.set_font_size(8)
        numberocho = workbook.add_format({'num_format':'0.00000000'})
        numberocho.set_font_size(8)
        bord = workbook.add_format()
        bord.set_border(style=1)
        bord.set_font_size(8)
        numberdos.set_border(style=1)
        numberdos.set_font_size(8)
        numbertres.set_border(style=1)
        numberseis.set_border(style=1)
        numberocho.set_border(style=1)
        numberdosbold = workbook.add_format({'num_format':'0.00','bold':True})
        numberdosbold.set_font_size(8)
        x= 10
        tam_col = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        tam_letra = 1.2
        y=0

        def _cabecera(self,x,y):
            worksheet.merge_range(1+y,5,1+y,10, "KARDEX FISICO", especial1)
            worksheet.write(2+y,0,'FECHA INICIO:',bold)
            worksheet.write(3+y,0,'FECHA FIN:',bold)

            worksheet.write(2+y,1,str(self.fini))
            worksheet.write(3+y,1,str(self.ffin))
            import datetime

            worksheet.merge_range(8+y,0,9+y,0, u"Ubicacion Origen",boldbord)
            worksheet.merge_range(8+y,1,9+y,1, u"Ubicacion Destino",boldbord)
            worksheet.merge_range(8+y,2,9+y,2, u"Almacen",boldbord)
            worksheet.merge_range(8+y,3,9+y,3, u"Tipo de Operación",boldbord)
            worksheet.merge_range(8+y,4,9+y,4, u"Categoria",boldbord)

            worksheet.merge_range(8+y,5,9+y,5, u"Producto",boldbord)
            worksheet.merge_range(8+y,6,9+y,6, u"Codigo P.",boldbord)
            worksheet.merge_range(8+y,7,9+y,7, u"Unidad",boldbord)

            worksheet.merge_range(8+y,8,9+y,8, u"Fecha",boldbord)

            worksheet.merge_range(8+y,9,9+y,9, u"Doc. Almacen",boldbord)

            worksheet.write(8+y,10, "Ingreso",boldbord)
            worksheet.write(9+y,10, "Cantidad",boldbord)
            worksheet.write(8+y,11, "Salida",boldbord)
            worksheet.write(9+y,11, "Cantidad",boldbord)
            worksheet.write(8+y,12, "Saldo",boldbord)
            worksheet.write(9+y,12, "Cantidad",boldbord)
            x += 10
            return x

        _cabecera(self,x,0)

        self.env.cr.execute("""
        select
        slo.complete_name as "Ubicación Origen",
        sld.complete_name as "Ubicación Destino",
        sw.name as "Almacén",
        tok.name as "Tipo de Operación",
        pc.name as "Categoría",
        pt.name as "Producto",
        pp.default_code as "Código de Producto",
        uom.name as "Unidad",
        case
            when sp.use_kardex_date then sp.kardex_date::timestamp without time zone
            else sm.date::timestamp without time zone
        end as "Fecha",
        case
            when sp.name != '' then sp.name
            else si.name
        end as "Doc. Almacén",
        case 
            when spt.code = 'incoming' or coalesce(spt.code , '') = '' then sm.product_qty
            else 0
        end as "Entrada",
        case 
            when spt.code = 'incoming' or coalesce(spt.code , '') = '' then 0
            else sm.product_qty
        end as "Salida",
        svl.unit_cost + sm.kardex_price_unit as "Precio Unitario",
        sp.picking_type_id as "Tipo de Picking"
        from stock_move sm
        left join stock_move_line sml ON sm.id = sml.move_id
        left join stock_location slo ON sml.location_id = slo.id
        left join stock_location sld ON sml.location_dest_id = sld.id
        left join stock_warehouse sw ON sm.warehouse_id = sw.id
        left join stock_picking sp ON sp.id = sm.picking_id
        left join stock_picking_type spt ON sp.picking_type_id = spt.id
        left join type_operation_kardex tok ON tok.id = sp.type_operation_sunat_id
        left join product_product pp ON sm.product_id = pp.id
        left join product_template pt ON pp.product_tmpl_id = pt.id
        left join product_category pc ON pc.id = pt.categ_id
        left join uom_uom as uom ON uom.id = pt.uom_id
        left join stock_valuation_layer svl ON svl.stock_move_id = sm.id
        left join stock_inventory si ON sm.inventory_id = si.id
        where sm.product_id in """ +str(tuple(s_prod))+ """
        and sm.date >='""" + date_ini + """' and sm.date <='""" + date_fin + """'
        and (sml.location_id in """ +str(tuple(s_loca))+ """ or sml.location_dest_id in """ +str(tuple(s_loca))+ """ and sm.product_id in """ +str(tuple(s_prod))+ """)
        and sm.product_id in """ +str(tuple(s_prod))+ """
        and svl.stock_landed_cost_id is NULL
        order by "Fecha"
        """)



        ingreso1= 0
        ingreso2= 0
        salida1= 0
        salida2= 0

        saldo = 0
        almacen = None
        producto = None
        for line in self.env.cr.fetchall():
            if almacen == None:
                almacen = (line[2] if line[2] else '')
                ubicacion = (line[0] if line[11]>0 else line[1])
                producto = (line[5] if line[5] else '')
                saldo = line[10] - line[11]
            elif almacen != (line[2] if line[2] else '') or producto != (line[5] if line[5] else '') or ubicacion != (line[0] if line[11]>0 else line[1]):
                y = x + 2
                x = _cabecera(self,x,y) + 2
                almacen = (line[2] if line[2] else '')
                ubicacion = (line[0] if line[11]>0 else line[1])
                producto = (line[5] if line[5] else '')
                saldo = line[10] - line[11]

                # workbook.close()
                # f = open(direccion + 'kardex_producto.xlsx', 'rb')
                # return self.env['popup.it'].get_file('Kardex_Fisico.xlsx',base64.encodestring(b''.join(f.readlines())))

            else:
                saldo = saldo + line[10] - line[11]

            worksheet.write(x,0,line[0] if line[0] else '' ,bord )
            worksheet.write(x,1,line[1] if line[1] else '' ,bord )
            worksheet.write(x,2,line[2] if line[2] else '' ,bord )
            worksheet.write(x,3,line[3] if line[3] else '' ,bord )
            worksheet.write(x,4,line[4] if line[4] else '' ,bord )
            worksheet.write(x,5,line[5] if line[5] else '' ,bord )
            worksheet.write(x,6,line[6] if line[6] else '' ,bord )
            worksheet.write(x,7,line[7] if line[7] else '' ,bord )
            user_tz = pytz.timezone(self.env.context.get('tz'))
            date_to_xls = pytz.utc.localize(line[8]).astimezone(user_tz)
            worksheet.write(x,8,date_to_xls.strftime("%d/%m/%Y") if date_to_xls else '' ,bord )
            # worksheet.write(x,8,line[8] if line[8] else '' ,bord )
            worksheet.write(x,9,line[9] if line[9] else '' ,bord )
            worksheet.write(x,10,line[10] if line[10] else 0 ,numberdos )
            worksheet.write(x,11,line[11] if line[11] else 0 ,numberdos )
            worksheet.write(x,12,saldo ,numberdos )

            x = x +1

        tam_col = [11,11,5,5,7,5,11,11,11,11,11,11,11,11,11,11,11,11,11,11,11,11,11]


        worksheet.set_column('A:A', tam_col[0])
        worksheet.set_column('B:B', tam_col[1])
        worksheet.set_column('C:C', tam_col[2])
        worksheet.set_column('D:D', tam_col[3])
        worksheet.set_column('E:E', tam_col[4])
        worksheet.set_column('F:F', tam_col[5])
        worksheet.set_column('G:G', tam_col[6])
        worksheet.set_column('H:H', tam_col[7])
        worksheet.set_column('I:I', tam_col[8])
        worksheet.set_column('J:J', tam_col[9])
        worksheet.set_column('K:K', tam_col[10])
        worksheet.set_column('L:L', tam_col[11])
        worksheet.set_column('M:M', tam_col[12])
        worksheet.set_column('N:N', tam_col[13])
        worksheet.set_column('O:O', tam_col[14])
        worksheet.set_column('P:P', tam_col[15])
        worksheet.set_column('Q:Q', tam_col[16])
        worksheet.set_column('R:R', tam_col[17])
        worksheet.set_column('S:S', tam_col[18])
        worksheet.set_column('T:Z', tam_col[19])

        workbook.close()


        f = open(direccion + 'kardex_producto.xlsx', 'rb')

        return self.env['popup.it'].get_file('Kardex_Fisico.xlsx',base64.encodestring(b''.join(f.readlines())))





    def do_csv(self):
        data = self.read()
        cad=""
        if data[0]['products_ids']==[]:
            if data[0]['allproducts']:
                if data[0]['allproducts']==False:
                    raise osv.except_osv('Alerta','No existen productos seleccionados')
                    return
                else:
                    #prods= self.pool.get('product.product').search(cr,uid,[])
                    lst_products  = self.env['product.product'].search([]).ids
            else:
                raise osv.except_osv('Alerta','No existen productos seleccionados')
                return
        else:
            lst_products  = data[0]['products_ids']

        s_prod = [-1,-1,-1]
        s_loca = [-1,-1,-1]

        lst_locations = data[0]['location_ids']
        productos='{0,'
        almacenes='{0,'
        date_ini=data[0]['fini']
        date_fin=data[0]['ffin']
        if 'allproducts' in data[0]:
            if data[0]['allproducts']:
                lst_products = self.env['product.product'].with_context(active_test=False).search([]).ids
            else:
                lst_products  = data[0]['products_ids']
        else:
            lst_products  = data[0]['products_ids']

        if 'alllocations' in data[0]:
            lst_locations = self.env['stock.location'].search([]).ids

        for producto in lst_products:
            productos=productos+str(producto)+','
            s_prod.append(producto)
        productos=productos[:-1]+'}'
        for location in lst_locations:
            almacenes=almacenes+str(location)+','
            s_loca.append(location)
        almacenes=almacenes[:-1]+'}'
        direccion = self.env['main.parameter'].search([])[0].dir_create_file


        cadf=u"""



        copy (select
origen.complete_name AS "Ubicación Origen",
destino.complete_name AS "Ubicación Destino",
almacen.complete_name AS "Almacén",
vstf.motivo_guia AS "Tipo de operación",
pc.name as "Categoria",
coalesce(it.value,pt.name) as "Producto",
pt.default_code as "Codigo P.",
pu.name as "unidad",
vstf.fecha as "Fecha",
sp.name as "Doc. Almacén",
vstf.entrada as "Entrada",
vstf.salida as "Salida",
''::varchar as pedido_compra
from
(
select vst_kardex_fisico.date::date as fecha,vst_kardex_fisico.location_id as origen,
vst_kardex_fisico.location_dest_id as destino, vst_kardex_fisico.location_dest_id as almacen,
vst_kardex_fisico.product_qty as entrada, 0 as salida,vst_kardex_fisico.id  as stock_move,
vst_kardex_fisico.guia as motivo_guia,vst_kardex_fisico.product_id,
vst_kardex_fisico.estado from vst_kardex_fisico
join stock_move sm on sm.id = vst_kardex_fisico.id
join stock_picking sp on sm.picking_id = sp.id
join stock_location l_o on l_o.id = vst_kardex_fisico.location_id
join stock_location l_d on l_d.id = vst_kardex_fisico.location_dest_id
where ( (l_o.usage = 'internal' and l_o.usage = 'internal'  )  or ( l_o.usage != 'internal' or l_o.usage != 'internal' ) )

union all
select date::date as fecha, location_id as origen, location_dest_id as destino, location_id as almacen, 0 as entrada, product_qty as salida,id  as stock_move ,guia as motivo_guia ,product_id , estado from vst_kardex_fisico
) as vstf
inner join stock_location origen on origen.id = vstf.origen
inner join stock_location destino on destino.id = vstf.destino
inner join stock_location almacen on almacen.id = vstf.almacen
inner join product_product pp on pp.id = vstf.product_id
inner join product_template pt on pt.id = pp.product_tmpl_id
inner join product_category pc on pc.id = pt.categ_id
inner join uom_uom pu on pu.id = pt.uom_id
inner join stock_move sm on sm.id = vstf.stock_move
inner join stock_picking sp on sp.id = sm.picking_id
left join ir_translation it ON pt.id = it.res_id and it.name = 'product.template,name' and it.lang = 'es_PE' and it.state = 'translated'
where vstf.fecha >='""" +str(date_ini)+ u"""' and vstf.fecha <='""" +str(date_fin)+ u"""'
and vstf.product_id in """ +str(tuple(s_prod))+ u"""
and vstf.almacen in """ +str(tuple(s_loca))+ u"""
and vstf.estado = 'done'
and almacen.usage = 'internal'
order by
almacen.id,pp.id,vstf.fecha,vstf.entrada desc


) to '"""+direccion+u"""/kardex.csv'  WITH DELIMITER ',' CSV HEADER
        """
        
        self.env.cr.execute(cadf)
        import gzip
        import shutil

        f = open(direccion+'kardex.csv', 'rb')

        return self.env['popup.it'].get_file('Kardex_Fisico.csv',base64.encodestring(b''.join(f.readlines())))







class make_kardex_product(models.TransientModel):
    _name = "make.kardex.product"

    fini= fields.Date('Fecha inicial',required=True)
    ffin= fields.Date('Fecha final',required=True)
    location_ids=fields.Many2many('stock.location','rel_kardex_location_product','location_id','kardex_id','Ubicacion',required=True)
    destino = fields.Selection([('csv','CSV'),('crt','Pantalla')],'Destino')
    check_fecha = fields.Boolean('Editar Fecha')

    location = fields.Many2one('stock.location','Ubicación')

    alllocations = fields.Boolean('Todos los almacenes',default=True)

    format_13_1 = fields.Boolean(string='Formato 13.1')

    fecha_ini_mod = fields.Date('Fecha Inicial')
    fecha_fin_mod = fields.Date('Fecha Final')
    analizador = fields.Boolean('Analizador')

    @api.onchange('fecha_ini_mod')
    def onchange_fecha_ini_mod(self):
        self.fini = self.fecha_ini_mod


    @api.onchange('fecha_fin_mod')
    def onchange_fecha_fin_mod(self):
        self.ffin = self.fecha_fin_mod


    @api.model
    def default_get(self, fields):
        res = super(make_kardex_product, self).default_get(fields)
        import datetime
        fecha_hoy = str(datetime.datetime.now())[:10]
        fecha_inicial = fecha_hoy[:4] + '-01-01'
        res.update({'fecha_ini_mod':fecha_inicial})
        res.update({'fecha_fin_mod':fecha_hoy})
        res.update({'fini':fecha_inicial})
        res.update({'ffin':fecha_hoy})

        #locat_ids = self.pool.get('stock.location').search(cr, uid, [('usage','in',('internal','inventory','transit','procurement','production'))])
        locat_ids = self.env['stock.location'].search([('usage','in',('internal','inventory','transit','procurement','production'))])
        locat_ids = [elemt.id for elemt in locat_ids]
        res.update({'location_ids':[(6,0,locat_ids)]})
        return res

    @api.onchange('alllocations')
    def onchange_alllocations(self):
        if self.alllocations == True:
            locat_ids = self.env['stock.location'].search( [('usage','in',('internal','inventory','transit','procurement','production'))] )
            self.location_ids = [(6,0,locat_ids.ids)]
        else:
            self.location_ids = [(6,0,[])]




    def do_popup(self):		
        cad = ""

        s_prod = [-1,-1,-1]
        s_loca = [-1,-1,-1]
        if self.alllocations == True:
            locat_ids = self.env['stock.location'].search( [('usage','in',('internal','inventory','transit','procurement','production'))] )
            lst_locations = locat_ids.ids
        else:
            lst_locations = self.location_ids.ids
        lst_products  = [self.env.context['active_id']]
        productos='{'
        almacenes='{'
        date_ini=self.fini.strftime("%Y-%m-%d")
        date_fin=self.ffin.strftime("%Y-%m-%d 23:59:59")
        

        if len(lst_products) == 0:
            raise osv.except_osv('Alerta','No existen productos seleccionados')

        for producto in lst_products:
            productos=productos+str(producto)+','
            s_prod.append(producto)
        productos=productos[:-1]+'}'
        for location in lst_locations:
            almacenes=almacenes+str(location)+','
            s_loca.append(location)
        almacenes=almacenes[:-1]+'}'



        self.env.cr.execute("""
        drop table if exists tree_view_kardex_fisico;
        create table tree_view_kardex_fisico AS
        select row_number() OVER () as id,
        slo.complete_name as u_origen,
        sld.complete_name as u_destino,
        sw.name as almacen,
        tok.name as t_opera,
        pc.name as categoria,
        pt.name as producto,
        pp.default_code as cod_pro,
        uom.name as unidad,
        case
            when sp.use_kardex_date then sp.kardex_date::timestamp without time zone
            else sm.date::timestamp without time zone
        end as fecha,
        case
            when sp.name != '' then sp.name
            else si.name
        end as doc_almacen,
        case 
            when spt.code = 'incoming' or coalesce(spt.code , '') = '' then sm.product_qty
            else 0
        end as entrada,
        case 
            when spt.code = 'incoming' or coalesce(spt.code , '') = '' then 0
            else sm.product_qty
        end as salida,
        case 
            when spt.code = 'incoming' or coalesce(spt.code , '') = '' then sld.complete_name
            else slo.complete_name
        end as orden_ubicacion		
        from stock_move sm
        left join stock_move_line sml ON sm.id = sml.move_id
        left join stock_location slo ON sml.location_id = slo.id
        left join stock_location sld ON sml.location_dest_id = sld.id
        left join stock_warehouse sw ON sm.warehouse_id = sw.id
        left join stock_picking sp ON sp.id = sm.picking_id
        left join stock_picking_type spt ON sp.picking_type_id = spt.id
        left join type_operation_kardex tok ON tok.id = sp.type_operation_sunat_id
        left join product_product pp ON sm.product_id = pp.id
        left join product_template pt ON pp.product_tmpl_id = pt.id
        left join product_category pc ON pc.id = pt.categ_id
        left join uom_uom as uom ON uom.id = pt.uom_id
        left join stock_valuation_layer svl ON svl.stock_move_id = sm.id
        left join stock_inventory si ON sm.inventory_id = si.id
        where sm.product_id in """ +str(tuple(s_prod))+ """
        and sm.date >='""" + date_ini + """' and sm.date <='""" + date_fin + """'
        and (sml.location_id in """ +str(tuple(s_loca))+ """ or sml.location_dest_id in """ +str(tuple(s_loca))+ """ and sm.product_id in """ +str(tuple(s_prod))+ """)
        and sm.product_id in """ +str(tuple(s_prod))+ """
        and svl.stock_landed_cost_id is NULL
        order by orden_ubicacion, fecha
        """)



        return {
            'name': 'Kardex Fisico',
            'type': 'ir.actions.act_window',
            'res_model': 'tree.view.kardex.fisico',
            'view_mode': 'tree',
            'views': [(False, 'tree')],
        }

    def do_popup_libro(self,ids):		
        cad = ""

        s_prod = [-1,-1,-1]
        s_loca = [-1,-1,-1]
        if self.alllocations == True:
            locat_ids = self.env['stock.location'].search( [('usage','in',('internal','inventory','transit','procurement','production'))] )
            lst_locations = locat_ids.ids
        else:
            lst_locations = self.location_ids.ids
        lst_products  = [ids]
        productos='{'
        almacenes='{'
        date_ini=self.fini.strftime("%Y-%m-%d")
        date_fin=self.ffin.strftime("%Y-%m-%d 23:59:59")
        

        if len(lst_products) == 0:
            raise osv.except_osv('Alerta','No existen productos seleccionados')

        for producto in lst_products:
            productos=productos+str(producto)+','
            s_prod.append(producto)
        productos=productos[:-1]+'}'
        for location in lst_locations:
            almacenes=almacenes+str(location)+','
            s_loca.append(location)
        almacenes=almacenes[:-1]+'}'



        self.env.cr.execute("""
        drop table if exists tree_view_kardex_fisico;
        create table tree_view_kardex_fisico AS
        select row_number() OVER () as id,
        slo.complete_name as u_origen,
        sld.complete_name as u_destino,
        sw.name as almacen,
        tok.name as t_opera,
        pc.name as categoria,
        pt.name as producto,
        pp.default_code as cod_pro,
        uom.name as unidad,
        case
            when sp.use_kardex_date then sp.kardex_date::timestamp without time zone
            else sm.date::timestamp without time zone
        end as fecha,
        case
            when sp.name != '' then sp.name
            else si.name
        end as doc_almacen,
        case 
            when spt.code = 'incoming' or coalesce(spt.code , '') = '' then sm.product_qty
            else 0
        end as entrada,
        case 
            when spt.code = 'incoming' or coalesce(spt.code , '') = '' then 0
            else sm.product_qty
        end as salida,
        case 
            when spt.code = 'incoming' or coalesce(spt.code , '') = '' then sld.complete_name
            else slo.complete_name
        end as orden_ubicacion		
        from stock_move sm
        left join stock_move_line sml ON sm.id = sml.move_id
        left join stock_location slo ON sml.location_id = slo.id
        left join stock_location sld ON sml.location_dest_id = sld.id
        left join stock_warehouse sw ON sm.warehouse_id = sw.id
        left join stock_picking sp ON sp.id = sm.picking_id
        left join stock_picking_type spt ON sp.picking_type_id = spt.id
        left join type_operation_kardex tok ON tok.id = sp.type_operation_sunat_id
        left join product_product pp ON sm.product_id = pp.id
        left join product_template pt ON pp.product_tmpl_id = pt.id
        left join product_category pc ON pc.id = pt.categ_id
        left join uom_uom as uom ON uom.id = pt.uom_id
        left join stock_valuation_layer svl ON svl.stock_move_id = sm.id
        left join stock_inventory si ON sm.inventory_id = si.id
        where sm.product_id in """ +str(tuple(s_prod))+ """
        and sm.date >='""" + date_ini + """' and sm.date <='""" + date_fin + """'
        and (sml.location_id in """ +str(tuple(s_loca))+ """ or sml.location_dest_id in """ +str(tuple(s_loca))+ """ and sm.product_id in """ +str(tuple(s_prod))+ """)
        and sm.product_id in """ +str(tuple(s_prod))+ """
        and svl.stock_landed_cost_id is NULL
        order by orden_ubicacion, fecha
        """)






    def do_csvtoexcel(self):
        if self.format_13_1:
            return self.do_csvtoexcel_13_1()
        else:
            return self.do_csvtoexcel_commercial()

    def do_csvtoexcel_commercial_libro(self,ids):
        cad = ""

        s_prod = [-1,-1,-1]
        s_loca = [-1,-1,-1]
        if self.alllocations == True:
            locat_ids = self.env['stock.location'].search( [('usage','in',('internal','inventory','transit','procurement','production'))] )
            lst_locations = locat_ids.ids
        else:
            lst_locations = self.location_ids.ids
        lst_products  = [ids]
        productos='{'
        almacenes='{'
        date_ini=self.fini.strftime("%Y-%m-%d")
        date_fin=self.ffin.strftime("%Y-%m-%d 23:59:59")
        

        if len(lst_products) == 0:
            raise osv.except_osv('Alerta','No existen productos seleccionados')

        for producto in lst_products:
            productos=productos+str(producto)+','
            s_prod.append(producto)
        productos=productos[:-1]+'}'
        for location in lst_locations:
            almacenes=almacenes+str(location)+','
            s_loca.append(location)
        almacenes=almacenes[:-1]+'}'



        import io
        from xlsxwriter.workbook import Workbook
        output = io.BytesIO()
        product = self.env['product.product'].browse(ids)
        import datetime



        sql = """
        select
        slo.complete_name as "Ubicación Origen",
        sld.complete_name as "Ubicación Destino",
        sw.name as "Almacén",
        case
            when si.is_initial_sil = True then 'SALDO INICIAL'
            else
                case
                    when sm.inventory_id is not NULL then 'AJUSTE POR DIFERENCIA DE INVENTARIO'
                    else tok.name
                end
        end as "Tipo de Operación",
        pc.name as "Categoría",
        pt.name as "Producto",
        pp.default_code as "Código de Producto",
        uom.name as "Unidad",
        case
            when sp.invoice_id is not NULL then aml.invoice_date
            else
                case
                    when sp.use_kardex_date then sp.kardex_date
                    else 
                        case
                            when sm.inventory_id is NULL then sm.date
                            else
                                case
                                    when si.accounting_date is NULL then si.date
                                    else si.accounting_date
                                end
                        end
                end
        end as "Fecha",
        case
            when sp.invoice_id is not NULL then aml.invoice_name
            else
                case
                    when sp.name != '' then sp.name
                    else si.name
                end
        end as "Doc. Almacén",
        case 
            when spt.code = 'incoming' or coalesce(spt.code , '') = '' then sm.product_qty
            else 0
        end as "Entrada",
        case 
            when spt.code = 'incoming' or coalesce(spt.code , '') = '' then 0
            else sm.product_qty
        end as "Salida",
        svl.unit_cost + sm.kardex_price_unit as "Precio Unitario",
        sp.picking_type_id as "Tipo de Picking",
        sm.inventory_id as "Ajuste",
        si.is_initial_sil
        from stock_move sm
        left join stock_move_line sml ON sm.id = sml.move_id
        left join stock_location slo ON sml.location_id = slo.id
        left join stock_location sld ON sml.location_dest_id = sld.id
        left join stock_warehouse sw ON sm.warehouse_id = sw.id
        left join stock_picking sp ON sp.id = sm.picking_id
        left join stock_picking_type spt ON sp.picking_type_id = spt.id
        left join type_operation_kardex tok ON tok.id = sp.type_operation_sunat_id
        left join product_product pp ON sm.product_id = pp.id
        left join product_template pt ON pp.product_tmpl_id = pt.id
        left join product_category pc ON pc.id = pt.categ_id
        left join uom_uom as uom ON uom.id = pt.uom_id
        left join stock_valuation_layer svl ON svl.stock_move_id = sm.id
        left join (select *, si.id as idsi, sil.is_initial as is_initial_sil from stock_inventory si
        left join stock_inventory_line sil ON sil.inventory_id = si.id where product_id in """ +str(tuple(s_prod))+ """ and si.state = 'done') si ON sm.inventory_id = si.idsi
        left join (select *, am.id as idam, am.ref as invoice_name from account_move am 
        left join account_move_line aml ON aml.move_id = am.id
        where aml.exclude_from_invoice_tab = false and aml.product_id in """ +str(tuple(s_prod))+ """) as aml ON sp.invoice_id = aml.idam
        where sm.product_id in """ +str(tuple(s_prod))+ """
        and sm.date >='""" + date_ini + """' and sm.date <='""" + date_fin + """'
        and (sml.location_id in """ +str(tuple(s_loca))+ """ or sml.location_dest_id in """ +str(tuple(s_loca))+ """)
        and svl.stock_landed_cost_id is NULL
        and sm.state = 'done'
        order by "Fecha"
        """
        self.env.cr.execute(sql)

        return self.env.cr.fetchall()
        
    def do_csvtoexcel_commercial(self):
        cad = ""

        s_prod = [-1,-1,-1]
        s_loca = [-1,-1,-1]
        if self.alllocations == True:
            locat_ids = self.env['stock.location'].search( [('usage','in',('internal','inventory','transit','procurement','production'))] )
            lst_locations = locat_ids.ids
        else:
            lst_locations = self.location_ids.ids
        lst_products  = [self.env.context['active_id']]
        productos='{'
        almacenes='{'
        date_ini=self.fini.strftime("%Y-%m-%d")
        date_fin=self.ffin.strftime("%Y-%m-%d 23:59:59")
        

        if len(lst_products) == 0:
            raise osv.except_osv('Alerta','No existen productos seleccionados')

        for producto in lst_products:
            productos=productos+str(producto)+','
            s_prod.append(producto)
        productos=productos[:-1]+'}'
        for location in lst_locations:
            almacenes=almacenes+str(location)+','
            s_loca.append(location)
        almacenes=almacenes[:-1]+'}'



        import io
        from xlsxwriter.workbook import Workbook
        output = io.BytesIO()

        my_path = os.path.abspath(os.path.dirname(__file__))
        #my_path = "/opt/odoo/addons/jp_kardex_valorizado/static"
        path = os.path.join(my_path, '../static/')

        #direccion = self.env['main.parameter'].search([])[0].dir_create_file
        # workbook = Workbook(direccion +'kardex_producto.xlsx')
        workbook = Workbook(path +'kardex_producto' + self.env.user.name + '.xlsx')
        worksheet = workbook.add_worksheet("Kardex")
        bold = workbook.add_format({'bold': True})
        bold.set_font_size(8)
        normal = workbook.add_format()
        boldbord = workbook.add_format({'bold': True})
        boldbord.set_border(style=2)
        boldbord.set_align('center')
        boldbord.set_align('vcenter')
        boldbord.set_text_wrap()
        boldbord.set_font_size(8)
        boldbord.set_bg_color('#DCE6F1')

        especial1 = workbook.add_format({'bold': True})
        especial1.set_align('center')
        especial1.set_align('vcenter')
        especial1.set_text_wrap()
        especial1.set_font_size(15)

        numbertres = workbook.add_format({'num_format':'0.000'})
        numberdos = workbook.add_format({'num_format':'0.00'})
        numberseis = workbook.add_format({'num_format':'0.000000'})
        numberseis.set_font_size(8)
        numberocho = workbook.add_format({'num_format':'0.00000000'})
        numberocho.set_font_size(8)
        bord = workbook.add_format()
        bord.set_border(style=1)
        bord.set_font_size(8)
        numberdos.set_border(style=1)
        numberdos.set_font_size(8)
        numbertres.set_border(style=1)
        numberseis.set_border(style=1)
        numberocho.set_border(style=1)
        numberdosbold = workbook.add_format({'num_format':'0.00','bold':True})
        numberdosbold.set_font_size(8)
        x= 7
        tam_col = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        tam_letra = 1.2

        product = self.env['product.product'].browse(self.env.context['active_id'])

        worksheet.merge_range(1,5,1,10, "KARDEX FISICO - " + product.name, especial1)
        worksheet.write(2,0,'FECHA INICIO:',bold)
        worksheet.write(3,0,'FECHA FIN:',bold)

        worksheet.write(2,1,str(self.fini))
        worksheet.write(3,1,str(self.ffin))
        import datetime

        worksheet.merge_range(5,0,6,0, u"Ubicacion Origen",boldbord)
        worksheet.merge_range(5,1,6,1, u"Ubicacion Destino",boldbord)
        worksheet.merge_range(5,2,6,2, u"Almacen",boldbord)
        worksheet.merge_range(5,3,6,3, u"Tipo de Operación",boldbord)
        worksheet.merge_range(5,4,6,4, u"Categoria",boldbord)

        worksheet.merge_range(5,5,6,5, u"Producto",boldbord)
        worksheet.merge_range(5,6,6,6, u"Codigo P.",boldbord)
        worksheet.merge_range(5,7,6,7, u"Unidad",boldbord)

        worksheet.merge_range(5,8,6,8, u"Fecha",boldbord)

        worksheet.merge_range(5,9,6,9, u"Doc. Almacen",boldbord)

        worksheet.merge_range(5,10,5,12, "Ingreso",boldbord)
        worksheet.write(6,10, "Cantidad",boldbord)
        worksheet.write(6,11, "Costo. Unitario",boldbord)
        worksheet.write(6,12, "Costo Total",boldbord)
        worksheet.merge_range(5,13,5,15, "Salida",boldbord)
        worksheet.write(6,13, "Cantidad",boldbord)
        worksheet.write(6,14, "Costo. Unitario",boldbord)
        worksheet.write(6,15, "Costo Total",boldbord)
        worksheet.merge_range(5,16,5,18, "Saldo",boldbord)
        worksheet.write(6,16, "Cantidad",boldbord)
        worksheet.write(6,17, "Costo. Unitario",boldbord)
        worksheet.write(6,18, "Costo Total",boldbord)


        sql = """
        select
        slo.complete_name as "Ubicación Origen",
        sld.complete_name as "Ubicación Destino",
        sw.name as "Almacén",
        case
            when si.is_initial_sil = True then 'SALDO INICIAL'
            else
                case
                    when sm.inventory_id is not NULL then 'AJUSTE POR DIFERENCIA DE INVENTARIO'
                    else tok.name
                end
        end as "Tipo de Operación",
        pc.name as "Categoría",
        pt.name as "Producto",
        pp.default_code as "Código de Producto",
        uom.name as "Unidad",
        case
            when sp.invoice_id is not NULL then aml.invoice_date
            else
                case
                    when sp.use_kardex_date then sp.kardex_date
                    else 
                        case
                            when sm.inventory_id is NULL then sm.date
                            else
                                case
                                    when si.accounting_date is NULL then si.date
                                    else si.accounting_date
                                end
                        end
                end
        end as "Fecha",
        case
            when sp.invoice_id is not NULL then aml.invoice_name
            else
                case
                    when sp.name != '' then sp.name
                    else si.name
                end
        end as "Doc. Almacén",
        case 
            when spt.code = 'incoming' or coalesce(spt.code , '') = '' then sm.product_qty
            else 0
        end as "Entrada",
        case 
            when spt.code = 'incoming' or coalesce(spt.code , '') = '' then 0
            else sm.product_qty
        end as "Salida",
        svl.unit_cost + sm.kardex_price_unit as "Precio Unitario",
        sp.picking_type_id as "Tipo de Picking",
        sm.inventory_id as "Ajuste",
        si.is_initial_sil
        from stock_move sm
        left join stock_move_line sml ON sm.id = sml.move_id
        left join stock_location slo ON sml.location_id = slo.id
        left join stock_location sld ON sml.location_dest_id = sld.id
        left join stock_warehouse sw ON sm.warehouse_id = sw.id
        left join stock_picking sp ON sp.id = sm.picking_id
        left join stock_picking_type spt ON sp.picking_type_id = spt.id
        left join type_operation_kardex tok ON tok.id = sp.type_operation_sunat_id
        left join product_product pp ON sm.product_id = pp.id
        left join product_template pt ON pp.product_tmpl_id = pt.id
        left join product_category pc ON pc.id = pt.categ_id
        left join uom_uom as uom ON uom.id = pt.uom_id
        left join stock_valuation_layer svl ON svl.stock_move_id = sm.id
        left join (select *, si.id as idsi, sil.is_initial as is_initial_sil from stock_inventory si
        left join stock_inventory_line sil ON sil.inventory_id = si.id where product_id in """ +str(tuple(s_prod))+ """ and si.state = 'done') si ON sm.inventory_id = si.idsi
        left join (select *, am.id as idam, am.ref as invoice_name from account_move am 
        left join account_move_line aml ON aml.move_id = am.id
        where aml.exclude_from_invoice_tab = false and aml.product_id in """ +str(tuple(s_prod))+ """) as aml ON sp.invoice_id = aml.idam
        where sm.product_id in """ +str(tuple(s_prod))+ """
        and sm.date >='""" + date_ini + """' and sm.date <='""" + date_fin + """'
        and (sml.location_id in """ +str(tuple(s_loca))+ """ or sml.location_dest_id in """ +str(tuple(s_loca))+ """)
        and svl.stock_landed_cost_id is NULL
        and sm.state = 'done'
        order by "Fecha"
        """
        self.env.cr.execute(sql)
        print(sql)
        ingreso1= 0
        ingreso2= 0
        salida1= 0
        salida2= 0

        saldo = 0
        saldo_total = 0
        last_price = 0
        almacen = None
        producto = None
        for line in self.env.cr.fetchall():

            saldo = saldo + line[10] - line[11]

            worksheet.write(x,0,line[0] if line[0] else '' ,bord )
            worksheet.write(x,1,line[1] if line[1] else '' ,bord )
            worksheet.write(x,2,line[2] if line[2] else '' ,bord )
            worksheet.write(x,3,line[3] if line[3] else '' ,bord )
            worksheet.write(x,4,line[4] if line[4] else '' ,bord )
            worksheet.write(x,5,line[5] if line[5] else '' ,bord )
            worksheet.write(x,6,line[6] if line[6] else '' ,bord )
            worksheet.write(x,7,line[7] if line[7] else '' ,bord )
            # user_tz = pytz.timezone(self.env.context.get('tz'))
            # date_to_xls = pytz.utc.localize(line[8]).astimezone(user_tz)
            # worksheet.write(x,8,date_to_xls.strftime("%d/%m/%Y") if date_to_xls else '' ,bord )
            worksheet.write(x,8,line[8].strftime("%d/%m/%Y") ,bord )
            worksheet.write(x,9,line[9] if line[9] else '' ,bord )
            if line[14]==None:
                worksheet.write(x,10,line[10] if line[10] else 0 ,numberdos )
                worksheet.write(x,11,line[12] if line[12] and line[10]>0 else 0 ,numberocho )
                worksheet.write(x,12,round(line[12] * line[10],2) if line[10] and line[12] else 0 ,numberdos )
            else:
                worksheet.write(x,10, 0 ,numberdos )
                worksheet.write(x,11, 0 ,numberocho )
                worksheet.write(x,12, 0 ,numberdos )
            worksheet.write(x,13,line[11] if line[11] else 0 ,numberdos )
            worksheet.write(x,14,(last_price if last_price > 0 else line[12]) if (last_price if last_price > 0 else line[12]) and line[11]>0 else 0 ,numberocho )
            worksheet.write(x,15,round((last_price if last_price > 0 else line[12]) * line[11],2) if line[11] and (last_price if last_price > 0 else line[12]) else 0 ,numberdos )
            worksheet.write(x,16,saldo ,numberdos )
            ing = round((line[12] if line[12] and line[12]>0 else last_price) * line[10],2) if line[10] else 0
            sal = round(last_price * line[11],2) if line[11] else 0
            if line[13] == 1 or line[13] == None: #Stock pickin type == 1 == Ingreso
                saldo_total = saldo_total + ing - sal
                if line[14] and line[15] == False or line[14] and line[15] == True and x > 7:
                    last_price = last_price
                else:
                    last_price = saldo_total / saldo if saldo_total else 0
            else:
                saldo_total = saldo_total + ing - sal
            worksheet.write(x,17, last_price ,numberocho )
            worksheet.write(x,18,saldo_total if saldo_total else 0,numberdos )
            x = x +1

        tam_col = [11,11,5,5,7,5,11,11,11,11,11,11,11,11,11,11,11,11,11,11,11,11,11]


        worksheet.set_column('A:A', tam_col[0])
        worksheet.set_column('B:B', tam_col[1])
        worksheet.set_column('C:C', tam_col[2])
        worksheet.set_column('D:D', tam_col[3])
        worksheet.set_column('E:E', tam_col[4])
        worksheet.set_column('F:F', tam_col[5])
        worksheet.set_column('G:G', tam_col[6])
        worksheet.set_column('H:H', tam_col[7])
        worksheet.set_column('I:I', tam_col[8])
        worksheet.set_column('J:J', tam_col[9])
        worksheet.set_column('K:K', tam_col[10])
        worksheet.set_column('L:L', tam_col[11])
        worksheet.set_column('M:M', tam_col[12])
        worksheet.set_column('N:N', tam_col[13])
        worksheet.set_column('O:O', tam_col[14])
        worksheet.set_column('P:P', tam_col[15])
        worksheet.set_column('Q:Q', tam_col[16])
        worksheet.set_column('R:R', tam_col[17])
        worksheet.set_column('S:S', tam_col[18])
        worksheet.set_column('T:Z', tam_col[19])

        workbook.close()


        # f = open(direccion + 'kardex_producto.xlsx', 'rb')
        f = open(path + 'kardex_producto' + self.env.user.name + '.xlsx', 'rb')

        return self.env['popup.it'].get_file('Kardex_Fisico.xlsx',base64.encodestring(b''.join(f.readlines())))



    def do_csvtoexcel_13_1(self):
        cad = ""

        s_prod = [-1,-1,-1]
        s_loca = [-1,-1,-1]
        if self.format_13_1:
            lst_locations = [self.location.id]
        else:
            if self.alllocations == True:
                locat_ids = self.env['stock.location'].search( [('usage','in',('internal','inventory','transit','procurement','production'))] )
                lst_locations = locat_ids.ids
            else:
                lst_locations = self.location_ids.ids
        lst_products  = [self.env.context['active_id']]
        productos='{'
        almacenes='{'
        date_ini=self.fini.strftime("%Y-%m-%d")
        date_fin=self.ffin.strftime("%Y-%m-%d 23:59:59")
        

        if len(lst_products) == 0:
            raise osv.except_osv('Alerta','No existen productos seleccionados')

        for producto in lst_products:
            productos=productos+str(producto)+','
            s_prod.append(producto)
        productos=productos[:-1]+'}'
        for location in lst_locations:
            almacenes=almacenes+str(location)+','
            s_loca.append(location)
        almacenes=almacenes[:-1]+'}'



        import io
        from xlsxwriter.workbook import Workbook
        output = io.BytesIO()

        my_path = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(my_path, '../static/')

        #direccion = self.env['main.parameter'].search([])[0].dir_create_file
        # workbook = Workbook(direccion +'kardex_producto.xlsx')
        workbook = Workbook(path +'kardex_producto.xlsx')
        worksheet = workbook.add_worksheet("Kardex")
        bold = workbook.add_format({'bold': True})
        bold.set_font_size(8)
        normal = workbook.add_format()
        boldbord = workbook.add_format({'bold': True})
        boldbord.set_border(style=2)
        boldbord.set_align('center')
        boldbord.set_align('vcenter')
        boldbord.set_text_wrap()
        boldbord.set_font_size(8)
        boldbord.set_bg_color('#DCE6F1')

        especial1 = workbook.add_format({'bold': True})
        especial1.set_align('left')
        especial1.set_align('vcenter')
        especial1.set_text_wrap()
        especial1.set_font_size(15)

        numbertres = workbook.add_format({'num_format':'0.000'})
        numberdos = workbook.add_format({'num_format':'0.00'})
        numberseis = workbook.add_format({'num_format':'0.000000'})
        numberseis.set_font_size(8)
        numberocho = workbook.add_format({'num_format':'0.00000000'})
        numberocho.set_font_size(8)
        bord = workbook.add_format()
        bord.set_border(style=1)
        bord.set_font_size(8)
        numberdos.set_border(style=1)
        numberdos.set_font_size(8)
        numbertres.set_border(style=1)
        numberseis.set_border(style=1)
        numberocho.set_border(style=1)
        numberdosbold = workbook.add_format({'num_format':'0.00','bold':True})
        numberdosbold.set_font_size(8)
        x= 16
        tam_col = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        tam_letra = 1.2

        product = self.env['product.product'].browse(self.env.context['active_id'])

        # worksheet.merge_range(1,5,1,10, "KARDEX FISICO - " + product.name, especial1)
        worksheet.merge_range(0,0,0,20,'FORMATO 13.1: "REGISTRO DE INVENTARIO PERMANENTE VALORIZADO - DETALLE DEL INVENTARIO VALORIZADO"',especial1)
        if str(self.fini)[5:7] == str(self.ffin)[5:7]:
            period = str(self.fini)[5:7] + '-' + str(self.fini)[:4]
        else:
            period = str(self.fini)[5:7] + '-' + str(self.fini)[:4] + ' al ' + str(self.ffin)[:4] + '-' + str(self.ffin)[5:7]

        worksheet.write(2,0,'PERIODO: ' + period,bold)
        worksheet.write(3,0,'RUC: ' + self.env.user.company_id.partner_id.vat if self.env.user.company_id.partner_id.vat else 'Vat number not configured in company.',bold)
        worksheet.write(4,0,'APELLIDOS Y NOMBRES, DENOMINACIÓN O RAZÓN SOCIAL: ' + self.env.user.company_id.partner_id.name,bold)
        worksheet.write(5,0,'ESTABLECIMIENTO (1): ' + self.location.name,bold)
        worksheet.write(6,0,'CÓDIGO DE LA EXISTENCIA: ' + product.default_code if product.default_code else 'CÓDIGO DE LA EXISTENCIA: Sin código de producto',bold)
        worksheet.write(7,0,'TIPO (TABLA 5): ' + product.categ_id.existence_type_id.name if product.categ_id.existence_type_id else 'No tiene tipo de existencia en la categoría',bold)
        worksheet.write(8,0,'DESCRIPCIÓN: ' + product.name,bold)
        worksheet.write(9,0,'CÓDIGO DE LA UNIDAD DE MEDIDA (TABLA 6): ' + product.uom_kardex_id.name if product.uom_kardex_id else 'CÓDIGO DE LA UNIDAD DE MEDIDA (TABLA 6): ' + product.uom_id.name, bold) #'El producto no tiene unidad de medida de kardex',bold)
        worksheet.write(10,0,'MÉTODO DE VALUACIÓN: ' + dict(product.categ_id._fields['property_cost_method']._description_selection(self.env)).get(product.categ_id.property_cost_method),bold)
        
        # worksheet.write(2,1,str(self.fini))
        # worksheet.write(3,1,str(self.ffin))
        import datetime

        worksheet.merge_range(13,0,14,3, u"DOCUMENTO DE TRASLADO, COMPROBANTE DE PAGO, DOCUMENTO INTERNO O SIMILAR",boldbord)
        worksheet.write(15,0, u"FECHA",boldbord)
        worksheet.write(15,1, u"TIPO (TABLA 10)",boldbord)
        worksheet.write(15,2, u"SERIE",boldbord)
        worksheet.write(15,3, u"NUMERO",boldbord)
        worksheet.merge_range(13,4,15,4, u"TIPO DE OPERACIÓN (TABLA 12)",boldbord)
        # worksheet.merge_range(13,3,14,3, u"Tipo de Operación",boldbord)
        # worksheet.merge_range(13,4,14,4, u"Categoria",boldbord)

        # worksheet.merge_range(13,5,14,5, u"Producto",boldbord)
        # worksheet.merge_range(13,6,14,6, u"Codigo P.",boldbord)
        # worksheet.merge_range(13,7,14,7, u"Unidad",boldbord)

        # worksheet.merge_range(13,8,14,8, u"Fecha",boldbord)

        # worksheet.merge_range(13,9,14,9, u"Doc. Almacen",boldbord)

        worksheet.merge_range(13,5,13,7, "ENTRADAS",boldbord)
        worksheet.merge_range(14,5,15,5, "CANTIDAD",boldbord)
        worksheet.merge_range(14,6,15,6, "COSTO UNITARIO",boldbord)
        worksheet.merge_range(14,7,15,7, "COSTO TOTAL",boldbord)
        worksheet.merge_range(13,8,13,10, "SALIDAS",boldbord)
        worksheet.merge_range(14,8,15,8, "CANTIDAD",boldbord)
        worksheet.merge_range(14,9,15,9, "COSTO UNITARIO",boldbord)
        worksheet.merge_range(14,10,15,10, "COSTO TOTAL",boldbord)
        worksheet.merge_range(13,11,13,13, "SALDO FINAL",boldbord)
        worksheet.merge_range(14,11,15,11, "CANTIDAD",boldbord)
        worksheet.merge_range(14,12,15,12, "COSTO UNITARIO",boldbord)
        worksheet.merge_range(14,13,15,13, "COSTO TOTAL",boldbord)



        self.env.cr.execute("""
        select
        slo.complete_name as "Ubicación Origen",
        sld.complete_name as "Ubicación Destino",
        sw.name as "Almacén",
        case
            when si.is_initial_sil = True then 'SALDO INICIAL'
            else
                case
                    when sm.inventory_id is not NULL then 'AJUSTE POR DIFERENCIA DE INVENTARIO'
                    else tok.name
                end
        end as "Tipo de Operación",
        pc.name as "Categoría",
        pt.name as "Producto",
        pp.default_code as "Código de Producto",
        uom.name as "Unidad",
        case
            when sp.invoice_id is not NULL then aml.invoice_date
            else
                case
                    when sp.use_kardex_date then sp.kardex_date
                    else 
                        case
                            when sm.inventory_id is NULL then sm.date
                            else
                                case
                                    when si.accounting_date is NULL then si.date
                                    else si.accounting_date
                                end
                        end
                end
        end as "Fecha",
        case
            when sp.invoice_id is not NULL then aml.invoice_name
            else
                case
                    when sp.name != '' then sp.name
                    else si.name
                end
        end as "Doc. Almacén",
        case 
            when spt.code = 'incoming' or coalesce(spt.code , '') = '' then sm.product_qty
            else 0
        end as "Entrada",
        case 
            when spt.code = 'incoming' or coalesce(spt.code , '') = '' then 0
            else sm.product_qty
        end as "Salida",
        svl.unit_cost + sm.kardex_price_unit as "Precio Unitario",
        sp.picking_type_id as "Tipo de Picking",
        sm.inventory_id as "Ajuste",
        si.is_initial_sil
        from stock_move sm
        left join stock_move_line sml ON sm.id = sml.move_id
        left join stock_location slo ON sml.location_id = slo.id
        left join stock_location sld ON sml.location_dest_id = sld.id
        left join stock_warehouse sw ON sm.warehouse_id = sw.id
        left join stock_picking sp ON sp.id = sm.picking_id
        left join stock_picking_type spt ON sp.picking_type_id = spt.id
        left join type_operation_kardex tok ON tok.id = sp.type_operation_sunat_id
        left join product_product pp ON sm.product_id = pp.id
        left join product_template pt ON pp.product_tmpl_id = pt.id
        left join product_category pc ON pc.id = pt.categ_id
        left join uom_uom as uom ON uom.id = pt.uom_id
        left join stock_valuation_layer svl ON svl.stock_move_id = sm.id
        left join (select *, si.id as idsi, sil.is_initial as is_initial_sil from stock_inventory si
        left join stock_inventory_line sil ON sil.inventory_id = si.id where product_id in """ +str(tuple(s_prod))+ """ and si.state = 'done') si ON sm.inventory_id = si.idsi
        left join (select *, am.id as idam, am.ref as invoice_name from account_move am 
        left join account_move_line aml ON aml.move_id = am.id
        where aml.exclude_from_invoice_tab = false and aml.product_id in """ +str(tuple(s_prod))+ """) as aml ON sp.invoice_id = aml.idam
        where sm.product_id in """ +str(tuple(s_prod))+ """
        and sm.date >='""" + date_ini + """' and sm.date <='""" + date_fin + """'
        and (sml.location_id in """ +str(tuple(s_loca))+ """ or sml.location_dest_id in """ +str(tuple(s_loca))+ """)
        and svl.stock_landed_cost_id is NULL
        and sm.state = 'done'
        order by "Fecha"
        """)

        ingreso1= 0
        ingreso2= 0
        salida1= 0
        salida2= 0

        saldo = 0
        saldo_total = 0
        last_price = 0
        almacen = None
        producto = None
        for line in self.env.cr.fetchall():
            if line[3]:	
                saldo = saldo + line[10] - line[11]
                worksheet.write(x,0,line[8].strftime("%d/%m/%Y") if line[7] else '' ,bord )
                worksheet.write(x,1,line[8] if line[8] else '' ,bord )
                if line[9]:
                    num_doc = line[9].split('-')
                    if len(num_doc)>1:
                        serie = num_doc[0]
                        numero = num_doc[1]
                    else:
                        serie=''
                        numero = line[9]
                worksheet.write(x,2,serie if serie else '' ,bord )
                worksheet.write(x,3,numero if numero else '' ,bord )
                worksheet.write(x,4,line[3] ,bord )
                if line[15]==None:
                    worksheet.write(x,5,line[10] if line[10] else 0 ,numberdos )
                    worksheet.write(x,6,line[12] if line[12] and line[10]>0 else 0 ,numberocho )
                    worksheet.write(x,7,round(line[12] * line[10],2) if line[10] and line[12] else 0 ,numberdos )
                else:
                    worksheet.write(x,5, 0 ,numberdos )
                    worksheet.write(x,6, 0 ,numberocho )
                    worksheet.write(x,7, 0 ,numberdos )
                worksheet.write(x,8,line[11] if line[11] else 0 ,numberdos )
                worksheet.write(x,9,(last_price if last_price > 0 else line[12]) if (last_price if last_price > 0 else line[12]) and line[11]>0 else 0 ,numberocho )
                worksheet.write(x,10,round((last_price if last_price > 0 else line[12]) * line[11],2) if line[11] and (last_price if last_price > 0 else line[12]) else 0 ,numberdos )
                worksheet.write(x,11,saldo ,numberdos )
                ing = round((line[12] if line[12] and line[12]>0 else last_price) * line[10],2) if line[10] else 0
                sal = round(last_price * line[11],2) if line[11] else 0
                if line[13] == 1 or line[13] == None: #Stock pickin type == 1 == Ingreso
                    saldo_total = saldo_total + ing - sal
                    if line[14] and line[15] == False or line[14] and line[15] == True and x > 16:
                        last_price = last_price
                    else:
                        last_price = saldo_total / saldo if saldo_total else 0
                else:
                    saldo_total = saldo_total + ing - sal
                worksheet.write(x,12, last_price ,numberocho )
                worksheet.write(x,13,saldo_total if saldo_total else 0,numberdos )
                x = x +1

        tam_col = [11,8,5,7,12,11,11,11,11,11,11,11,11,11,11,11,11,11,11,11,11,11,11]


        worksheet.set_column('A:A', tam_col[0])
        worksheet.set_column('B:B', tam_col[1])
        worksheet.set_column('C:C', tam_col[2])
        worksheet.set_column('D:D', tam_col[3])
        worksheet.set_column('E:E', tam_col[4])
        worksheet.set_column('F:F', tam_col[5])
        worksheet.set_column('G:G', tam_col[6])
        worksheet.set_column('H:H', tam_col[7])
        worksheet.set_column('I:I', tam_col[8])
        worksheet.set_column('J:J', tam_col[9])
        worksheet.set_column('K:K', tam_col[10])
        worksheet.set_column('L:L', tam_col[11])
        worksheet.set_column('M:M', tam_col[12])
        worksheet.set_column('N:N', tam_col[13])
        worksheet.set_column('O:O', tam_col[14])
        worksheet.set_column('P:P', tam_col[15])
        worksheet.set_column('Q:Q', tam_col[16])
        worksheet.set_column('R:R', tam_col[17])
        worksheet.set_column('S:S', tam_col[18])
        worksheet.set_column('T:Z', tam_col[19])

        workbook.close()


        # f = open(direccion + 'kardex_producto.xlsx', 'rb')
        f = open(path + 'kardex_producto.xlsx', 'rb')

        return self.env['popup.it'].get_file('Kardex_Fisico.xlsx',base64.encodestring(b''.join(f.readlines())))



    def do_csv(self):
        data = self.read()
        cad=""
        
        lst_products  = [self.env.context['active_id']]

        s_prod = [-1,-1,-1]
        s_loca = [-1,-1,-1]

        lst_locations = data[0]['location_ids']
        productos='{0,'
        almacenes='{0,'
        date_ini=data[0]['fini']
        date_fin=data[0]['ffin']
        
        if 'alllocations' in data[0]:
            lst_locations = self.env['stock.location'].search([]).ids

        for producto in lst_products:
            productos=productos+str(producto)+','
            s_prod.append(producto)
        productos=productos[:-1]+'}'
        for location in lst_locations:
            almacenes=almacenes+str(location)+','
            s_loca.append(location)
        almacenes=almacenes[:-1]+'}'
        direccion = self.env['main.parameter'].search([])[0].dir_create_file


        cadf=u"""



        copy (select
origen.complete_name AS "Ubicación Origen",
destino.complete_name AS "Ubicación Destino",
almacen.complete_name AS "Almacén",
vstf.motivo_guia AS "Tipo de operación",
pc.name as "Categoria",
coalesce(it.value,pt.name) as "Producto",
pt.default_code as "Codigo P.",
pu.name as "unidad",
vstf.fecha as "Fecha",
sp.name as "Doc. Almacén",
vstf.entrada as "Entrada",
vstf.salida as "Salida",
''::varchar as pedido_compra
from
(
select vst_kardex_fisico.date::date as fecha,vst_kardex_fisico.location_id as origen,
vst_kardex_fisico.location_dest_id as destino, vst_kardex_fisico.location_dest_id as almacen,
vst_kardex_fisico.product_qty as entrada, 0 as salida,vst_kardex_fisico.id  as stock_move,
vst_kardex_fisico.guia as motivo_guia,vst_kardex_fisico.product_id,
vst_kardex_fisico.estado from vst_kardex_fisico
join stock_move sm on sm.id = vst_kardex_fisico.id
join stock_picking sp on sm.picking_id = sp.id
join stock_location l_o on l_o.id = vst_kardex_fisico.location_id
join stock_location l_d on l_d.id = vst_kardex_fisico.location_dest_id
where ( (l_o.usage = 'internal' and l_o.usage = 'internal'  )  or ( l_o.usage != 'internal' or l_o.usage != 'internal' ) )

union all
select date::date as fecha, location_id as origen, location_dest_id as destino, location_id as almacen, 0 as entrada, product_qty as salida,id  as stock_move ,guia as motivo_guia ,product_id , estado from vst_kardex_fisico
) as vstf
inner join stock_location origen on origen.id = vstf.origen
inner join stock_location destino on destino.id = vstf.destino
inner join stock_location almacen on almacen.id = vstf.almacen
inner join product_product pp on pp.id = vstf.product_id
inner join product_template pt on pt.id = pp.product_tmpl_id
inner join product_category pc on pc.id = pt.categ_id
inner join uom_uom pu on pu.id = pt.uom_id
inner join stock_move sm on sm.id = vstf.stock_move
inner join stock_picking sp on sp.id = sm.picking_id
left join ir_translation it ON pt.id = it.res_id and it.name = 'product.template,name' and it.lang = 'es_PE' and it.state = 'translated'
where vstf.fecha >='""" +str(date_ini)+ u"""' and vstf.fecha <='""" +str(date_fin)+ u"""'
and vstf.product_id in """ +str(tuple(s_prod))+ u"""
and vstf.almacen in """ +str(tuple(s_loca))+ u"""
and vstf.estado = 'done'
and almacen.usage = 'internal'
order by
almacen.id,pp.id,vstf.fecha,vstf.entrada desc


) to '"""+direccion+u"""/kardex.csv'  WITH DELIMITER ',' CSV HEADER
        """
        
        self.env.cr.execute(cadf)
        import gzip
        import shutil

        f = open(direccion+'/kardex.csv', 'rb')

        return self.env['popup.it'].get_file('Kardex_Fisico.csv',base64.encodestring(b''.join(f.readlines())))