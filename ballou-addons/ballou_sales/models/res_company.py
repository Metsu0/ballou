# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    report_footer_receipt = fields.Text("Bas de page du ticket de caisse")