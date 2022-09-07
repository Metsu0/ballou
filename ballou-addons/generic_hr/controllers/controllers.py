# -*- coding: utf-8 -*-
# from odoo import http


# class GenericHr(http.Controller):
#     @http.route('/generic_hr/generic_hr/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/generic_hr/generic_hr/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('generic_hr.listing', {
#             'root': '/generic_hr/generic_hr',
#             'objects': http.request.env['generic_hr.generic_hr'].search([]),
#         })

#     @http.route('/generic_hr/generic_hr/objects/<model("generic_hr.generic_hr"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('generic_hr.object', {
#             'object': obj
#         })
