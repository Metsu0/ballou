# -*- encoding: utf-8 -*-

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2020 eTech (<https://www.etechconsulting-mg.com/>). All Rights Reserved
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
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

{
    'name': "Madagascar - Accounting Reports without pcg ",
    'version': '1.1',

    'description': """
Accounting reports for Madagascar
    """,

    'author': "eTech",
    'website': "https://www.etechconsulting-mg.com/",
    'category': 'Accounting/Accounting',

    # any module necessary for this one to work correctly
    'depends': [
        # 'base',
        # 'l10n_mg',
        'account_reports',
    ],

    # always loaded
    'data': [
        # SECURITY
        'security/ir.model.access.csv',


        # DATA
        'data/account_financial_html_report_data.xml',
        'data/account_result_nature_view.xml',
        'data/account_result_fonction_view.xml',
        'data/account_balance_sheet_active.xml',
        'data/account_balance_sheet_equity_and_liabilities.xml',

        # 'data/account_financial_passif.xml',
        # 'data/account_flux_tresorerie_directe.xml',
        # 'data/account_flux_tresorerie_indirect_view.xml',
        'data/evcp_template.xml',
        'data/indirect_cash_flow_template.xml',
        # VIEW
        'views/evcp_template_view.xml',
        'views/cash_flow_wizard_view.xml',
        'views/account_financial_report_inherit.xml',
        'views/action_manager.xml',

    ],

    'qweb': [

    ],

    # only loaded in demonstration mode
    'demo': [

    ],

    'auto_install': False,
    'installable': True,
    'application': False,
}
