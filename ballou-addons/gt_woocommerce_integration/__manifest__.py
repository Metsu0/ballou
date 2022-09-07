# -*- encoding: utf-8 -*-
##############################################################################
#
#    Globalteckz
#    Copyright (C) 2012 (http://www.globalteckz.com)
#
##############################################################################

{
    "name": "Odoo Woocommerce Connector",
    "author": "Globalteckz",
    "category": "Sales",
    "depends": ['base', 'sale_shop', 'account','product_images_olbs', 'delivery', 'stock', 'sale'],
    "description": """
Odoo Woocommerce Connector to manage all your woocommerce from odoo

    """,
    'summary': 'Odoo woocommerce connector will help you to manage all your operations in Odoo Amazon Odoo Bridge(AOB) Amazon Odoo connector Odoo Amazon bridge Odoo amazon connector Connectors Odoo bridge Amazon to odoo Manage orders Manage products Import products Import customers Import orders Ebay to Odoo Odoo multi-channel bridge Multi channel connector Multi platform connector Multiple platforms bridge Connect Amazon with odoo Amazon bridge Flipkart bridge Woocommerce odoo bridge Odoo woocommerce bridge Ebay odoo bridge Odoo ebay bridge Multi channel bridge Prestashop odoo bridge Odoo prestahop Akeneo bridge Marketplace bridge Multi marketplace connector Multiple marketplace platform odoo shopify shopify connector shopify bridge shipstation connector shipstation integration shipstation bridge',
    "price": "295.00",
    "currency": "USD",
    'website': 'http://www.globalteckz.com',
    "license" : "Other proprietary",
    'images': ['static/description/banner.gif'],
    'website': 'http://www.globalteckz.com',
    "data": [
        'security/woocommerce_security.xml',
        'security/ir.model.access.csv',
        'data/product_data.xml',
        'data/scheduler.xml',
        'data/woocom_sequence_data.xml',
        # 'views/sale_analysis_view.xml',
        'views/wocommerce_integration_view.xml',
        'views/sale_shop_view.xml',
        # 'views/woocom_account_view.xml',
        'wizard/woocom_connector_wizard_view.xml',
        'wizard/woocom_export_categ_view.xml',
        'wizard/woocom_export_product_view.xml',
        'wizard/woocom_export_order_view.xml',
        'wizard/woocom_export_customer_view.xml',
        'views/woocommerce_dashboard_view.xml',
        'views/order_workflow_view.xml',
        'views/product_attribute_view.xml',
        'views/coupon_view.xml',
        'views/product_tag_view.xml',
        'views/woocom_product_view.xml',
        'views/res_partner_view.xml',
        'views/carrier_woocom_view.xml',
        'views/payment_gatway_view.xml',
        'views/woocom_order_view.xml',
        'views/stock_view.xml',
        'views/woocommerce_log_view.xml',
        'views/wocommerce_menus.xml',

    ],
    "installable": True,
    "active": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
