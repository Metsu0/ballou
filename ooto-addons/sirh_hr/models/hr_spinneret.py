# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class HrEmployeeSpinneret(models.Model):
    _name = 'hr.spinneret'
    _description = 'hr_spinneret'

    name = fields.Char('Name', required=True)
    employee_ids = fields.One2many('hr.employee', 'spinneret_id', string='Employees')
    number_of_employees = fields.Integer(string='Number of employees', compute='_get_number_of_employees')

    def _get_number_of_employees(self):
        for data in self:
            data.number_of_employees = len(data.employee_ids)