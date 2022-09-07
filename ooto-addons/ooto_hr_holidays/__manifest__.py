# -*- coding: utf-8 -*-
{
    'name': "OOTO - HR holidays",
    'summary': """ OOTO - HR holidays""",
    'description': """ OOTO - HR holidays""",
    'author': "Etech",
    'website': "https://www.etechconsulting-mg.com/",
    'category': 'hr',
    'version': '13',
    'depends': ['base', 'hr_holidays'],
    'data': [
        # security
        'security/ir.model.access.csv',

        # data
        'data/hr_leave_data.xml',

        # views
        'views/hr_leave_follower.xml',
        'views/hr_leave_allocation.xml',
        'views/edit_holiday_status_form.xml'
    ],
    'demo': [],
}
