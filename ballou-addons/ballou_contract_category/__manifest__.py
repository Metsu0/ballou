# -*- coding: utf-8 -*-
{
    'name': "Contract category",

    'summary': """
        """,

    'description': """
    """,
    'author': 'eTech Consulting',
    'website': 'http://www.etechconsulting-mg.com',

    'category': 'Human Resources/Category',
    'version': '0.1',

    'depends': ['hr_contract', 'ballou_hr'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/hr_category_data.xml',
        'views/hr_category_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_contract_views.xml',
    ],
}
