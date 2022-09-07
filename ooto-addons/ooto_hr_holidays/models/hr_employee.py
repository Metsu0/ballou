# -*- coding: utf-8 -*-

from pytz import utc

from odoo import models


def timezone_datetime(time):
    if not time.tzinfo:
        time = time.replace(tzinfo=utc)
    return time


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def _get_leave_days_data(self, from_datetime, to_datetime, calendar=None, domain=None, is_payslip=False):
        """
            By default the resource calendar is used, but it can be
            changed using the `calendar` argument.

            `domain` is used in order to recognise the leaves to take,
            None means default value ('time_type', '=', 'leave')

            Returns a dict {'days': n, 'hours': h} containing the number of leaves
            expressed as days and as hours.

            ==*==
            Override native function to add context when calling _get_days_data
            ==*==
        """
        resource = self.resource_id
        calendar = calendar or self.resource_calendar_id

        # naive datetimes are made explicit in UTC
        from_datetime = timezone_datetime(from_datetime)
        to_datetime = timezone_datetime(to_datetime)

        day_total = calendar._get_day_total(from_datetime, to_datetime, resource)

        # compute actual hours per day
        attendances = calendar._attendance_intervals(from_datetime, to_datetime, resource)
        if is_payslip:
            leave_ids = calendar._leave_intervals(from_datetime, to_datetime, resource, domain, is_payslip=is_payslip)
            return leave_ids
        else:
            leaves = calendar._leave_intervals(from_datetime, to_datetime, resource, domain)
            # add context employee_id
            return calendar.with_context(employee_id=self, leaves=leaves)._get_days_data(attendances & leaves,
                                                                                         day_total)

    def _get_work_days_data(self, from_datetime, to_datetime, compute_leaves=True, calendar=None, domain=None):
        """
            By default the resource calendar is used, but it can be
            changed using the `calendar` argument.

            `domain` is used in order to recognise the leaves to take,
            None means default value ('time_type', '=', 'leave')

            Returns a dict {'days': n, 'hours': h} containing the
            quantity of working time expressed as days and as hours.
        """
        resource = self.resource_id
        calendar = calendar or self.resource_calendar_id

        # naive datetimes are made explicit in UTC
        from_datetime = timezone_datetime(from_datetime)
        to_datetime = timezone_datetime(to_datetime)

        day_total = calendar._get_day_total(from_datetime, to_datetime, resource)

        # actual hours per day
        if compute_leaves:
            intervals = calendar._work_intervals(from_datetime, to_datetime, resource, domain)
        else:
            intervals = calendar._attendance_intervals(from_datetime, to_datetime, resource)

        return calendar.with_context(employee_id=self, from_leave=True)._get_days_data(intervals, day_total)
