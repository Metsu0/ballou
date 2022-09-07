# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'
    _description = 'Salary Rule'

    appears_in_payslip_resume = fields.Boolean(default=False)


class HrPayrollStructure(models.Model):
    _inherit = 'hr.payroll.structure'
    _description = 'Salary Structure'

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
