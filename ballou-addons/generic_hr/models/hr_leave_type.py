# -*- coding: utf-8 -*-

from odoo import api, fields, models
from lxml import etree


class HolidaysType(models.Model):
    _inherit = "hr.leave.type"

    display_in_payslip = fields.Boolean(deafult=False)
    simple_leave_allocation = fields.Boolean(default=True, inverse='_compute_toggle_simple')
    double_leave_allocation = fields.Boolean(default=False, inverse='_compute_toggle_double')

    @api.depends('simple_leave_allocation')
    @api.onchange('simple_leave_allocation')
    def _compute_toggle_simple(self):
        for rec in self:
            if rec.simple_leave_allocation:
                rec.double_leave_allocation = False
            else:
                rec.double_leave_allocation = True

    @api.depends('double_leave_allocation')
    @api.onchange('double_leave_allocation')
    def _compute_toggle_double(self):
        for rec in self:
            if rec.double_leave_allocation:
                rec.simple_leave_allocation = False
            else:
                rec.simple_leave_allocation = True
