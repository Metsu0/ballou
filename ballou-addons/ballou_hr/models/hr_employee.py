# -*- coding: utf-8 -*-

import logging
from datetime import date, datetime, time, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from dateutil import relativedelta

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    seniority = fields.Char(string='Seniority', compute='_get_seniority', groups="hr.group_hr_user")
    cnaps_number = fields.Char(string='CNAPS number', groups="hr.group_hr_user")
    years = fields.Integer(string="Years", groups="hr.group_hr_user")
    months = fields.Integer(string="Months", groups="hr.group_hr_user")
    days = fields.Integer(string="Days", groups="hr.group_hr_user")
    cin_validity_date = fields.Date(string='CIN validity date', groups="hr.group_hr_user")
    passport_validity_date = fields.Date(string='Passport validity date', groups="hr.group_hr_user")
    internal_classification = fields.Many2one(comodel_name="hr.internal.classification",
                                              string="Internal classification",
                                              related="contract_id.internal_classification", store=True,
                                              groups="hr.group_hr_user")
    dependent_ids = fields.One2many('hr.dependent', 'employee_id', 'Dependent lines', groups="hr.group_hr_user")
    children = fields.Integer(compute='_compute_children_number', store=True, groups="hr.group_hr_user")

    def _get_seniority(self):
        seniority = ''
        if self.first_contract_date:
            # dateStart = datetime.combine(fields.Date.from_string('2021-03-10'), time.min)
            dateStart = datetime.combine(self.first_contract_date, time.min)
            diff = relativedelta.relativedelta(datetime.now(), dateStart)
            if diff.years:
                if diff.years == 1:
                    seniority = seniority + str(diff.years) + ' ' + _('year') + ' '
                else:
                    seniority = seniority + str(diff.years) + ' ' + _('years') + ' '
                self.years = diff.years
            if diff.months:
                if diff.months == 1:
                    if seniority != '':
                        seniority = seniority + _('and') + ' '
                    seniority = seniority + str(diff.months) + ' ' + _('month') + ' '
                else:
                    if seniority != '':
                        seniority = seniority + _('and') + ' '
                    seniority = seniority + str(diff.months) + ' ' + _('months') + ' '
                self.months = diff.months
            if diff.days:
                if diff.days == 1:
                    if seniority != '':
                        seniority = seniority + _('and') + ' '
                    seniority = seniority + str(diff.days) + ' ' + _('day')
                else:
                    if seniority != '':
                        seniority = seniority + _('and') + ' '
                    seniority = seniority + str(diff.days) + ' ' + _('days')
                self.days = diff.days
            if seniority == '':
                seniority = '0 ' + _('day')
        self.seniority = seniority

    @api.depends('dependent_ids')
    def _compute_children_number(self):
        """
        Compute children number
        :return:
        """
        for rec in self:
            rec.children = len(rec.dependent_ids)
