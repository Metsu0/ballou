# -*- coding: utf-8 -*-

import base64
import logging

from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError, AccessError
from odoo.modules.module import get_module_resource

_logger = logging.getLogger(__name__)

class HrJob(models.Model):
    _inherit = "hr.job"

    employee_ids = fields.One2many('hr.employee', 'job_id', string='Employees')
    number_of_employees = fields.Integer(string='Number of employees', compute='_get_number_of_employees')
    minimal_salary = fields.Float(string='Minimal salary')
    maximum_salary = fields.Float(string='Maximum salary')

    def _get_number_of_employees(self):
        for data in self:
            data.number_of_employees = len(data.employee_ids)