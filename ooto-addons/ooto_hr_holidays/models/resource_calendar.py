# Copyright 2020 Shabeer VPK
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons.resource.models.resource import Intervals
import calendar
from collections import defaultdict
from odoo.tools import float_utils

from pytz import timezone, utc
from datetime import datetime, time
from dateutil import rrule
from datetime import timedelta

ROUNDING_FACTOR = 16


def string_to_datetime(value):
    """ Convert the given string value to a datetime in UTC. """
    return utc.localize(fields.Datetime.from_string(value))


def datetime_to_string(dt):
    """ Convert the given datetime (converted in UTC) to a string value. """
    return fields.Datetime.to_string(dt.astimezone(utc))


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    def _weekend_intervals(self, start_dt, end_dt, resource=None):
        """ Return the weekend intervals in the given datetime range.
            The returned intervals are expressed in the resource's timezone.
        """
        tz = timezone((resource or self).tz)
        start_dt = start_dt.astimezone(tz)
        end_dt = end_dt.astimezone(tz)
        start = start_dt.date()
        until = end_dt.date()
        result = []
        weekdays = []
        global_leaves = self._global_leave_intervals(start_dt, end_dt, resource or self)
        for attendance in self.attendance_ids:
            weekdays.append(int(attendance.dayofweek))
        # weekdays = [int(attendance.dayofweek) for attendance in self.attendance_ids]
        weekends = [d for d in range(7) if d not in weekdays]
        for day in rrule.rrule(rrule.DAILY, start, until=until, byweekday=weekends):
            last_day = day - timedelta(days=1 if day.weekday() == 5 else 2)
            last_day_is_global = last_day.strftime("%m/%d/%Y %H:%M:%S") in [s.strftime("%m/%d/%Y %H:%M:%S") for s, e, r
                                                                            in global_leaves]
            day_is_global = day.strftime("%m/%d/%Y %H:%M:%S") in [s.strftime("%m/%d/%Y %H:%M:%S") for s, e, r in
                                                                  global_leaves]
            if not last_day_is_global and not day_is_global:
                result.append(
                    (
                        day.replace(hour=8, tzinfo=tz),
                        day.replace(hour=12, tzinfo=tz),
                        self.env['resource.calendar.attendance']
                    )
                )
                result.append(
                    (
                        day.replace(hour=13, tzinfo=tz),
                        day.replace(hour=17, tzinfo=tz),
                        self.env['resource.calendar.attendance']
                    )
                )
        return Intervals(result)

    def _global_leave_intervals(self, start_dt, end_dt, resource=None):
        """ Return the global leave intervals in the given datetime range.
            The returned intervals are expressed in the resource's timezone.
        """
        tz = timezone((resource or self).tz)
        start_dt = start_dt.astimezone(tz)
        end_dt = end_dt.astimezone(tz)
        result = []
        global_leave_ids = self.global_leave_ids.filtered(
            lambda l: l.date_to.date() >= start_dt.date() and l.date_to.date() <= end_dt.date())
        for global_leave in global_leave_ids:
            result.append((datetime.combine(global_leave.date_to, time.min).astimezone(tz),
                           datetime.combine(global_leave.date_to, time.max).astimezone(tz),
                           self.env['resource.calendar.leaves']), )
        return Intervals(result)

    def _attendance_intervals(self, start_dt, end_dt, resource=None, domain=None, tz=None):
        res = super()._attendance_intervals(start_dt=start_dt,
                                            end_dt=end_dt,
                                            resource=resource,
                                            domain=domain,
                                            tz=tz)
        if resource:
            weekend = self._weekend_intervals(start_dt, end_dt, resource or self)
            global_leave = self._global_leave_intervals(start_dt, end_dt, resource or self)
            employee = self.env['hr.employee'].search([('user_id', '=', resource.user_id.id)])
            res = res - (res & global_leave)
            for direction_id in employee.direction_id:
                if direction_id.friday_take_in_account:
                    res = res | weekend
        return res

    def _leave_intervals(self, start_dt, end_dt, resource=None, domain=None, tz=None, is_payslip=False):
        """ Return the leave intervals in the given datetime range.
            The returned intervals are expressed in specified tz or in the calendar's timezone.
        """
        assert start_dt.tzinfo and end_dt.tzinfo
        self.ensure_one()

        # for the computation, express all datetimes in UTC
        resource_ids = [resource.id, False] if resource else [False]
        if domain is None:
            domain = [('time_type', '=', 'leave')]
        domain = domain + [
            ('calendar_id', '=', self.id),
            ('resource_id', 'in', resource_ids),
            ('date_from', '<=', datetime_to_string(end_dt)),
            ('date_to', '>=', datetime_to_string(start_dt)),
        ]

        # retrieve leave intervals in (start_dt, end_dt)
        tz = tz if tz else timezone((resource or self).tz)
        start_dt = start_dt.astimezone(tz)
        end_dt = end_dt.astimezone(tz)
        result = []
        if is_payslip:
            return self.env['resource.calendar.leaves'].search(domain)
        else:
            for leave in self.env['resource.calendar.leaves'].search(domain):
                dt0 = string_to_datetime(leave.date_from).astimezone(tz)
                dt1 = string_to_datetime(leave.date_to).astimezone(tz)
                for i in [1, 2]:
                    if dt1.weekday() == 4 + i and dt0.weekday() <= 4:
                        dt1 -= timedelta(days=i)
                result.append((max(start_dt, dt0), min(end_dt, dt1), leave))

            return Intervals(result)

    @api.model
    def check_is_friday(self, list_date):
        """
        check if all date in list_date is a Friday
        :param list_date: list of items in intervals
        :return: True if all date is a Friday, else False
        """
        return all([dt.date().weekday() == 4 for dt in list_date]) if list_date else False

    @api.model
    def check_additional_days(self, list_date):
        """
        Count the additional days if there are holidays taken on a Friday
        :param list_date: list of items in intervals
        :return: day_additional : additional days
        """
        day_additional = 0.0
        for dt in list_date:
            try:
                is_not_week_next_in_list = not self.check_is_week_next(dt[0].date(), list_date)
                is_afternoon = dt[2].day_period == 'afternoon' and ((dt == list_date[-1]) | is_not_week_next_in_list)
                list_date_morning = [l[0].date() for l in list_date if l[2].day_period == 'morning']
                continue_date = (dt[0] + timedelta(days=3)).date() in list_date_morning
                is_friday = self.check_is_friday([dt[0]])
                if is_friday and is_afternoon and is_not_week_next_in_list and not continue_date:
                    day_additional += self.with_context(
                        from_leave=self.env.context.get('from_leave', False)).check_next_weekend(dt[0])
            except Exception as e:
                print(e)
        return day_additional

    @api.model
    def check_is_week_next(self, date_fri, list_date):
        """
        Check if the date following date_fri is a weekend in list_date which is the time off interval
        :param date_fri: friday date
        :param list_date: list of items in intervals
        :return: True if next day is saturday, else False
        """
        result = False
        list_date = [d[0].date() for d in list_date]
        list_date = list(dict.fromkeys(list_date))
        if list_date[list_date.index(date_fri)] != list_date[-1]:
            result = True if list_date[list_date.index(date_fri) + 1].weekday() == 5 else False
        return result

    @api.model
    def check_next_weekend(self, date_fri):
        """
        Count the following weekend if it is still in the current month, if so, add the remaining days
        :param date_fri: friday date
        :return: count next day in current month
        """
        tz = timezone((self).tz)
        days = 0.0
        friday_is_global = date_fri.date() in [d.date() for d in self.global_leave_ids.mapped('date_to')]
        global_leave = [d.replace(tzinfo=tz).date() for d in self.global_leave_ids.mapped('date_to')]
        is_from_leave = self.env.context.get('from_leave', False)
        for i in [1, 2]:
            we_is_global = (date_fri + timedelta(days=i)).date() in global_leave
            same_month = (date_fri + timedelta(days=i)).date().month == date_fri.date().month
            if (is_from_leave | same_month) and not friday_is_global and not we_is_global:
                days += 1.0
        return days

    def _get_days_data(self, intervals, day_total):
        """
        helper function to compute duration of `intervals`
        expressed in days and hours.
        `day_total` is a dict {date: n_hours} with the number of hours for each day.

        ==*==
        Override the native method and add the weekends (2 days) if friday_take_in_account is True
        and the half day of Friday is taken by the employee
        ==*==

        """
        # start
        we_additional = 0.0
        employee_id = self.env.context.get('employee_id', False)
        try:
            if employee_id:
                friday_take_in_account = employee_id.direction_id.friday_take_in_account if employee_id.direction_id else False
                if friday_take_in_account:
                    we_additional = self.with_context(
                        from_leave=self.env.context.get('from_leave', False)).check_additional_days(intervals._items)
        except Exception as e:
            print(e)
        # end overriding

        day_hours = defaultdict(float)
        for start, stop, meta in intervals:
            day_hours[start.date()] += (stop - start).total_seconds() / 3600

        # compute number of days as quarters
        temp = []
        for day in day_hours:
            day_total_value = day_total[day]
            day_hours_value = day_hours[day]
            if day_total[day]:
                a = float_utils.round(ROUNDING_FACTOR * day_hours_value / day_total_value) / ROUNDING_FACTOR
            else:
                a = 0.0
            temp.append(a)
        days = sum(temp)
        # add additional day we_additional
        return {
            'days': days + we_additional,
            'hours': sum(day_hours.values()),
        }
