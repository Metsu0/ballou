# -*- coding: utf-8 -*-
{
    'name': "Ooto - Annuaire",

    'summary': """
         Ooto - Annuaire""",

    'description': """
       Ooto - Annuaire
    """,

    'author': "etech",
    'website': "https://www.etechconsulting-mg.com/",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'hr', 'ooto_base_security', 'ooto_onboarding'],
    'data': [
        # security
        "security/security.xml",
        "security/ir.model.access.csv",
 
        # data
        "data/ooto_annuaire_configuration.xml",
        "data/annuaire_tutorial_data.xml",
 
        # views
        "views/ooto_annuaire.xml",
        "views/ooto_annuaire_configuration.xml",
        "views/annuaire_tutorial.xml",
        "views/ooto_annuaire_rules_views.xml",
        "views/res_users_views.xml",
        "views/hr_employee_views.xml",
    ],
}
