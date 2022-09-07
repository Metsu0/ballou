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
    'name': 'SIRH - HR',
    'version': '13.0.1.0.0',
    'category': '',
    'sequence': -15,
    'summary': '',
    'author': 'eTech Consulting',
    'website': 'http://www.etechconsulting-mg.com',
    'depends': ['website','sirh_base_security', 'hr_contract', 'ooto_hr_account'],
    'data': [
        # security
        'security/ir.model.access.csv',
        'security/ir_model_access.xml',
        'security/ir_rule_for_employee.xml',
        # 'security/ir_rule_for_leave.xml',
        'security/ir_rule_native_updated.xml',
        # 'security/menu_restriction.xml',
        'security/profile_menu_restriction.xml',
        'security/base_salary_security.xml',

        # data
        'data/security_data.xml',
        'data/hr_level_data.xml',
        'data/direction_data.xml',
        'data/notification_to_all_template.xml',
        'data/hr_payment_mode_data.xml',
        'data/hr_contract_category_data.xml',

        # views
        'views/hr_employee_view_inherit.xml',
        'views/hr_department_view_inherit.xml',
        'wizard/regenerate_direction_on_employee.xml',
        'views/hr_level_view.xml',
        'views/skill_matrix_menu.xml',
        'views/direction_view.xml',
        'views/hr_job_view.xml',
        'views/hr_spinneret_view.xml',
        'views/send_notification_to_all.xml',
        'views/hr_contract_category_views.xml',
        'views/hr_paysilp_payment_mode_views.xml',
        'views/hr_contract_views.xml',
        'views/hr_employee_badge_view.xml',
        'views/hr_contract_template.xml',

        # report
        'report/hr_contract_report.xml',
        'report/report_contract_template.xml',
        'report/report_certificate_work.xml'
    ],
    'qweb': [],
    'demo': [],
    'installable': True,
    'application': False,
}
