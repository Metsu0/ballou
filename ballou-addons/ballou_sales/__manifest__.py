# -*- coding: utf-8 -*-
{
    'name': "ballou_sales",

    'summary': """
        Specific needs of Ballou which are related to Sale module""",

    'description': """
        Specific needs of Ballou, concerning Sale module
    """,

    'author': "Etech consulting",
    'website': "www.etechconsulting-mg.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','stock','account','web','product'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/ballou_sales_security.xml',
        # 'views/views.xml',
        # 'views/templates.xml',
        'views/assets.xml',
        'report/ballou_external_layout.xml',
        'views/account_journal_form_inherit.xml',
        'views/base_view_partner_form_inherit.xml',
        'views/base_document_layout_views.xml',
        'views/res_partner_views.xml',
        'views/product_views.xml',
        'views/product_template_views.xml',
        'views/sale_order_inherit.xml',
        'report/sale_report_templates_inherit.xml',
        'report/account_report_invoice_document_inherit.xml',
        'data/ballou_sales_data.xml',
        'report/report_account_move_receipt_template.xml',
        'report/report_account_move_receipt.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
