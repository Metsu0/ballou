# -*- coding: utf-8 -*-
{
    'name': "SIRH - HR Employee Front ",
    'version': '13.0.1.0.0',
    'sequence': -15,
    'summary': '',
    'author': 'eTech Consulting',
    'website': 'http://www.etechconsulting-mg.com',
    'depends': ['base', 'portal', 'ooto_hr_account', 'sirh_base_security'],
    'data': [
        # views
        'views/assets.xml',
        'views/sirh_portal.xml',
    ],
    'qweb': [],
    'demo': [],
    'installable': True,
    'application': False,
}
