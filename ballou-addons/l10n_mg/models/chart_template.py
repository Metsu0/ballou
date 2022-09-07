# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountChartTemplate(models.Model):
    _name = 'account.chart.template'
    _inherit = 'account.chart.template'
    _description = 'Templates for Account Chart'

    code_digits = fields.Integer(default=6)




