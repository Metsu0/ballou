# -*- coding: utf-8 -*-

from odoo import _, models, fields, api
from odoo.http import request
import datetime


class HrDashboard(models.Model):
    _name = 'hr.dashboard'
    _description = 'HR Dashboard'

    name = fields.Char("")

    @api.model
    def get_onboarding_info(self):
        dashboard = dict()
        period_data_value = list()
        period_data_label = [
            _('Before arrival'),
            _('Arrival day'),
            _('First week'),
            _('First month'),
            _('After first month')
        ]
        task_ids = self.env['hr.onboarding'].sudo().search([]).mapped('task_ids')
        task_late = task_ids.filtered(lambda t: t.task_state == 'late')
        arrival_curr_month = self.env['hr.employee'].sudo().search([]).filtered(
            lambda e: e.hiring_date and e.hiring_date.month == datetime.datetime.now().month)
        leaving_curr_month = self.env['hr.employee'].sudo().search([]).filtered(
            lambda e: e.departure_date and e.departure_date.month == datetime.datetime.now().month)
        published_advice = self.env['hr.onboarding.task'].search(
            [('task_state', 'not in', ['draft', 'unpublished']), ('task_type', '=', 'advice'), '|',
             ('parent_id', '=', False), ('is_from_onboarding', '=', True)])
        if len(task_ids) > 0:
            period_data_value.append(
                len(task_ids.filtered(lambda t: t.period == 'before_arrival')) * 100 / len(task_ids))
            period_data_value.append(len(task_ids.filtered(lambda t: t.period == 'arrival_day')) * 100 / len(task_ids))
            period_data_value.append(len(task_ids.filtered(lambda t: t.period == 'first_week')) * 100 / len(task_ids))
            period_data_value.append(len(task_ids.filtered(lambda t: t.period == 'first_month')) * 100 / len(task_ids))
            period_data_value.append(
                len(task_ids.filtered(lambda t: t.period == 'after_first_month')) * 100 / len(task_ids))
            period_data_value = [round(elem, 2) for elem in period_data_value]
        else:
            period_data_value = [0, 0, 0, 0, 0]
        conn_before_arrival = self.env['hr.employee'].search([('period', '=', 'before_arrival')]).filtered(
            lambda e: e.user_id and e.user_id.state == 'active')
        all_emp_with_user = self.env['hr.employee'].search([('user_id', '!=', False), ('hiring_date', '!=', False)])
        if len(all_emp_with_user) > 0:
            conn_bef = round(len(conn_before_arrival) * 100 / len(all_emp_with_user), 2)
        else:
            conn_bef = 0
        finished_in_time = task_ids.filtered(lambda t: t.finished_in_time)
        task_data_label = [_('Task late'), _('Task finished on time')]
        if len(task_ids) > 0:
            task_data_value = [len(task_late) * 100 / len(task_ids), len(finished_in_time) * 100 / len(task_ids)]
            task_data_value = [round(elem, 2) for elem in task_data_value]
        else:
            task_data_value = [0]
        dashboard.update({
            'task_late': len(task_late),
            'arrival_curr_month': len(arrival_curr_month),
            'leaving_curr_month': len(leaving_curr_month),
            'published_advice': len(published_advice),
            'period_data_value': period_data_value,
            'period_data_label': period_data_label,
            'conn_bef': conn_bef,
            'task_data_value': task_data_value,
            'task_data_label': task_data_label,
            'finished_in_time': len(finished_in_time),
        })
        return dashboard
