# -*- coding: utf-8 -*-
{
    'name': "sanction",

    'summary': """
        """,

    'description': """
    """,

    'author': "Etch-consulting",
    'website': "",

    'category': 'Human Resources/Sanction',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/sanction_type_data.xml',
        'views/hr_sanction_view.xml',
        'views/hr_employee_view.xml',
    ],
}
