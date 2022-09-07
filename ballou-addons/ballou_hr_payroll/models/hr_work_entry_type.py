# -*- encoding: utf-8 -*-

from odoo import models, fields


class HrWorkEntryType(models.Model):
    _inherit = 'hr.work.entry.type'

    applied_in_payslip = fields.Boolean(default=True)