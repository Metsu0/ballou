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

from odoo import http
from odoo.addons.website.controllers.main import Website
from werkzeug import urls


class Website(Website):
    """
    Class héritant de Website
    """

    @http.route('/', type='http', auth="public", website=True)
    def index(self, *args, **kw):
        """
        Permet de rendre la page d'accueil non public, redirection vers la page de login tant que l'utilisateur
        ne s'est pas connecté
        :param args:
        :param kw:
        :return:
        """
        homepage = http.request.website.homepage_id
        url = http.request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if homepage and homepage.url == '/' and http.request.env.user.login == 'public':
            return http.request.redirect(urls.url_join(url, '/web/session/logout'))
        return super(Website, self).index(*args, **kw)
