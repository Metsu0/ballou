# -*- coding: utf-8 -*-

from odoo import models, fields, api
from . import convertion


class ReportInvoiceWithPaymentInherit(models.AbstractModel):
    _inherit = 'report.account.report_invoice'

    @api.model
    def _get_report_values(self, docids, data=None):

        total = self.env['account.move'].browse(docids[0]).amount_total
        currency_id = self.env['account.move'].browse(docids[0]).currency_id
        total_words = []
        total_words.append(convertion.trad(total,currency_id.currency_unit_label))

        rslt = super()._get_report_values(docids, data)
        rslt['total_words'] = total_words
        return rslt
