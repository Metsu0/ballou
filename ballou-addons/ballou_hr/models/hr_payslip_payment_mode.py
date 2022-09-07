# -*- coding: utf-8 -*-

from odoo import api, fields, models


class HrPayslipPaymentMode(models.Model):
    _name = 'hr.payslip.payment.mode'
    _description = 'Payment Mode (ex: Virement, Cheque, ...)'

    name = fields.Char(string='Name', required=True)
    note = fields.Text(string='Description')
