# -*- coding: utf-8 -*-

import logging

from odoo.exceptions import ValidationError
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import calendar
from pytz import utc

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    first_approver_can_confirm = fields.Boolean("The first approver can confirm a second time", default=True)

    # Send mail to holidays followers
    def action_approve(self):
        res = super(HrLeave, self).action_approve()

        for holiday in self:
            holidays_followers = self.env['hr.leave.follower'].search([])
            if holidays_followers:
                followers = []
                for follower in holidays_followers:
                    if follower.admin_follower.user_id.partner_id:
                        followers.append(follower.admin_follower.user_id.partner_id.id)
                holiday.message_post(
                    body=_('%s planning for %s has been approved.') % (
                        holiday.holiday_status_id.display_name, holiday.date_from),
                    partner_ids=followers)
        return res

    # Send mail to holidays followers
    def action_refuse(self):
        res = super(HrLeave, self).action_refuse()

        for holiday in self:
            holidays_followers = self.env['hr.leave.follower'].search([])
            if holidays_followers:
                followers = []
                for follower in holidays_followers:
                    if follower.admin_follower.user_id.partner_id:
                        followers.append(follower.admin_follower.user_id.partner_id.id)

                holiday.message_post(
                    body=_('%s planning for %s has been refused.') % (
                        holiday.holiday_status_id.display_name,
                        holiday.date_from
                    ),
                    partner_ids=followers
                )
        return res

    @api.model
    def get_leave_count_on_date(self, employee_id, search_date=date.today()):
        """
        Get leave's count on specified date
        :param employee_id:
        :param search_date:
        :return:
        """
        # Variable init
        my_time = datetime.max.time()
        # Get taken leave
        taken_leave_count = self.get_taken_leaves_between_specific_date(employee_id, search_date)
        # Get allocated leave
        allocated_leaves_ids = self.env['hr.leave.allocation'].search([
            ('confirmation_date', '<=', search_date),
            ('employee_id', '=', employee_id.id),
            ('state', '=', 'validate'),
            ('holiday_status_id.unpaid', '=', False)
        ])
        allocated_regular_leave_count = sum(
            allocated_leaves_ids.filtered(lambda l: l.allocation_type == 'regular').mapped('number_of_days_display')
        )
        allocated_accrual_leave_count = allocated_leaves_ids.filtered(
            lambda l: l.allocation_type == 'accrual'
        ).get_balance_accrual_leaves_count(date_to=datetime.combine(search_date, my_time))
        return allocated_accrual_leave_count + allocated_regular_leave_count - abs(taken_leave_count)

    def get_all_date_between_two_date(self, start_date, end_date):
        """
        Given two instances of ``datetime.date``, generate a list of dates on
        the 1st of every month between the two dates (inclusive).

        """
        year = start_date.year
        month = start_date.month

        while (year, month) <= (end_date.year, end_date.month):
            yield datetime(year, month, 1)

            # Move to the next month.  If we're at the end of the year, wrap around
            # to the start of the next.
            if month == 12:
                month = 1
                year += 1
            else:
                month += 1

    def get_taken_leaves_between_specific_date(self, employee_id, search_date):
        """
        Get all taken leaves between search_date and the first leave
        :param employee_id:
        :param search_date:
        :return:
        """
        leave_domain = ['|',
                        ('request_date_to', '<=', search_date),
                        ('request_date_from', '<=', search_date),
                        ('employee_id', '=', employee_id.id),
                        ('state', '=', 'validate'),
                        ('holiday_status_id.unpaid', '=', False)
                        ]
        leave_ids = self.env['hr.leave'].search(leave_domain, order='request_date_from')
        taken = 0
        if leave_ids:
            dt_start = datetime.combine(leave_ids[0].request_date_from, datetime.min.time())
            dt_end = datetime.combine(search_date, datetime.min.time())
            for dt in self.get_all_date_between_two_date(dt_start, dt_end):
                date_from = fields.Date.to_date(dt)
                date_to = fields.Date.to_date((dt + relativedelta(months=+1, day=1, days=-1)).date())
                if date_to <= search_date:
                    taken += self.get_taken_leave_by_date(employee_id, date_to, date_from, True)
        return taken

    @api.model
    def get_taken_leave_date_in_date_range(self, employee_id, date_to, date_from=False):
        """
        Get leaves date in date range
        :param employee_id:
        :param date_to:
        :param date_from:
        :return:
        """
        # Variable init
        date_from_list = []
        date_to_list = []
        leaves_date_list = []
        leave_ids = []
        leave_from_domain = [
            ('request_date_from', '<=', date_to),
            ('employee_id', '=', employee_id.id),
            ('state', '=', 'validate'),
            ('holiday_status_id.unpaid', '=', False)
        ]
        leave_to_domain = [
            ('request_date_to', '<=', date_to),
            ('employee_id', '=', employee_id.id),
            ('state', '=', 'validate'),
            ('holiday_status_id.unpaid', '=', False)
        ]
        if date_from:
            leave_from_domain.append(('request_date_from', '>=', date_from))
            leave_to_domain.append(('request_date_to', '>=', date_from))
        leave_from_ids = self.env['hr.leave'].search(leave_from_domain, order='request_date_from')
        leave_to_ids = self.env['hr.leave'].search(leave_to_domain, order='request_date_from')
        [leave_ids.append(leave_id) for leave_id in leave_to_ids + leave_from_ids if leave_id not in leave_ids]
        # Set date from and date to list values
        for leave_id in leave_ids:
            date_to_list.append(leave_id.request_date_to)
            date_from_list.append(leave_id.request_date_from)
        # Set leaves_date_list value
        current_list = []
        for i in range(0, len(date_to_list)):
            if (i + 1) % 5:
                current_list.append((date_from_list[i], date_to_list[i]))
            else:
                leaves_date_list.append(current_list)
                current_list = [(date_from_list[i], date_to_list[i])]
        leaves_date_list.append(current_list)
        return leaves_date_list

    @api.model
    def is_global_day(self, day_date, global_leave_ids):
        res = global_leave_ids.filtered(lambda l: l.date_from <= day_date and l.date_to >= day_date)
        return True if res else False

    @api.model
    def get_taken_leave_by_date(self, employee_id, date_to, date_from, is_payslip=False, domain=None,
                                work_day_count=False):
        """
        :param employee_id:
        :param date_to:
        :param date_from:
        :return:
        """
        date_from = datetime.combine(date_from, datetime.min.time())
        date_to = datetime.combine(date_to, datetime.max.time())
        resource_calendar_id = employee_id.company_id.resource_calendar_id
        if is_payslip:
            date_from_last_month = False
            if date_from.weekday() == 6:
                date_from_last_month = date_from - timedelta(days=2)
            if date_from.weekday() == 5:
                date_from_last_month = date_from - timedelta(days=1)
            add_count = 0.0
            if date_from_last_month:
                leaves_last_ids = employee_id._get_leave_days_data(date_from_last_month, date_from,
                                                                   calendar=resource_calendar_id, is_payslip=is_payslip,
                                                                   domain=domain)
                if leaves_last_ids.filtered(lambda l: l.holiday_id):
                    if employee_id.direction_id.friday_take_in_account:
                        if date_from.weekday() == 6:
                            if not self.is_global_day(date_from, resource_calendar_id.global_leave_ids):
                                add_count += 1
                        if date_from.weekday() == 5:
                            sunday = date_from + timedelta(days=1)
                            for day_dt in [sunday, date_from]:
                                if not self.is_global_day(day_dt, resource_calendar_id.global_leave_ids):
                                    add_count += 1
            leaves_ids = employee_id._get_leave_days_data(date_from, date_to, calendar=resource_calendar_id,
                                                          is_payslip=is_payslip, domain=domain)
            taken_leave = add_count
            if work_day_count:
                all_type = leaves_ids.filtered(
                    lambda l: not l.holiday_id.holiday_status_id.is_maternity_absence).mapped(
                    'holiday_id.holiday_status_id')
                leave_by_type = []
                for type in all_type:
                    type_count = 0
                    l_ids = leaves_ids.filtered(
                        lambda
                            l: l.holiday_id.holiday_status_id == type and not l.holiday_id.holiday_status_id.is_maternity_absence)
                    for leave in l_ids:
                        l_date_from = date_from if leave[0].date_from < date_from else leave[0].date_from
                        l_date_to = date_to if leave[0].date_to > date_to else leave[0].date_to
                        type_count += \
                            employee_id._get_leave_days_data(l_date_from, l_date_to, calendar=resource_calendar_id)[
                                'days']
                    leave_by_type.append((type, type_count))
                return leave_by_type
            else:
                for leave in leaves_ids:
                    l_date_from = date_from if leave[0].date_from < date_from else leave[0].date_from
                    l_date_to = date_to if leave[0].date_to > date_to else leave[0].date_to
                    if not leave.holiday_id.holiday_status_id.unpaid:
                        if leave.holiday_id.holiday_status_id.is_maternity_absence:
                            taken_leave += (l_date_to.date() - l_date_from.date()).days + 1
                        else:
                            taken_leave += \
                            employee_id._get_leave_days_data(l_date_from, l_date_to, calendar=resource_calendar_id)['days']
                return taken_leave
        else:
            res = employee_id._get_leave_days_data(date_from, date_to, calendar=resource_calendar_id)['days']
            return res

    @api.model
    def get_taken_leave_in_date_range(self, employee_id, date_to, date_from=False):
        """
        Get leaves information according the payslip
        :return:
        """
        # Variable init
        leave_from_domain = [
            ('request_date_from', '<=', date_to),
            ('employee_id', '=', employee_id.id),
            ('state', '=', 'validate'),
            ('holiday_status_id.unpaid', '=', False)
        ]
        leave_to_domain = [
            ('request_date_to', '<=', date_to),
            ('employee_id', '=', employee_id.id),
            ('state', '=', 'validate'),
            ('holiday_status_id.unpaid', '=', False)
        ]
        if date_from:
            leave_from_domain.append(('request_date_from', '>=', date_from))
            leave_to_domain.append(('request_date_to', '>=', date_from))
        # Add date_to in month range
        date_to = date(date_to.year, date_to.month, calendar.monthrange(date_to.year, date_to.month)[1])
        leave_from_ids = self.env['hr.leave'].search(leave_from_domain)
        leave_to_ids = self.env['hr.leave'].search(leave_to_domain)
        taken = 0
        #
        resource_calendar_id = employee_id.company_id.resource_calendar_id

        for leave_id in set(leave_to_ids + leave_from_ids):
            if leave_id.request_date_from.month == leave_id.request_date_to.month:
                taken += leave_id.number_of_days
            elif date_to.month < leave_id.request_date_to.month:
                monthrange = calendar.monthrange(date_to.year, date_to.month)
                taken += monthrange[1] - leave_id.request_date_from.day + 1
            else:
                taken += leave_id.request_date_to.day

        return taken

    @api.model
    def get_allocated_leave(self, employee_id, date_from, date_to):
        """
        Get allocated leave on the month
        :return:
        """
        # Variable init
        date_from = date_from
        date_to = date_to
        my_time = datetime.max.time()
        regular_allocation_ids = self.env['hr.leave.allocation'].search([
            ('confirmation_date', '>=', date_from),
            ('confirmation_date', '<=', date_to),
            ('employee_id', '=', employee_id.id),
            ('allocation_type', '=', 'regular'),
            ('state', '=', 'validate'),
            ('holiday_status_id.unpaid', '=', False)
        ])
        accrual_allocation_ids = self.env['hr.leave.allocation'].search([
            ('confirmation_date', '<=', date_to),
            ('employee_id', '=', employee_id.id),
            ('allocation_type', '=', 'accrual'),
            ('state', '=', 'validate'),
            ('holiday_status_id.unpaid', '=', False)
        ])
        balance_accrual_allocation = accrual_allocation_ids.get_balance_accrual_leaves_count(
            date_to=datetime.combine(date_to, my_time),
            date_from=datetime.combine(date_from, my_time)
        )
        return sum(regular_allocation_ids.mapped('number_of_days_display')) + balance_accrual_allocation

    @api.model
    def get_is_exceptional_day_available(self, front=False, employee_id=None, date_from=None, number_of_days=False):
        day_exceptional_permission = int(
            self.env['ir.config_parameter'].sudo().get_param('ooto_hr_holidays.day_exceptional_permission', 0))
        if front:
            date_from = datetime.combine(date_from, datetime.min.time())
            first_day = date_from.min.replace(year=date_from.year)
            last_day = date_from.max.replace(year=date_from.year)
            leaves_ids = self.env['hr.leave'].search([
                ('employee_id', '=', employee_id.id),
                ('request_date_from', '<=', last_day.date()),
                ('request_date_to', '>=', first_day.date()),
                ('holiday_status_id.is_exceptional_permission', '=', True),
                ('state', 'not in', ['refuse', 'cancel'])
            ])
        else:
            first_day = self.date_from.min.replace(year=self.date_from.year)
            last_day = self.date_from.max.replace(year=self.date_from.year)
            leaves_ids = self.env['hr.leave'].search([
                ('employee_id', '=', self.employee_id.id),
                ('request_date_from', '<=', last_day.date()),
                ('request_date_to', '>=', first_day.date()),
                ('holiday_status_id.is_exceptional_permission', '=', True),
                ('state', 'not in', ['refuse', 'cancel'])
            ])
        taken_leave = 0.0
        for leave in leaves_ids:
            l_date_from = first_day if leave[0].date_from < first_day else leave[0].date_from
            l_date_to = last_day if leave[0].date_to > last_day else leave[0].date_to
            taken_leave += leave._get_number_of_days(l_date_from, l_date_to, leave.employee_id.id)["days"]
        number_of_days = number_of_days if front else 0
        res = {
            'day': day_exceptional_permission - taken_leave,
            'can_take': False if day_exceptional_permission < (taken_leave + number_of_days) else True
        }
        return res

    @api.constrains('number_of_days', 'holiday_status_id', 'request_date_from', 'request_date_to')
    def _check_holidays_except(self):
        for holiday in self:
            if holiday.holiday_status_id and holiday.holiday_status_id.is_exceptional_permission:
                day_ex = holiday.get_is_exceptional_day_available()
                date_complete = holiday.request_date_from and holiday.request_date_to
                if date_complete and holiday.holiday_status_id and holiday.employee_id and not day_ex['can_take']:
                    raise ValidationError(_("The number of exceptional leave remaining is not sufficient"))


class HrLeaveType(models.Model):
    _inherit = "hr.leave.type"

    is_exceptional_permission = fields.Boolean("Exceptional permission")

    @api.onchange('is_exceptional_permission')
    def onchange_is_exceptional_permission(self):
        if self.is_exceptional_permission:
            self.allocation_type = 'no'
