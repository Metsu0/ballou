# -*- coding: utf-8 -*-

from odoo import api, fields, models


class HrLeaveType(models.Model):
    _inherit = "hr.leave.type"

    allow_credit = fields.Boolean(
        string='Allow Credit',
        help=(
            'If set to true, employees would be able to make requests for this'
            ' leave type even if allocated amount is insufficient.'
        ),
    )
    creditable_employee_ids = fields.Many2many(
        string='Creditable Employees',
        comodel_name='hr.employee',
        help='If set, limits credit allowance to specified employees',
    )
    creditable_employee_category_ids = fields.Many2many(
        string='Creditable Employee Tags',
        comodel_name='hr.employee.category',
        help=(
            'If set, limits credit allowance to employees with at least one of'
            ' specified tags'
        ),
    )
    creditable_department_ids = fields.Many2many(
        string='Creditable Departments/Services',
        comodel_name='hr.department',
        help=(
            'If set, limits credit allowance to employees of specified'
            ' departments/services'
        ),
    )



