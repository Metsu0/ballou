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
    'name': 'SIRH - Base',
    'version': '13.0.1.0.0',
    'category': '',
    'sequence': -15,
    'summary': '',
    'author': 'eTech Consulting',
    'website': 'http://www.etechconsulting-mg.com',
    'depends': ['base', 'ooto_base', 'mail', 'hr', 'web_disable_export_group'],
    # 'depends': ['base', 'ooto_base', 'mail','atharva_theme_general', 'hr', 'web_disable_export_group'],
    'data': [
        # security
        'security/ir.model.access.csv',

        # data

        # views
        'views/assets_domain_selector.xml',
        'views/res_partner.xml',
        'views/portal_login_template.xml',
        'views/res_bank_views.xml',
        'views/mail_data.xml',
        'views/res_company.xml',
        'views/view_employee_form.xml',

        # Translation
        # 'data/ir_translation.yml',
    ],
    'qweb': [],
    'demo': [],
    'installable': True,
    'application': False,
}
