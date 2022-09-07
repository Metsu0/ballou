# -*- encoding: utf-8 -*-


from odoo import models, fields, exceptions, api, _


class ReportAccountFinancialReport(models.Model):
    _inherit = 'account.financial.html.report'


class AccountFinancialReportLin(models.Model):
    _inherit = 'account.financial.html.report.line'

