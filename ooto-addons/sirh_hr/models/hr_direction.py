# -*- coding: utf-8 -*-

import base64
import logging

from datetime import datetime, date, timedelta
from dateutil import relativedelta

from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError, AccessError
from odoo.modules.module import get_module_resource

_logger = logging.getLogger(__name__)


class Direction(models.Model):
    _name = 'hr.direction'

    name = fields.Char(string='Name')
    executive_id = fields.Many2one('hr.employee', string='Executive')
    department_ids = fields.Many2many('hr.department', string='CC', compute='_compute_department_linked')

    def set_default_company(self):
        return self.env.user.company_id

    company_id = fields.Many2one('res.company', string='Company', default=set_default_company)

    def _compute_department_linked(self):
        for rec in self:
            departments = self.env['hr.department'].search([('direction_id', '=', rec.id)])
            rec.department_ids = departments
