# coding: utf-8

from datetime import datetime, date
from locale import Error
from dateutil.relativedelta import MO, relativedelta
import calendar
from odoo.exceptions import UserError

from odoo import models, fields, api, _


class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    unpaid = fields.Boolean(default=False)

    