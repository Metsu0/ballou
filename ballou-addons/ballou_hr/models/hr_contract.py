# -*- coding: utf-8 -*-

import logging
from datetime import date, datetime, time, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from dateutil import relativedelta

from odoo import api, fields, models, _


class HrContract(models.Model):
    _inherit = "hr.contract"

    internal_classification = fields.Many2one(comodel_name="hr.internal.classification",
                                              string="Internal classification")
