# -*- coding: utf-8 -*-
{
    'name': "generic_hr",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['ballou_hr', 'ballou_hr_payroll', 'hr_payroll', 'hr_holidays', 'hr_skills'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'views/hr_payroll_views.xml',
        'views/hr_leave_type_views.xml',
        'views/payslip_resume_views.xml',
        'views/hr_salary_rule_views.xml',
        'views/hr_contract.xml',
        'views/hr_sanction_view.xml',
        # report
        'report/report_payslip_generic_templates.xml',
        'report/report_payslip_generic_templates.xml',
        'report/hr_employee_history.xml',
        # wizard
        'wizard/payslip_state_export.xml',
        'wizard/payslip_state_export_template.xml',
    ],
    'assets': {
        'web.assets_common': [
            # '/generic_hr/static/src/scss/style.scss',

        ]
    },
    # only loaded in demonstration mode

}
