# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2019 eTech Consulting (<http://www.etechconsulting-mg.com>). All Rights Reserved
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

{
    'name': 'OOTO Base Security',
    'version': '13.0.1.0.0',
    'category': '',
    'sequence': -12,
    'summary': '',
    'author': 'eTech Consulting',
    'website': 'http://www.etechconsulting-mg.com',
    'depends': ['ooto_base', 'smile_access_control', 'hide_menu'],
    'data': [
        # security
        'security/ir.model.access.csv',
        'security/website_security.xml',

        # data
        'data/security_data.xml',

        # views
        'views/res_users.xml'
    ],
    'qweb': [],
    'demo': [],
    'installable': True,
    'application': False,
}
