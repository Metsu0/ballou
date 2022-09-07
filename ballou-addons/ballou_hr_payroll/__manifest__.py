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
    'name': "BALLOU HR PAYROLL",

    'version': '14.0.1.0.0',
    'category': '',
    'sequence': -15,
    'summary': '',
    'author': 'eTech Consulting',
    'website': 'http://www.etechconsulting-mg.com',
    'depends': ['base', 'hr_payroll', 'ballou_base', 'ballou_hr', 'ballou_contract_category', 'ballou_hr_holidays'],
    'data': [
        # security
        'security/ir.model.access.csv',
        # data
        'data/hr_work_entry_type.xml',
        # views
        'views/hr_contract.xml',
        'views/hr_payslip_config_views.xml',
        'views/payslip_resume_views.xml',
        'views/res_bank_views.xml',
        'views/hr_salary_rule_views.xml',
        'views/hr_payroll_views.xml',
        'views/hr_work_entry_type.xml',
        'views/hr_leave_type_views.xml',
        'views/hr_payroll_report_views.xml',

        # report
        'report/report_payslip_templates.xml',
        'report/report_payslip_ballou_templates.xml',
        'report/report_payslip_ballou.xml',
    ],
    'qweb': [],
    'demo': [],
    'installable': True,
    'application': False,
}
