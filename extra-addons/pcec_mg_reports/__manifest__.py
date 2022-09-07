# -*- coding: utf-8 -*-
{
    'name': "PCEC Malagasy Reports",

    'summary': """
     Plan Comptable des Etablissements de Crédit Etats financiers
        """,

    'description': """
       Plan Comptable des Etablissements de Crédit Etats financiers
    """,

    'author': "Etech consulting",
    'website': "https://www.etechconsulting-mg.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account_accountant', 'account', 'account_reports'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_financial_report_view.xml',
        'data/income_statement_data.xml',
        'data/balance_sheet_active_data.xml',
        'data/balance_sheet_passive_data.xml',

    ],
    # only loaded in demonstration mode
    'demo': [],
}
