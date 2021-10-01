# -*- coding: utf-8 -*-
# from odoo import http


# class JpForeignTradeLogistics(http.Controller):
#     @http.route('/jp_foreign_trade_logistics/jp_foreign_trade_logistics/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/jp_foreign_trade_logistics/jp_foreign_trade_logistics/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('jp_foreign_trade_logistics.listing', {
#             'root': '/jp_foreign_trade_logistics/jp_foreign_trade_logistics',
#             'objects': http.request.env['jp_foreign_trade_logistics.jp_foreign_trade_logistics'].search([]),
#         })

#     @http.route('/jp_foreign_trade_logistics/jp_foreign_trade_logistics/objects/<model("jp_foreign_trade_logistics.jp_foreign_trade_logistics"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('jp_foreign_trade_logistics.object', {
#             'object': obj
#         })
