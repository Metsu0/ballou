# -*- coding: utf-8 -*-

from odoo import api, fields, models


class HrPayslipPaymentMode(models.Model):
    _inherit = 'hr.payslip.payment.mode'

    contract_ids = fields.One2many('hr.contract', 'payslip_payment_mode_id', 'Contracts')
