# -*- coding: utf-8 -*-

from odoo import models, fields, api
from . import convertion


class SaleOrderReportDocument(models.AbstractModel):
    _name = 'report.sale.report_saleorder'

    @api.model
    def _get_report_values(self, docids, data=None):

        total = self.env['sale.order'].browse(docids[0]).amount_total
        currency_id = self.env['sale.order'].browse(docids[0]).currency_id
        docs = self.env['sale.order'].browse(docids)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'sale.order',
            'data': data,
            'docs': docs,
            'total_words': convertion.trad(total,currency_id.currency_unit_label),
        }