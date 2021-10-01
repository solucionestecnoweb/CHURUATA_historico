# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
from datetime import datetime, timedelta
import base64
from io import StringIO
from odoo import api, fields, models
from datetime import date
from odoo.tools.float_utils import float_round
from odoo.exceptions import Warning

class ReporteCategoria(models.TransientModel):
    _name = "stock.move.report.categoria"

    date_from = fields.Date(string='Date From', default=lambda *a:datetime.now().strftime('%Y-%m-%d'))
    date_to = fields.Date('Date To', default=lambda *a:(datetime.now() + timedelta(days=(1))).strftime('%Y-%m-%d'))
    category_id = fields.Many2one(comodel_name='product.category', string='Categoria')
    product = fields.Many2many(comodel_name='product.product', string='product')
    date_today = fields.Date(string='Date Today', default=lambda *a:datetime.now().strftime('%Y-%m-%d'))
    company_id = fields.Many2one('res.company','Company',default=lambda self: self.env.user.company_id.id)
    date_report = fields.Date(string='day', default=lambda *a:datetime.now().strftime('%Y-%m-%d'))

    libro  = fields.Many2many(comodel_name='libro.inventario.categoria', string='Libro')
    
    def float_format(self,valor):
        #valor=self.base_tax
        if valor:
            result = '{:,.2f}'.format(valor)
            result = result.replace(',','*')
            result = result.replace('.',',')
            result = result.replace('*','.')
        else:
            result="0,00"
        return result

    def datos(self):
        temp_libro = self.env['libro.inventario.categoria'].search([])
        temp_line = self.env['libro.inventario'].search([])

        categoria =[]

        categoria.append(self.category_id)

        temp = self.env['product.category'].search([
            ('parent_id','=',self.category_id.id)
        ])

        for l in temp:
            categoria.append(l)

        for t in temp_libro:
            t.unlink()

        for t in temp_line:
                t.unlink()

        
        for cat in categoria:
                
            cabezera = self.env['libro.inventario.categoria'].create({
                'name':cat.id,
            })

            self.product =  self.env['product.product'].search([
                ('categ_id','=',cat.id),
                ('type','=','product')
            ])

            for item in self.product:
                item.generate_kardex_gb()
                salida = 0 
                monto_salida = 0
                cantidad_salidas = 0
                
                libro = self.env['libro.inventario'].create({ 
                    'name': item.id,
                    'libro':cabezera.id ,
                    })
                
                libro.libro = cabezera.id
                
                inicial =  self.env['product.product.kardex.line'].search([
                    ('name','=',item.id),
                    ('fecha','<',self.date_from),
                    ])

                if len(inicial) > 0:
                    cantidad_inicial = len(inicial)
                    libro.cantidad_inicial = inicial[cantidad_inicial - 1].total 
                    libro.costo_intradas   = inicial[cantidad_inicial -1 ].promedio
                    libro.total_bolivares_inicial = inicial[cantidad_inicial -1].total_bolivares

                    libro.total = inicial[cantidad_inicial - 1].total 
                    libro.promedio = inicial[cantidad_inicial -1 ].promedio
                    libro.total_bolivares =  inicial[cantidad_inicial -1].total_bolivares

                kardex_line  =  self.env['product.product.kardex.line'].search([
                    ('name','=',item.id),
                    ('fecha','>=',self.date_from),
                    ('fecha','<=',self.date_to),
                    ])
            
                if len(kardex_line) > 0:
                    
                    
                    cantidad = len(kardex_line)

                  
                    libro.total = kardex_line[cantidad -1].total
                    libro.promedio = kardex_line[cantidad-1].promedio
                    libro.total_bolivares = kardex_line[cantidad-1].total_bolivares
                    

                    for sal in kardex_line :
                        libro.cantidad_entradas += sal.cantidad_entradas
                        libro.total_bolivares_entradas += sal.total_bolivares_entradas

                        libro.cantidad_salidas += sal.cantidad_salidas
                        libro.total_bolivares_salida += sal.total_bolivares_salida
                    
                    libro.costo_entradas = libro.total_bolivares_entradas / libro.cantidad_entradas  if libro.total_bolivares_entradas  > 0 else 0
                    libro.costo_salidas  = libro.total_bolivares_salida / libro.cantidad_salidas if libro.total_bolivares_salida > 0 else 0 

                    
        self.libro =  self.env['libro.inventario.categoria'].search([])
        for item in self.libro:
            for l in item.line_id:
                if l.cantidad_inicial == 0 and l.cantidad_entradas == 0 and l.cantidad_salidas == 0:
                    l.unlink()

                
    def print_facturas(self):
        self.datos()
        return self.env.ref('libro_inventario.movimientos_categoria_libro').report_action(self)

class LibroVentasModelo(models.Model):
    _name = "libro.inventario.categoria" 
    name = fields.Many2one(comodel_name='product.category', string='Categoria')
    line_id = fields.One2many(comodel_name='libro.inventario', inverse_name='libro', string='Linea')
    

class LibroVentasModelo(models.Model):
    _name = "libro.inventario" 

    libro = fields.Many2one(comodel_name='libro.inventario.categoria', string='Categoria')
    
    name  = fields.Many2one(comodel_name='product.product', string='Producto')

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
    
    
    
    

    

    
