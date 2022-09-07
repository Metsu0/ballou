# coding: utf-8

import math
from datetime import datetime, date, timedelta
from locale import Error
from dateutil.relativedelta import MO, relativedelta
import calendar
from odoo.exceptions import UserError

from odoo import models, fields, api, _


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    leave_allocation_current_year = fields.Float(readonly=True,
                                                 string='Leave allocation for the current year',
                                                 compute='_compute_leave_allocation_current_year')
    leave_allocation_previous_year = fields.Float(readonly=True,
                                                  string='Leave allocation for the previous year',
                                                  compute='_compute_leave_allocation_previous_year')
    hourly_rate_productif = fields.Float(
        string="Hourly rate productif", compute='_compute_hourly_rate')
    hourly_rate_non_productif = fields.Float(
        string="Hourly rate non productif", compute='_compute_hourly_rate')

    def _get_base_local_dict(self):
        return {
            **super(HrPayslip, self)._get_base_local_dict(),

            'date': date,
            'datetime': datetime,
            'relativedelta': relativedelta,
        }

    @api.model
    def get_number_of_days(self):
        if self.date_from and self.date_to:
            diff_days = (self.date_to - self.date_from).days + 1
            if self.date_from.month == self.date_to.month:
                month_range = calendar.monthrange(
                    self.date_from.year, self.date_from.month)[1]
                days_max_value = 31 if month_range == 31 else 30
                diff_days = diff_days if diff_days != month_range else days_max_value
            return diff_days
        return False

    @api.model
    def create(self, vals):
        rec_ids = super(HrPayslip, self).create(vals)
        for rec in rec_ids:
            worked_line = rec.env['hr.payslip.worked_days'].search([('id', 'in', rec.worked_days_line_ids.mapped(
                'id')), ('code', '=', 'NBR_JOURS_TRAVAILLES')], order='id desc')
            if worked_line:
                to_delete = worked_line - worked_line[0]
                to_delete.unlink()

        return rec_ids

    def write(self, vals):
        is_success = super(HrPayslip, self).write(vals)
        for rec in self:
            worked_line = rec.env['hr.payslip.worked_days'].search([('id', 'in', rec.worked_days_line_ids.mapped(
                'id')), ('code', '=', 'NBR_JOURS_TRAVAILLES')], order='id desc')
            if worked_line:
                to_delete = worked_line - worked_line[0]
                to_delete.unlink()

        return is_success

    @api.onchange('date_from', 'date_to', 'employee_id')
    def _onchange_employee(self):
        super(HrPayslip, self)._onchange_employee()
        if self.worked_days_line_ids:
            for worked_days_line in self.worked_days_line_ids:
                if (worked_days_line.work_entry_type_id and not worked_days_line.work_entry_type_id.applied_in_payslip) or (worked_days_line.work_entry_type_id and worked_days_line.work_entry_type_id.code == 'NBR_JOURS_TRAVAILLES'):
                    self.worked_days_line_ids = [
                        (3, worked_days_line.id, False)]
        if self._origin.id or self.id:
            hr_payslip_worked_days_id = self.env['hr.payslip.worked_days'].sudo().create(
                self._get_worked_day_number())
        else:
            hr_payslip_worked_days_id = self.env['hr.payslip.worked_days'].sudo().new(
                self._get_worked_day_number())

        self.worked_days_line_ids = [(4, (hr_payslip_worked_days_id.id))]

    def _get_worked_day_number(self):
        number_of_days = self.get_number_of_days()
        number_of_days = number_of_days if number_of_days else 0
        is_days_max_values = number_of_days == calendar.monthrange(
            self.date_from.year, self.date_from.month)[1]
        basic_salary = self.line_ids.filtered(
            lambda line: line.salary_rule_id.code == 'BASIC')
        basic_salary_amount = basic_salary.amount if basic_salary else 0
        return {
            'name': _('Worked days number'),
            'payslip_id': self.id or self._origin.id,
            'number_of_days': number_of_days,
            'number_of_hours': 173.33 if is_days_max_values else round((173.33 * number_of_days), 2) / 30,
            'work_entry_type_id': self.env.ref('ballou_hr_payroll.hr_work_entry_type_worked_days').id,
            'code': 'NBR_JOURS_TRAVAILLES',
            'is_paid': True,
            'amount': (basic_salary_amount / 30) * number_of_days,
        }

    @api.depends('employee_id', 'date_from', 'date_to')
    @api.onchange('employee_id', 'date_from', 'date_to')
    def _compute_leave_allocation_previous_year(self):
        for payslip in self:
            if payslip.date_from:
                payslip.leave_allocation_previous_year = payslip.get_leave_allocation_number_of_days(
                    payslip.date_from.year)
            else:
                payslip.leave_allocation_previous_year = 0

    @api.depends('employee_id', 'date_from', 'date_to')
    @api.onchange('employee_id', 'date_from', 'date_to')
    def _compute_leave_allocation_current_year(self):
        for payslip in self:
            if payslip.date_from:
                payslip.leave_allocation_current_year = payslip.get_leave_allocation_number_of_days(
                    payslip.date_from.year + 1)
            else:
                payslip.leave_allocation_current_year = 0

    @api.model
    def format_currency(self, amount):
        currency = "{:,}".format(round(amount))
        return currency.replace(',', ' ')

    @api.model
    def get_leave_allocation_number_of_days(self, year):
        leave_allocations = self.env['hr.leave.allocation'].sudo().search([('state', '=', 'validate'),
                                                                           ('employee_id.id', '=',
                                                                            self.employee_id.id),
                                                                           ('holiday_status_id.unpaid',
                                                                            '=', False),
                                                                           ('holiday_status_id.validity_start', '>=', date(
                                                                               year, 1, 1)),
                                                                           ('holiday_status_id.validity_stop', '<=', date(year, 12, 31))])
        if not leave_allocations:
            return 0
        leave_allocations_count = sum([leave_allocation.number_of_days - leave_allocation.leaves_taken for leave_allocation in leave_allocations]
                                      ) if len(leave_allocations) > 0 else leave_allocations.leaves_taken

        # décrémente leave allocation
        payslip_month = self.date_from.month
        number_per_interval = leave_allocations[0].number_per_interval if len(
            leave_allocations) > 0 else leave_allocations.number_per_interval
        while year == self.date_from.year + 1 and payslip_month < date.today().month:
            leave_allocations_count -= number_per_interval
            payslip_month += 1

        if self.date_from.year == year:
            leaves = self.env['hr.leave'].sudo().search([('state', '=', 'validate'), ('employee_id.id', '=', self.employee_id.id),
                                                         ('request_date_from', '<=', date(
                                                             self.date_from.year, 12, 31)),
                                                         ('request_date_from', '>', self.date_to)])
            leave_allocations_count += sum(
                [leave.number_of_days for leave in leaves])

        if self.date_from.year + 1 == year:
            if self.date_from.month < date.today().month and leave_allocations_count < self.date_from.month * number_per_interval:
                leave_allocations_count += number_per_interval
                leave_allocations_count = leave_allocations_count if leave_allocations_count > 0 else 0
        return leave_allocations_count

    def get_amount_by_code(self, code):
        """
        Get line amount by code
        :param code:
        :return:
        """
        total_amount = 0
        for rec in self:
            line_ids = rec.line_ids.filtered(lambda l: l.code == code)
            total_amount += sum(line_ids.mapped('total')) if line_ids else 0
        return total_amount

    def _get_worked_day_lines_values(self, domain=None):
        """
            Override work entry number of days for maternity absence
        :param domain:
        :return:
        """
        self.ensure_one()
        res = super(HrPayslip, self)._get_worked_day_lines_values(domain)

        for work_day_line_id in res:
            work_entry_type = self.env['hr.work.entry.type'].browse(
                work_day_line_id.get('work_entry_type_id'))

            # Calculation of maternity leave
            maternity_leave_ids = self.env['hr.leave'].search([
                ('employee_id', '=', self.employee_id.id),
                ('state', '=', 'validate'),
                ('date_from', '<=', self.date_to),
                ('date_to', '>=', self.date_from),
                ('holiday_status_id.weekend_consideration', '=', True)
            ])
            maternity_day = 0

            if maternity_leave_ids and work_entry_type == maternity_leave_ids.mapped(
                    'holiday_status_id').work_entry_type_id:
                for leave in maternity_leave_ids:
                    l_date_from = self.date_from if leave[0].date_from.date() < self.date_from else leave[
                        0].date_from.date()
                    l_date_to = self.date_to if leave[0].date_to.date(
                    ) > self.date_to else leave[0].date_to.date()
                    maternity_day += (l_date_to - l_date_from).days + 1

                # Update number_of_days and number_of_hours for work_entry maternity_line
                work_day_line_id.update({'number_of_days': maternity_day,
                                         'number_of_hours': maternity_day * 8
                                         })
        return res

    def check_maternity_absence_one_month(self, payslip_id):
        """
        Check maternity absence days one month
        :param payslip_id:
        :return:
        """
        day_dt_from = datetime.combine(
            payslip_id.date_from, datetime.min.time())
        day_dt_to = datetime.combine(payslip_id.date_to, datetime.max.time())
        abs_names = self.env['hr.leave.type'].search([('weekend_consideration', '=', True)]).mapped(
            'work_entry_type_id').mapped('name')
        nb_days = 0
        if payslip_id.worked_days_line_ids:
            nb_days = sum(
                payslip_id.worked_days_line_ids.filtered(lambda w: w.name in abs_names).mapped('number_of_days'))
        is_one_month = True if day_dt_from.day == 1 and day_dt_to.day == nb_days else False
        return is_one_month

    def get_maternity_absence(self, payslip_id):
        """
        Get maternity absence days
        :param payslip_id:
        :return:
        """
        abs_names = self.env['hr.leave.type'].search([('weekend_consideration', '=', True)]).mapped(
            'work_entry_type_id').mapped('name')
        nb_days = 0
        if payslip_id.worked_days_line_ids:
            nb_days = sum(
                payslip_id.worked_days_line_ids.filtered(lambda w: w.name in abs_names).mapped('number_of_days'))
        return nb_days

    def get_employees_dependent_age(self, emp, date_from):
        dt_from = datetime.strptime(str(date_from), "%Y-%m-%d")
        dependent_count = 0
        for dependent_id in emp.dependent_ids:
            birthdate = dependent_id.birthdate
            dt_birthdate = datetime.strptime(str(birthdate), "%Y-%m-%d")
            diff = relativedelta(date_from, birthdate)
            years = int(diff.years)
            if years <= 20 and dt_from.month != dt_birthdate.month or years < 20 and dt_from.month == dt_birthdate.month or dependent_id.is_handicap:
                dependent_count += 1
        return dependent_count

    @api.model
    def get_month_name(self, month):
        if month not in range(14):
            raise UserError(
                _("The month is not valid")
            )
        MONTHS = [
            "Janvier", "Février", "Mars",
            "Avril", "Mai", "Juin",
            "Juillet", "Août", "Septembre",
            "Octobre", "Novembre", "Decembre"
        ]
        return MONTHS[month-1]

    @api.model
    def get_decimal(self, x):
        print('*'*2)
        print(x)
        return math.floor(x)

    def _compute_hourly_rate(self):
        for slip in self:
            if slip.state == 'done':
                if slip.employee_id.internal_classification:
                    if (slip.employee_id.internal_classification.name or "").lower() == "productif":
                        slip.hourly_rate_productif = slip._get_salary_line_total(
                            "TH") + slip._get_salary_line_total("TH_SANS_OSTIE")
                    elif (slip.employee_id.internal_classification.name or "").lower() == "non productif":
                        slip.hourly_rate_non_productif = slip._get_salary_line_total(
                            "TH") + slip._get_salary_line_total("TH_SANS_OSTIE")
                elif slip.employee_id.category_ids:
                    if "Productif" in slip.employee_id.category_ids.mapped("name") or "PRODUCTIF" in slip.employee_id.category_ids.mapped("name"):
                        slip.hourly_rate_productif = slip._get_salary_line_total(
                            "TH") + slip._get_salary_line_total("TH_SANS_OSTIE")
                    elif "Non Productif" in slip.employee_id.category_ids.mapped("name") or "NON PRODUCTIF" in slip.employee_id.category_ids.mapped("name"):
                        slip.hourly_rate_non_productif = slip._get_salary_line_total(
                            "TH") + slip._get_salary_line_total("TH_SANS_OSTIE")


# class HrPayslipInput(models.Model):
#     _inherit = 'hr.payslip.input'

#     custom_code = fields.Char(related='input_type_id.code', store=True, help="The code that can be used in the salary rules")

#     @api.depends('input_type_id')
#     def _compute_custom_code(self):
#         for rec in self :
#             self._cr.execute("""
#             UPDATE hr_payslip_input SET custom_code = %s WHERE id = %s
#             """ % (rec.input_type_id.code, rec.id))

class HrPayslipWorkedDays(models.Model):
    _inherit = 'hr.payslip.worked_days'

    work_entry_type_id = fields.Many2one(required=False)
    is_paid = fields.Boolean(compute=False)
