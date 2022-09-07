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


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'
    employee_id = fields.Many2one('hr.employee', compute='_compute_employee_id', string="Employee")

    def _compute_employee_id(self):
        for partner in self:
            partner.employee_id = False
            user = self.env['res.users'].search([('partner_id', '=', partner.id)])
            if user:
                employee = self.env['hr.employee'].search([('user_id', '=', user.id)])
                if employee:
                    employee.with_context(set_name=True).name = "%s %s" % (
                    employee.lastname or '', employee.firstname or '')
                    partner.employee_id = employee.id
            else:
                partner.employee_id = False
