# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from psycopg2 import sql

from odoo import tools
from odoo import api, fields, models


class HrPayrollReport(models.Model):
    _inherit = "hr.payroll.report"
    _description = "Payroll Analysis Report"
