# -*- coding: utf-8 -*-
# from odoo import http


# class BallouSales(http.Controller):
#     @http.route('/ballou_sales/ballou_sales/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ballou_sales/ballou_sales/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ballou_sales.listing', {
#             'root': '/ballou_sales/ballou_sales',
#             'objects': http.request.env['ballou_sales.ballou_sales'].search([]),
#         })

#     @http.route('/ballou_sales/ballou_sales/objects/<model("ballou_sales.ballou_sales"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ballou_sales.object', {
#             'object': obj
#         })
