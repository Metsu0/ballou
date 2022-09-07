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
    'name': "BALLOU HR",
    'version': '14.0.1.0.0',
    'category': 'Human Resources/Employees',
    'sequence': 10,
    'summary': 'Customization of HR module',
    'author': 'eTech Consulting',
    'website': 'http://www.etechconsulting-mg.com',
    'depends': ['hr', 'hr_contract'],
    'data': [
        # sercurity
        'security/ir.model.access.csv',

        # data
        'data/hr_payment_mode_data.xml',

        # view
        'views/hr_employee_views.xml',
        'views/hr_contract_views.xml',
        'views/hr_internale_classification_views.xml',
        'views/hr_dependent_views.xml',
        'views/hr_paysilp_payment_mode_views.xml',
    ],
    'qweb': [],
    'demo': [],
    'installable': True,
    'application': False,
}
