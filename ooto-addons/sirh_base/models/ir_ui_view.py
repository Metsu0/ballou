# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2019 eTech (<https://www.etechconsulting-mg.com/>). All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging

from odoo import api, models

from odoo.http import request
from odoo.addons.portal.controllers.portal import _build_url_w_params

_logger = logging.getLogger(__name__)


# class CustomView(models.Model):
#     _inherit = 'ir.ui.view'
#
#     def render(self, values=None, engine='ir.qweb', minimal_qcontext=False):
#         if self._context.get('active_ids'):
#             return super(CustomView, self).render(values, engine=engine, minimal_qcontext=minimal_qcontext)
#         if (not request.session.uid and self.id not in [self.env.ref('web.login').id,
#                                                         self.env.ref('auth_signup.reset_password').id]):
#             request.params.update({'redirect': request.httprequest.path})
#             redirection = _build_url_w_params('/web/login', request.params)
#             response = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
#                             <head>
#                                 <title>Redirecting...</title>
#                             </head>
#                             <body>
#                             <h1>Redirecting...</h1>
#                             <p>You should be redirected automatically to target URL: <a id="redirect_link" href="%s">%s</a>.
#                             If not click the link.</p>
#                             <script type="text/javascript">
#                                document.addEventListener("DOMContentLoaded", function(event) {
#                                 document.getElementById("redirect_link").click();
#                               });
#                             </script>
#                             </body>""" % (redirection, redirection)
#             return response
#         return super(CustomView, self).render(values, engine=engine, minimal_qcontext=minimal_qcontext)
