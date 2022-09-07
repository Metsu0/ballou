# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import timedelta
import math

class HrLeave(models.Model):
    _inherit = 'hr.leave'

    def _get_number_of_days(self, date_from, date_to, employee_id):
        """
            If weekend_consideration return all total days
        :param date_from:
        :param date_to:
        :param employee_id:
        :return: days, hours
        """
        if employee_id:
            if self.holiday_status_id.weekend_consideration:
                if self.request_unit_half:
                    return {'days': 0.5, 'hours': 4}
                else:
                    days = (self.date_to.date() - self.date_from.date()).days + 1
                    hours = round((self.date_to - self.date_from).seconds / 60 / 60, 2) if days == 1 else round(((self.date_to - self.date_from).seconds / 60 / 60) / 8, 2)
                    print()
                    return {
                        'days': days,
                        'hours': hours
                    }
        print()
        return super(HrLeave, self)._get_number_of_days(date_from, date_to, employee_id)

   
    def _get_date_reprise(self, date_to):
        """
            Get the reprise date to put in report
            :param date_to:
            :return datetime:
        """
        return (self.date_to + timedelta(days=1)).strftime("%d/%m/%Y")

    @api.model
    def format_leave(self, x):
        return math.floor(x*10)/10