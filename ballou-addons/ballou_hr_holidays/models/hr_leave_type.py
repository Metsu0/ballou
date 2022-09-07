# -*- coding: utf-8 -*-

from odoo import api, fields, models
from lxml import etree


class HolidaysType(models.Model):
    _inherit = "hr.leave.type"

    weekend_consideration = fields.Boolean(string='Weekend consideration', default=False)



