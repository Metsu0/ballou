# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    sanction_count = fields.Integer(string="Sanction", compute="_get_sanction_count")

    def _get_sanction_count(self):
        self.sanction_count = self.env['hr.sanction'].search_count([('employee_id', '=', self.id)])
