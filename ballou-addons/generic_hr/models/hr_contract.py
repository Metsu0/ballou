# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class HrContract(models.Model):
    _inherit = 'hr.contract'

    payroll_variable_ids = fields.One2many(comodel_name="hr.payroll.variable",
                                           inverse_name="contract_id",
                                           string='Payroll variable')
    input_ids = fields.Many2many('hr.payslip.input.type', compute='compute_structure_type')

    @api.depends('structure_type_id')
    def compute_structure_type(self):
        if self.structure_type_id:
            for contract in self:
                inputs = self.env['hr.payslip.input.type']
                for struct in contract.structure_type_id.struct_ids:
                    inputs |= struct.input_line_type_ids.filtered(lambda e: e.is_input)
                contract.input_ids = inputs


class HrPayrollVariable(models.Model):
    _name = 'hr.payroll.variable'
    _description = 'Hr Payroll Variable'

    input_ids = fields.Many2many('hr.payslip.input.type',
                                 string='Input',
                                 required=True)
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    amount = fields.Float(string='Amount')
    print = fields.Boolean(string='Print')
    contract_id = fields.Many2one('hr.contract',
                                  string='Contract')

    @api.constrains('start_date', 'end_date')
    def get_two_date(self):
        for var in self:
            if (var.start_date and not var.end_date) or (not var.start_date and var.end_date):
                raise ValidationError("Start date and end date must be filled in or not")


class HrPaysLipInputType(models.Model):
    _inherit = 'hr.payslip.input.type'

    is_input = fields.Boolean(string="Is input",
                              default=False)
