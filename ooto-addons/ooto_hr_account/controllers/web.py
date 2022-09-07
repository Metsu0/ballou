# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.addons.portal.controllers.web import Home as HomePortal
from odoo.addons.web.controllers.main import Home
from odoo.http import request


class HomePortal(HomePortal):

    def _login_redirect(self, uid, redirect=None):
        if not redirect and not request.env['res.users'].sudo().browse(uid).has_group('base.group_user'):
            return '/'
        return Home()._login_redirect(uid, redirect=redirect)