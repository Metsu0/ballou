# -*- coding: utf-8 -*-
# from odoo import http


# class BallouPurchase(http.Controller):
#     @http.route('/ballou_purchase/ballou_purchase/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ballou_purchase/ballou_purchase/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ballou_purchase.listing', {
#             'root': '/ballou_purchase/ballou_purchase',
#             'objects': http.request.env['ballou_purchase.ballou_purchase'].search([]),
#         })

#     @http.route('/ballou_purchase/ballou_purchase/objects/<model("ballou_purchase.ballou_purchase"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ballou_purchase.object', {
#             'object': obj
#         })
