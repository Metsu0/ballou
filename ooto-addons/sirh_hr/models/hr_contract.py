# -*- coding: utf-8 -*-
from datetime import datetime, time

import babel
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _, tools


class HrContract(models.Model):
    _inherit = 'hr.contract'

    contract_category_id = fields.Many2one('hr.contract.category', string='Category', track_visibility='onchange')
    payslip_payment_mode_id = fields.Many2one('hr.payslip.payment.mode', string='Payment mode',
                                              track_visibility='onchange')
    contract_type = fields.Selection([('cdi', 'CDI'), ('cdd', 'CDD')],
                                     string='Contract Type', default='cdi',
                                     required=True, track_visibility='onchange')
    duration = fields.Char(string='Duration', track_visibility='onchange')
    duration_years = fields.Integer(string='Year(s)')
    duration_months = fields.Integer(string='Month(s)')
    duration_days = fields.Integer(string='Day(s)')
    date_start = fields.Date(track_visibility='onchange')
    date_end = fields.Date(track_visibility='onchange', compute='_compute_date_end', store=True)
    trial_date_end = fields.Date(track_visibility='onchange')
    struct_id = fields.Many2one(track_visibility='onchange')
    job_id = fields.Many2one(track_visibility='onchange')
    coach_id = fields.Many2one(related='employee_id.coach_id')
    trial_period_state = fields.Selection(
        [('in_progress', 'In progress'),
         ('validated', 'Validated'),
         ('refused', 'Refused')
         ], string="State of the trial period", default='in_progress')
    date_trial_period_refused = fields.Date("Trial period refused")

    @api.onchange('trial_period_state')
    def onchange_trial_period_state(self):
        for rec in self:
            if rec.trial_period_state == 'refused':
                rec.date_trial_period_refused = datetime.now().date()
            else:
                rec.date_trial_period_refused = False

    @api.depends('date_start', 'contract_type', 'duration_years', 'duration_months', 'duration_days')
    def _compute_date_end(self):
        """
        Method to calculate date_end if contract_type is CDD and also to format duration which has to display on
        read mode.
        :return: None
        """
        if self.contract_type == 'cdi':
            self.duration_years = 0
            self.duration_months = 0
            self.duration_days = 0
            self.date_end = None
            self.duration = ""
        elif self.contract_type == 'cdd' or self.duration_years or self.duration_months or self.duration_days:
            self.date_end = self.date_start + relativedelta(years=self.duration_years, months=self.duration_months,
                                                            days=self.duration_days)
            self.duration = str(self.duration_years) + _(' year(s) ') + str(self.duration_months) + _(
                ' month(s) ') + str(self.duration_days) + _(' day(s)')

    @api.model
    def recompute_all_date_end(self):
        """
        Method recompute date_end if contract_type is CDD and also to format duration which has to display on
        read mode.
        :return: None
        """
        contract_ids = self.search([('contract_type', '=', 'cdd')])
        for contract_id in contract_ids:
            contract_id.date_end = contract_id.date_start + relativedelta(years=contract_id.duration_years, months=contract_id.duration_months,
                                                            days=contract_id.duration_days)
            contract_id.duration = str(contract_id.duration_years) + _(' year(s) ') + str(contract_id.duration_months) + _(
                ' month(s) ') + str(contract_id.duration_days) + _(' day(s)')
        return True

    def format_date(self, date=fields.date.today()):
        """
        Format date according user language (Day Month Year)
        :param date: date to format
        :return:
        """
        locale = self.env.context.get('lang') or 'en_US'
        ttyme = datetime.combine(fields.Date.from_string(date), time.min)
        return tools.ustr(babel.dates.format_date(date=ttyme, format='d MMMM y', locale=locale)).title()