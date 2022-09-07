# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HrContract(models.Model):
    _inherit = 'hr.contract'

    payslip_payment_mode_id = fields.Many2one('hr.payslip.payment.mode', string='Payment mode',
                                              track_visibility='onchange')