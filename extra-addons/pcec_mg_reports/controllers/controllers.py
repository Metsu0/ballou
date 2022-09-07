# -*- coding: utf-8 -*-
# from odoo import http


# class PcecMgReports(http.Controller):
#     @http.route('/pcec_mg_reports/pcec_mg_reports/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pcec_mg_reports/pcec_mg_reports/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pcec_mg_reports.listing', {
#             'root': '/pcec_mg_reports/pcec_mg_reports',
#             'objects': http.request.env['pcec_mg_reports.pcec_mg_reports'].search([]),
#         })

#     @http.route('/pcec_mg_reports/pcec_mg_reports/objects/<model("pcec_mg_reports.pcec_mg_reports"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pcec_mg_reports.object', {
#             'object': obj
#         })
