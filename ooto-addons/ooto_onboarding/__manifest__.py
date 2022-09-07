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
    'name': 'OOTO - Onboarding',
    'version': '13.0.1.0.0',
    'category': 'HR',
    'sequence': -12,
    'summary': 'OOTO - Onboarding',
    'description': 'OOTO - Onboarding',
    'author': 'eTech Consulting',
    'website': 'http://www.etechconsulting-mg.com',
    'depends': ['base', 
                'hr', 
                'survey', 
                'calendar', 
                'hr_contract', 
                'kanban_draggable', 
                'mail', 
                'sign', 
                'mass_mailing',
                'ooto_base', 
                'ooto_default_image', 
                'ooto_base_security', 
                'ooto_hr_account', 
                'sirh_hr'
                ],
    'data': [
        "security/ooto_onboarding_security.xml",
        "security/ir.model.access.csv",
        "data/ooto_boarding_data.xml",
        "data/survey_data.xml",
        "views/onboarding_task_views.xml",
        "views/onboarding_appointment_views.xml",
        "views/onboarding_views.xml",
        "views/onboarding_role_views.xml",
        "views/survey_views.xml",
        "views/sign_templates.xml",
        "views/mail_marketing_template.xml",
        "views/hr_employee.xml",
        "views/mail_compose_message.xml",
        "views/assets.xml",
        "data/onboarding_tutorial.xml",
        "views/onboarding_tutorial_views.xml",
        "views/onboarding_employee_section_fields_views.xml",
        "views/onboarding_ir_model_fields_views.xml",
        "data/onboarding_notification_data.xml",
        "data/onboarding_notification_email_data.xml",
        "views/onboarding_notification_views.xml",
        "wizard/employee_option_wizard_views.xml",
        "data/mail_template_task_email.xml",
        "data/email_template.xml",
        "data/auth_signup_connection.xml",
        "data/ir_cron_reminder_mail.xml",
    ],
    'qweb': ['static/src/xml/*.xml'],
    'update_xml': ['query.sql'],
    'demo': [],
    'installable': True,
    'application': False,
}
