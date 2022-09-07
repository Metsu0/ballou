# -*- coding: utf-8 -*-
# from odoo import http


# class BallouStock(http.Controller):
#     @http.route('/ballou_stock/ballou_stock/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ballou_stock/ballou_stock/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ballou_stock.listing', {
#             'root': '/ballou_stock/ballou_stock',
#             'objects': http.request.env['ballou_stock.ballou_stock'].search([]),
#         })

#     @http.route('/ballou_stock/ballou_stock/objects/<model("ballou_stock.ballou_stock"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ballou_stock.object', {
#             'object': obj
#         })
