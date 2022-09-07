# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.addons.web.controllers.main import Home
from odoo import http
from odoo.tools import config
from odoo.http import request

class Home(Home):

    @http.route('/check/bon-a-savoir', type='http', auth='none', website=True)
    def load_googd_to_know(self):
        if not request.session.uid:
            try:
                if config['load_db'].find("sirh_") != -1:
                    request.session.db = config['load_db']
            except:
                pass
        return http.local_redirect("/bon-a-savoir")

    @http.route('/check/nous-recrutons', type='http', auth='none', website=True)
    def load_we_hire(self):
        if not request.session.uid:
            try:
                if config['load_db'].find("sirh_") != -1:
                    request.session.db = config['load_db']
            except:
                pass
        return http.local_redirect("/nous-recrutons")

    @http.route('/check/coin-bien-etre', type='http', auth='none', website=True)
    def load_know_how(self):
        if not request.session.uid:
            try:
                if config['load_db'].find("sirh_") != -1:
                    request.session.db = config['load_db']
            except:
                pass
        return http.local_redirect("/coin-bien-etre")


    @http.route('/check/newsletter', type='http', auth='none', website=True)
    def load_newsletter(self):
        if not request.session.uid:
            try:
                if config['load_db'].find("sirh_") != -1:
                    request.session.db = config['load_db']
            except:
                pass
        return http.local_redirect("/newsletter")