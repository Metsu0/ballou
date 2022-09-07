# -*- coding:utf-8 -*-

from collections import defaultdict
from datetime import datetime, date

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.addons.hr_work_entry_holidays.models.hr_leave import HrLeave as HrLeaveWorkEntry


class HrLeave(HrLeaveWorkEntry):
    _inherit = 'hr.leave'

    def _get_number_of_days(self, date_from, date_to, employee_id):
        """ If an employee is currently working full time but requests a leave next month
            where he has a new contract working only 3 days/week. This should be taken into
            account when computing the number of days for the leave (2 weeks leave = 6 days).
            Override this method to get number of days according to the contract's calendar
            at the time of the leave.
        """
        days = super(HrLeaveWorkEntry, self)._get_number_of_days(date_from, date_to, employee_id)
        if employee_id and not self.holiday_status_id.weekend_consideration:
            employee = self.env['hr.employee'].browse(employee_id)
            # Use sudo otherwise base users can't compute number of days
            contracts = employee.sudo()._get_contracts(date_from, date_to, states=['open'])
            contracts |= employee.sudo()._get_incoming_contracts(date_from, date_to)
            calendar = contracts[
                       :1].resource_calendar_id if contracts else None  # Note: if len(contracts)>1, the leave creation will crash because of unicity constaint
            return employee._get_work_days_data_batch(date_from, date_to, calendar=calendar)[employee.id]

        return days
