# -*- coding: utf-8 -*-
{
    'name': "OOTO - HR holidays Front",
    'summary': """ OOTO - HR holidays Front""",
    'description': """ OOTO - HR holidays Front""",
    'author': "Etech - Ravalison A. Tsiorimampionina",
    'website': "https://www.etechconsulting-mg.com/",
    'category': 'hr',
    'version': '12',
    'depends': ['ooto_hr_holidays',
                'portal_leave', 'website', 'ooto_base_security', 'ooto_hr_account'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/assets.xml',
        'data/website_data.xml',
        'views/template_portal_leave.xml',
        'views/res_config_settings_views.xml',
    ],
    'demo': [],
}
