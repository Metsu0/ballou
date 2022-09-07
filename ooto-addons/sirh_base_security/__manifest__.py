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
    'name': 'SIRH - Base Security',
    'version': '13.0.1.0.0',
    'category': '',
    'sequence': -15,
    'summary': '',
    'author': 'eTech Consulting',
    'website': 'http://www.etechconsulting-mg.com',
    'depends': ['base', 'hide_menu', 'hr', 'hr_contract', 'ooto_base_security', 'sirh_base', 'dynamic_bypass_rule',
                'access_menu_extra_groups', 'web_export_log', 'stock', 'account'],
    'data': [
        # security
        'data/profiles_data.xml',
        'security/ir.model.access.csv',
        'security/model_access_security.xml',
        'security/employee_group_assignation.xml',
        'security/profile_menu_restriction.xml',
        'security/group_native_updated.xml',

        # data

        # views
    ],
    'qweb': [],
    'demo': [],
    'installable': True,
    'application': False,
}
