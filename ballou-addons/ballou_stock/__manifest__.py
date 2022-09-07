# -*- coding: utf-8 -*-
{
    'name': "ballou_stock",

    'summary': """
        Specific needs of Ballou which are related to Inventory module""",

    'description': """
        Specific needs of Ballou which are related to Inventory module
    """,

    'author': "Etech consulting",
    'website': "www.etechconsulting-mg.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        #'views/views.xml',
        #'views/templates.xml',
        'report/report_deliveryslip.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
}
