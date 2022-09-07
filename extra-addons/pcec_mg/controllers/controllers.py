# -*- coding: utf-8 -*-
# from odoo import http


# class PcecMg(http.Controller):
#     @http.route('/pcec_mg/pcec_mg/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pcec_mg/pcec_mg/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pcec_mg.listing', {
#             'root': '/pcec_mg/pcec_mg',
#             'objects': http.request.env['pcec_mg.pcec_mg'].search([]),
#         })

#     @http.route('/pcec_mg/pcec_mg/objects/<model("pcec_mg.pcec_mg"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pcec_mg.object', {
#             'object': obj
#         })
