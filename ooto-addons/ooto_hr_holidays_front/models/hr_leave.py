# -*- coding: utf-8 -*-
from datetime import datetime, time
from odoo import models, fields, api
from odoo.addons.resource.models.resource import float_to_time, HOURS_PER_DAY
from datetime import datetime, date, timedelta
from dateutil import relativedelta
import calendar


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    approve_date = fields.Date("Approve date")
    approve_date_first = fields.Date("Approve date first")
    cancel_date = fields.Date("Cancel date")
    refuse_date = fields.Date("Refuse date")
    justificatory = fields.Binary("Justificatory")
    justificatory_filename = fields.Char("Filename")
    cancel_approver_id = fields.Many2one("hr.employee", "Cancel approver")
    via_fo = fields.Boolean(string="Via fo")

    @api.onchange('date_from', 'date_to', 'employee_id', 'holiday_status_id')
    def _onchange_leave_dates(self):
        if self.date_from and self.date_to:
            self.number_of_days = self._get_number_of_days(self.date_from, self.date_to, self.employee_id.id)['days']
        else:
            self.number_of_days = 0

    def return_leave_count(self, leave_float):
        if leave_float - int(leave_float) == 0:
            return int(leave_float)
        else:
            return leave_float

    def activity_update(self, send_now=False):
        if send_now:
            to_clean, to_do = self.env['hr.leave'], self.env['hr.leave']
            for holiday in self:
                if holiday.state == 'draft':
                    to_clean |= holiday
                elif holiday.state == 'confirm':
                    holiday.activity_schedule(
                        'hr_holidays.mail_act_leave_approval',
                        user_id=holiday.sudo()._get_responsible_for_approval().id)
                elif holiday.state == 'validate1':
                    holiday.activity_feedback(['hr_holidays.mail_act_leave_approval'])
                    holiday.activity_schedule(
                        'hr_holidays.mail_act_leave_second_approval',
                        user_id=holiday.sudo()._get_responsible_for_approval().id)
                elif holiday.state == 'validate':
                    to_do |= holiday
                elif holiday.state == 'refuse':
                    to_clean |= holiday
            if to_clean:
                to_clean.activity_unlink(
                    ['hr_holidays.mail_act_leave_approval', 'hr_holidays.mail_act_leave_second_approval'])
            if to_do:
                to_do.activity_feedback(
                    ['hr_holidays.mail_act_leave_approval', 'hr_holidays.mail_act_leave_second_approval'])
        else:
            pass

    # def write(self, values):
    # 	if values.get('state', False) == 'validate1':
    # 		values.update({'approve_date_first': datetime.now()})
    # 	if values.get('state', False) == 'validate':
    # 		values.update({'approve_date': datetime.now()})
    # 	if values.get('state', False) == 'refuse':
    # 		values.update({'refuse_date': datetime.now()})
    # 	return super(HrLeave, self).write(values)

    def write(self, values):
        if values.get('state', False) == 'validate1':
            values.update({'approve_date_first': datetime.now()})
        if values.get('state', False) == 'validate':
            values.update({'approve_date': datetime.now()})
        if values.get('state', False) == 'refuse':
            values.update({'refuse_date': datetime.now()})

        employee_id = values.get('employee_id', False)
        if not self.env.context.get('leave_fast_create'):
            if values.get('state'):
                self._check_approval_update(values['state'])
                if any(holiday.validation_type == 'both' for holiday in self):
                    if values.get('employee_id'):
                        employees = self.env['hr.employee'].browse(values.get('employee_id'))
                    else:
                        employees = self.mapped('employee_id')
                    self._check_double_validation_rules(employees, values['state'])
            if 'date_from' in values:
                values['request_date_from'] = values['date_from']
            if 'date_to' in values:
                values['request_date_to'] = values['date_to']

        if not self.env.context.get('leave_fast_create'):
            for holiday in self:
                if employee_id:
                    holiday.add_follower(employee_id)
                    self._sync_employee_details()
                if 'number_of_days' not in values and ('date_from' in values or 'date_to' in values):
                    holiday._onchange_leave_dates()
        # Overwrite native behavior checking group hr_holidays.group_hr_holidays_user member
        result = models.Model.write(self, values)
        return result

    @api.model
    def get_leave_data(self, user):
        user = self.env['res.users'].browse(user)
        current_year = datetime.now().year
        employees = self.env['hr.employee'].sudo().search([('user_id', '=', user.id)])
        domain = [('employee_id', '=', employees.id), ('state', '=', 'validate'),
                  ('holiday_status_id.unpaid', '=', False), ('holiday_status_id.allocation_type', '!=', 'no')]
        l_leave_requests = self.env['hr.leave'].sudo().search(domain).filtered(
            lambda a: a.date_from and datetime.strptime(str(a.date_from.date()),
                                                        '%Y-%m-%d').date().year == current_year - 1)
        l_allocs = self.env['hr.leave.allocation'].sudo().search(domain).filtered(
            lambda a: a.create_date and datetime.strptime(str(a.create_date.date()),
                                                          '%Y-%m-%d').date().year == current_year - 1)
        c_leave_requests = self.env['hr.leave'].sudo().search(
            [('employee_id', '=', employees.id), ('holiday_status_id.unpaid', '=', False),
             ('state', 'not in', ['refuse', 'cancel']), ('holiday_status_id.allocation_type', '!=', 'no')]).filtered(
            lambda a: a.date_from and datetime.strptime(str(a.date_from.date()),
                                                        '%Y-%m-%d').date().year == current_year)
        c_allocs = self.env['hr.leave.allocation'].sudo().search(domain).filtered(
            lambda a: a.create_date and datetime.strptime(str(a.create_date.date()),
                                                          '%Y-%m-%d').date().year == current_year)
        total_allocs = self.env['hr.leave.allocation'].sudo().search(domain)
        total_leave_request = self.env['hr.leave'].sudo().search(
            [('employee_id', '=', employees.id), ('holiday_status_id.unpaid', '=', False),
             ('state', 'not in', ['refuse', 'cancel']), ('holiday_status_id.allocation_type', '!=', 'no')]).filtered(
            lambda a: a.date_from and datetime.strptime(str(a.date_from.date()),
                                                        '%Y-%m-%d').date().year <= current_year)

        return {
            'last_all_leave': self.return_leave_count(round(sum(l_allocs.mapped('number_of_days')), 2)),
            'last_leave_allocation': self.return_leave_count(round(sum(l_allocs.mapped('number_of_days')), 2)),
            'last_leave_request': self.return_leave_count(
                abs(round(sum(l_leave_requests.mapped('number_of_days')), 2))),
            'current_all_leave': self.return_leave_count(round(sum(c_leave_requests.mapped('number_of_days')), 2)),
            'current_leave_allocation': self.return_leave_count(round(sum(c_allocs.mapped('number_of_days')), 2)),
            'current_leave_request': self.return_leave_count(
                abs(round(sum(c_leave_requests.mapped('number_of_days')), 2))),
            'number_of_days': self.return_leave_count(round(sum(c_allocs.mapped('number_of_days')), 2)),
            'total_rest_leave': self.return_leave_count(round(
                (sum(total_allocs.mapped('number_of_days')) - sum(total_leave_request.mapped('number_of_days'))), 2))
        }

    @api.model
    def add_attachment(self, res_id, file, filename):

        """ add attachment """
        attach_obj = self.env['ir.attachment']
        attach_obj_id = self.env['ir.attachment'].search([('res_id', '=', res_id), ('res_model', '=', 'hr.leave')])
        if attach_obj_id:
            attach_obj_id.write({
                'datas': file,
                'name': filename,
                # 'datas_fname': filename,
                'store_fname': filename,
            })
        else:
            attach_obj.create({
                'type': 'binary',
                'res_model': 'hr.leave',
                'res_id': res_id,
                'datas': file,
                'name': filename,
                # 'datas_fname': filename,
                'store_fname': filename,
            })
        return True

    def _get_number_of_days(self, date_from, date_to, employee_id):
        """ Returns a float equals to the timedelta between two dates given as string."""
        if employee_id:
            employee = self.env['hr.employee'].browse(employee_id)
            for i in [1, 2]:
                if date_to.weekday() == 4 + i and date_from.weekday() <= 4:
                    date_to -= timedelta(days=i)
            return employee._get_work_days_data(date_from, date_to)

        today_hours = self.env.company.resource_calendar_id.get_work_hours_count(
            datetime.combine(date_from.date(), time.min),
            datetime.combine(date_from.date(), time.max),
            False)

        hours = self.env.company.resource_calendar_id.get_work_hours_count(date_from, date_to)

        return {'days': hours / (today_hours or HOURS_PER_DAY), 'hours': hours}
