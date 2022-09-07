# -*- coding: utf-8 -*-
import base64
import json
from odoo import http
from datetime import datetime, time, timedelta
import dateutil.parser
from odoo.tools import float_compare
from pytz import timezone, UTC
from odoo.addons.resource.models.resource import float_to_time, HOURS_PER_DAY
from odoo import tools, _, SUPERUSER_ID
from odoo.exceptions import ValidationError
from odoo.http import request, route
from odoo.addons.website.controllers.main import QueryURL
# from odoo.addons.aw12_ouvrant_droit_front.controllers.portal import CustomerPortalOD
from odoo.addons.portal_leave.controllers.main import CustomerPortal as CustomerPortalLeave
from odoo.addons.portal.controllers.portal import get_records_pager, pager as portal_pager, CustomerPortal
from odoo.addons.ooto_hr_account.controllers.controllers import CustomerPortal as OotoCustomerPortal

import logging

_logger = logging.getLogger(__name__)


#
# class CustomerPortalHrHolidays(CustomerPortalOD):
#
# 	@route(['/my/account'], type='http', auth='user', website=True)
# 	def account(self, redirect=None, **post):
# 		res = super(CustomerPortalHrHolidays, self).account(redirect, **post)
# 		user = request.env.user
# 		leave_data = request.env['hr.leave'].browse(1).get_leave_data(user.id)
# 		res.qcontext.update(leave_data)
# 		return res


class CustomerPortal(CustomerPortalLeave):

    @http.route(['/params/justificatory'], type="json", auth="none")
    def _get_justificatory_size(self):
        size = request.env['ir.config_parameter'].sudo().get_param('ooto_hr_holidays_front._get_justificatory_size', '')
        return {'size': size if size else 8}

    @http.route(['/create/new/leave'], type='http', auth="user", website=True)
    def create_new_leave_1(self, page=1, sortby=None, search=None, search_in='content', **kw):
        user = request.env.user
        values = request.env['hr.leave'].browse(1).get_leave_data(user.id)
        employee_id = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)])
        hide_home = request.env['ir.config_parameter'].sudo().get_param('ooto_hr_account.hide_home')
        values.update({
            'leave_types': request.env['hr.leave.type'].sudo().search([('company_id', '=', employee_id.company_id.id)]),
            'hide_home': hide_home
        })
        return request.render("ooto_hr_holidays_front.registration_leave", values)

    @http.route(['/my/leaves', '/my/leaves/page/<int:page>'], type='http', auth="user", website=True)
    def my_helpdesk_leaves(self, page=1, sortby=None, search=None, search_in='content', filter=None, **kw):
        values = self._prepare_portal_layout_values()
        user = request.env.user
        employees = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)])
        for employee in employees:
            # domain = [('employee_id', '=', employee.id), ('state', '!=', 'draft')]
            domain = [('employee_id', '=', employee.id)]

            # pager
            leaves_count = request.env['hr.leave'].sudo().search_count(domain)
            pager = portal_pager(
                url="/my/leaves",
                total=leaves_count,
                page=page,
                step=8,
                url_args={'filter': filter, 'search': search},
            )

            leaves = request.env['hr.leave'].sudo().search(domain, limit=8, offset=pager['offset'])
            if search:
                search_date = False
                try:
                    search_1 = datetime.strptime(search, "%d/%m/%Y")
                    if search_1:
                        search = search.replace('/', '-')
                except Exception:
                    pass
                try:
                    search_date = datetime.strptime(search, "%d-%m-%Y")
                except Exception:
                    pass
                leaves = leaves.filtered(lambda l: l.name and l.name.find(
                    search) != -1 or (search_date and datetime.strptime(
                    l.request_date_from.strftime('%d-%m-%Y'), "%d-%m-%Y") <= search_date <= datetime.strptime(
                    l.request_date_to.strftime('%d-%m-%Y'), "%d-%m-%Y"))).sorted(
                    lambda l: l.request_date_from)
            filters = [
                ('none', _('Filter by')),
                ('approve', _('To Approve')),
                ('validated', _('Approved Leaves')),
                ('cancel', _('Cancelled')),
                ('refuse', _('Refused')),
                # ('active_types', _('Active Types')),
                # ('message_needaction', _('Unread Messages')),
                # ('department', _('My Department Leaves')),
                # ('my_team_leaves', _('My Team Leaves')),
                # ('to_do', _('To Do')),
                # ('year', _('Current Year')),
                # ('my_leaves', _('My Leaves')),
                # ('activities_overdue', _('Late Activities')),
                # ('activities_today', _('Today Activities')),
                # ('activities_upcoming_all', _('Future Activities'))
            ]
            if filter and filter == 'approve':
                leaves = leaves.filtered(lambda l: l.state in ['confirm', 'validate1'])
            if filter and filter == 'validated':
                leaves = leaves.filtered(lambda l: l.state == 'validate')
            if filter and filter == 'cancel':
                leaves = leaves.filtered(lambda l: l.state == 'cancel')
            if filter and filter == 'refuse':
                leaves = leaves.filtered(lambda l: l.state == 'refuse')
            if filter and filter == 'active_types':
                leaves = leaves.filtered(lambda l: l.holiday_status_id.active)
            if filter and filter == 'message_needaction':
                leaves = leaves.filtered(lambda l: l.message_needaction)
            if filter and filter == 'department':
                leaves = leaves.filtered(lambda l: l.department_id.member_ids.user_id.id == request.session.uid)
            if filter and filter == 'my_team_leaves':
                leaves = leaves.filtered(lambda l: l.employee_id.parent_id.user_id.id == request.session.uid)
            if filter and filter == 'to_do':
                leaves = leaves.filtered(lambda l: not l.payslip_status)
            if filter and filter == 'year':
                leaves = leaves.filtered(lambda l: l.holiday_status_id.active)
            if filter and filter == 'my_leaves':
                leaves = leaves.filtered(lambda l: l.employee_id.user_id.id == request.session.uid)
            dict_filter = dict((x, y) for x, y in filters)
            request.session['my_leaves_history'] = leaves.ids[:100]
            keep = QueryURL('/my/leaves')
            values.update({
                'leaves': leaves,
                'filters': filters,
                'search': search if search else False,
                'current_filter': dict_filter[filter] if filter else False,
                'keep': keep,
                'page_name': 'leave',
                'default_url': '/my/leaves',
                'pager': pager,
            })
            return request.render("portal_leave.portal_my_leaves", values)

    @http.route(['/leave/register'], type='http', auth="user", website=True)
    def create_new_leave_request(self, page=1, sortby=None, search=None, search_in='content', **kw):
        user = request.env.user
        from_date = ''
        to_date = ''
        header = {
            'Content-Type': 'text/html; charset=utf-8',
            'Access-Control-Allow-Methods': 'POST , OPTIONS',
        }
        if kw.get('request_date_from'):
            from_date = dateutil.parser.parse(kw.get('request_date_from')).date()
            if not kw.get('request_date_to') and not kw.get('halfday'):
                kw.update({'request_date_to': kw.get('request_date_from')})
        if kw.get('request_date_to'):
            to_date = dateutil.parser.parse(kw.get('request_date_to')).date()
        type_id = request.env['hr.leave.type'].sudo().browse(int(kw['state_id']))

        if type_id.validity_start and type_id.validity_stop:
            if from_date and to_date and (from_date < type_id.validity_start or to_date > type_id.validity_stop):
                response = http.request.make_response(
                    json.dumps({
                        'not_allowed': True
                    }), headers=header)
                return response

        elif type_id.validity_start:
            if from_date and (from_date < type_id.validity_start):
                response = http.request.make_response(
                    json.dumps({
                        'not_allowed': True
                    }), headers=header)
                return response

        elif type_id.validity_stop:
            if to_date and (to_date > type_id.validity_stop):
                response = http.request.make_response(
                    json.dumps({
                        'not_allowed': True
                    }), headers=header)
                return response

        employees = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)
        for employee in employees:
            period = ''
            if type_id.is_exceptional_permission:
                from_date_time = datetime.combine(from_date, datetime.min.time())
                to_date_time = datetime.combine(to_date, datetime.max.time())
                number_of_days = \
                request.env['hr.leave'].sudo()._get_number_of_days(from_date_time, to_date_time, employee.id)[
                    'days']
                res_excep = request.env['hr.leave'].sudo().get_is_exceptional_day_available(True, employee_id=employee,
                                                                                            date_from=from_date,
                                                                                            number_of_days=number_of_days)
                if not res_excep['can_take']:
                    response = http.request.make_response(
                        json.dumps({
                            'exceptional_error': True
                        }), headers=header)
                    return response
            if kw.get('halfday'):
                if kw.get('period') == _('Morning'):
                    period = 'am'
                if kw.get('period') == _('Afternoon'):
                    period = 'pm'

                domain = [('calendar_id', '=',
                           employee.resource_calendar_id.id or request.env.user.company_id.resource_calendar_id.id)]
                attendances = request.env['resource.calendar.attendance'].search(domain,
                                                                                 order='dayofweek, day_period DESC')
                # find first attendance coming after first_day
                attendance_from = next((att for att in attendances if int(att.dayofweek) >= from_date.weekday()),
                                       attendances[0])
                # find last attendance coming before last_day
                attendance_to = next(
                    (att for att in reversed(attendances) if int(att.dayofweek) <= from_date.weekday()),
                    attendances[-1])
                if period == 'am':
                    hour_from = float_to_time(attendance_from.hour_from)
                    hour_to = float_to_time(attendance_from.hour_to)
                else:
                    hour_from = float_to_time(attendance_to.hour_from)
                    hour_to = float_to_time(attendance_to.hour_to)
                tz = request.env.user.tz or 'UTC'  # custom -> already in UTC
                date_from = timezone(tz).localize(datetime.combine(from_date, hour_from)).astimezone(
                    UTC).replace(tzinfo=None)
                date_to = timezone(tz).localize(datetime.combine(from_date, hour_to)).astimezone(UTC).replace(
                    tzinfo=None)

                nholidays = request.env['hr.leave'].sudo().search_count([('request_date_from', '<=', date_to),
                                                                         ('date_to', '>', date_from),
                                                                         ('employee_id', '=', employee.id),
                                                                         ('state', 'not in', ['cancel', 'refuse']),
                                                                         ])
                if nholidays:
                    response = http.request.make_response(
                        json.dumps({
                            'overlaps': True
                        }), headers=header)
                    return response
                if type_id.allocation_type != 'no' and type_id.allow_credit == False:
                    leave_days = type_id.get_days(employee.id)[type_id.id]
                    _logger.info("Leave Days ----------------------------->>>>>>>>>>>>>>>>>")
                    _logger.info(leave_days)
                    if float_compare(leave_days['remaining_leaves'], 0, precision_digits=2) == -1 or \
                            float_compare(leave_days['remaining_leaves'], 0, precision_digits=2) == 0 or \
                            float_compare(leave_days['virtual_remaining_leaves'], 0, precision_digits=2) == 0 or \
                            float_compare(leave_days['virtual_remaining_leaves'], 0, precision_digits=2) == -1:
                        response = http.request.make_response(
                            json.dumps({
                                'sufficient': True
                            }), headers=header)
                        return response

                values = {
                    'employee_id': employee.id,
                    'holiday_status_id': int(kw.get('state_id')),
                    'request_date_from': kw.get('request_date_from'),
                    'request_date_to': kw.get('request_date_to'),
                    'number_of_days': 0.5,
                    'request_date_from_period': period,
                    'request_unit_half': kw.get('halfday'),
                    'name': kw.get('name'),
                }
                _logger.info(values)
                try:
                    leave = request.env['hr.leave'].sudo().create(values)
                except Exception as e:
                    response = http.request.make_response(
                        json.dumps({
                            'overlaps': True
                        }), headers=header)
                    return response
                if not leave.request_date_from:
                    leave.date_from = False
                    return

                if leave.request_unit_half or leave.request_unit_hours:
                    leave.request_date_to = leave.request_date_from

                if not leave.request_date_to:
                    leave.date_to = False
                    return

                domain = [('calendar_id', '=',
                           leave.employee_id.resource_calendar_id.id or request.env.user.company_id.resource_calendar_id.id)]
                attendances = request.env['resource.calendar.attendance'].search(domain,
                                                                                 order='dayofweek, day_period DESC')

                # find first attendance coming after first_day
                attendance_from = next(
                    (att for att in attendances if int(att.dayofweek) >= leave.request_date_from.weekday()),
                    attendances[0])
                # find last attendance coming before last_day
                attendance_to = next(
                    (att for att in reversed(attendances) if int(att.dayofweek) <= leave.request_date_to.weekday()),
                    attendances[-1])

                if leave.request_unit_half:
                    if leave.request_date_from_period == 'am':
                        hour_from = float_to_time(attendance_from.hour_from)
                        hour_to = float_to_time(attendance_from.hour_to)
                    else:
                        hour_from = float_to_time(attendance_to.hour_from)
                        hour_to = float_to_time(attendance_to.hour_to)
                else:
                    hour_from = float_to_time(attendance_from.hour_from)
                    hour_to = float_to_time(attendance_to.hour_to)

                tz = request.env.user.tz if request.env.user.tz and not leave.request_unit_custom else 'UTC'  # custom -> already in UTC
                leave.write({'date_from': timezone(tz).localize(
                    datetime.combine(leave.request_date_from, hour_from)).astimezone(
                    UTC).replace(tzinfo=None), 'date_to': timezone(tz).localize(
                    datetime.combine(leave.request_date_to, hour_to)).astimezone(
                    UTC).replace(tzinfo=None)})
                if leave.date_from and leave.date_to:
                    nb_days_hours = leave._get_number_of_days(leave.date_from, leave.date_to,
                                                              leave.employee_id.id)
                    leave.write({'number_of_days': nb_days_hours['days']})
                else:
                    leave.write({'number_of_days': 0})

                leave.activity_update(send_now=True)

            if not kw.get('halfday'):
                domain = [('calendar_id', '=',
                           employee.resource_calendar_id.id or request.env.user.company_id.resource_calendar_id.id)]
                attendances = request.env['resource.calendar.attendance'].search(domain,
                                                                                 order='dayofweek, day_period DESC')
                # find first attendance coming after first_day
                attendance_from = next((att for att in attendances if int(att.dayofweek) >= from_date.weekday()),
                                       attendances[0])
                # find last attendance coming before last_day
                attendance_to = next((att for att in reversed(attendances) if int(att.dayofweek) <= to_date.weekday()),
                                     attendances[-1])
                hour_from = float_to_time(attendance_from.hour_from)
                hour_to = float_to_time(attendance_to.hour_to)
                tz = request.env.user.tz or 'UTC'
                date_from = timezone(tz).localize(datetime.combine(from_date, hour_from)).astimezone(
                    UTC).replace(tzinfo=None)
                date_to = timezone(tz).localize(datetime.combine(to_date, hour_to)).astimezone(UTC).replace(tzinfo=None)
                nholidays = request.env['hr.leave'].sudo().search_count(
                    [('request_date_from', '<=', date_to),
                     ('date_to', '>', date_from),
                     ('employee_id', '=', employee.id),
                     ('state', 'not in', ['cancel', 'refuse']),
                     ])
                if nholidays:
                    response = http.request.make_response(
                        json.dumps({
                            'overlaps': True
                        }), headers=header)
                    return response

                if type_id.allocation_type != 'no' and type_id.allow_credit == False:
                    leave_days = type_id.get_days(employee.id)[type_id.id]

                    if float_compare(leave_days['remaining_leaves'], 0, precision_digits=2) == -1 or \
                            float_compare(leave_days['remaining_leaves'], 0, precision_digits=2) == 0 or \
                            float_compare(leave_days['virtual_remaining_leaves'], 0, precision_digits=2) == 0 or \
                            float_compare(leave_days['virtual_remaining_leaves'], 0, precision_digits=2) == -1:
                        response = http.request.make_response(
                            json.dumps({
                                'sufficient': True
                            }), headers=header)
                        return response

                values = {
                    'employee_id': employee.id,
                    'holiday_status_id': int(kw.get('state_id')),
                    'request_date_from': kw.get('request_date_from'),
                    'request_date_to': kw.get('request_date_to'),
                    'date_from': kw.get('request_date_from'),
                    'date_to': kw.get('request_date_to'),
                    'name': kw.get('name'),
                }
                leave = request.env['hr.leave'].sudo().create(values)
                if not leave.request_date_from:
                    leave.date_from = False
                    return

                if leave.request_unit_half or leave.request_unit_hours:
                    leave.request_date_to = leave.request_date_from

                if not leave.request_date_to:
                    leave.date_to = False
                    return

                domain = [('calendar_id', '=',
                           leave.employee_id.resource_calendar_id.id or request.env.user.company_id.resource_calendar_id.id)]
                attendances = request.env['resource.calendar.attendance'].search(domain,
                                                                                 order='dayofweek, day_period DESC')

                # find first attendance coming after first_day
                attendance_from = next(
                    (att for att in attendances if int(att.dayofweek) >= leave.request_date_from.weekday()),
                    attendances[0])
                # find last attendance coming before last_day
                attendance_to = next(
                    (att for att in reversed(attendances) if int(att.dayofweek) <= leave.request_date_to.weekday()),
                    attendances[-1])

                if leave.request_unit_half:
                    if leave.request_date_from_period == 'am':
                        hour_from = float_to_time(attendance_from.hour_from)
                        hour_to = float_to_time(attendance_from.hour_to)
                    else:
                        hour_from = float_to_time(attendance_to.hour_from)
                        hour_to = float_to_time(attendance_to.hour_to)
                else:
                    hour_from = float_to_time(attendance_from.hour_from)
                    hour_to = float_to_time(attendance_to.hour_to)

                tz = request.env.user.tz if request.env.user.tz and not leave.request_unit_custom else 'UTC'  # custom -> already in UTC
                leave.write({'date_from': timezone(tz).localize(
                    datetime.combine(leave.request_date_from, hour_from)).astimezone(
                    UTC).replace(tzinfo=None), 'date_to': timezone(tz).localize(
                    datetime.combine(leave.request_date_to, hour_to)).astimezone(
                    UTC).replace(tzinfo=None)})
                if leave.date_from and leave.date_to:
                    try:
                        nb_days_hours = leave._get_number_of_days(leave.date_from, leave.date_to, leave.employee_id.id)
                        # leave.write({'number_of_days': leave._get_number_of_days(leave.date_from, leave.date_to,
                        #                                                          leave.employee_id.id)})
                        leave.write({'number_of_days': nb_days_hours['days']})
                    except Exception as e:
                        if type_id.allow_credit == False:
                            response = http.request.make_response(
                                json.dumps({
                                    'sufficient': True
                                }), headers=header)
                            return response
                else:
                    leave.write({'number_of_days': 0})

                leave.activity_update(send_now=True)
            if kw.get('base64textarea'):
                leave.add_attachment(leave.id, kw.get('base64textarea'), kw.get('name_file'))
                leave.write({
                    'justificatory': kw.get('base64textarea'),
                    'justificatory_filename': kw.get('name_file')
                })
            else:
                leave.write({
                    'justificatory': False,
                    'justificatory_filename': False
                })
        response = http.request.make_response(
            json.dumps({
                'url': "/my/leaves"
            }), headers=header)
        return response

    @http.route(['/leave/editable/<int:leave_id>'], type='http', auth="user", website=True)
    def editable_leave(self, page=1, sortby=None, search=None, search_in='content', **kw):
        user = request.env.user
        values = request.env['hr.leave'].browse(1).get_leave_data(user.id)
        employee_id = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)])
        values.update({
            'leave_types': request.env['hr.leave.type'].sudo().search([('company_id', '=', employee_id.company_id.id)]),
            'leave': request.env['hr.leave'].sudo().browse(int(kw['leave_id']))
        })
        return request.render("ooto_hr_holidays_front.edit_leave", values)

    @http.route(['/leave/readonly/<int:leave_id>'], type='http', auth="user", website=True)
    def view_leave_request(self, page=1, sortby=None, search=None, search_in='content', **kw):
        return request.render("ooto_hr_holidays_front.edit_leave", {
            'leave': request.env['hr.leave'].sudo().browse(int(kw['leave_id'])),
            'read_only': True,
        })

    @http.route(['/leave/cancel/<int:leave_id>'], type='http', auth="user", website=True)
    def cancel_leave_request(self, **kw):
        current_employee = request.env['hr.employee'].search([('user_id', '=', request.session.uid)], limit=1)
        leave = request.env['hr.leave'].sudo().browse(int(kw['leave_id']))
        leave.action_refuse()
        if leave:
            leave.sudo().write({
                'state': 'cancel',
                'cancel_approver_id': current_employee.id,
                'cancel_date': datetime.now()
            })
            return self.my_helpdesk_leaves()

    @http.route(['/leave/edit/'], type='http', auth="user", website=True)
    def edit_leave_request(self, page=1, sortby=None, search=None, search_in='content', **kw):
        user = request.env.user
        employee_id = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)])
        type_id = request.env['hr.leave.type'].sudo().browse(int(kw['state_id']))
        if kw.get('request_date_from'):
            from_date = dateutil.parser.parse(kw.get('request_date_from')).date()
        if kw.get('request_date_to'):
            to_date = dateutil.parser.parse(kw.get('request_date_to')).date()
        leave_id = request.env['hr.leave'].sudo().browse(int(kw['leave_id']))
        period = ''
        if kw.get('halfday'):
            if kw.get('period') == _('Morning'):
                period = 'am'
            if kw.get('period') == _('Afternoon'):
                period = 'pm'

            domain = [('calendar_id', '=',
                       leave_id.employee_id.resource_calendar_id.id or request.env.user.company_id.resource_calendar_id.id)]
            attendances = request.env['resource.calendar.attendance'].search(domain, order='dayofweek, day_period DESC')
            # find first attendance coming after first_day
            attendance_from = next((att for att in attendances if int(att.dayofweek) >= from_date.weekday()),
                                   attendances[0])
            # find last attendance coming before last_day
            attendance_to = next((att for att in reversed(attendances) if int(att.dayofweek) <= from_date.weekday()),
                                 attendances[-1])
            if period == 'am':
                hour_from = float_to_time(attendance_from.hour_from)
                hour_to = float_to_time(attendance_from.hour_to)
            else:
                hour_from = float_to_time(attendance_to.hour_from)
                hour_to = float_to_time(attendance_to.hour_to)
            tz = request.env.user.tz or 'UTC'  # custom -> already in UTC
            date_from = timezone(tz).localize(datetime.combine(from_date, hour_from)).astimezone(
                UTC).replace(tzinfo=None)
            date_to = timezone(tz).localize(datetime.combine(from_date, hour_to)).astimezone(UTC).replace(tzinfo=None)

            nholidays = request.env['hr.leave'].sudo().search_count([('request_date_from', '<=', date_to),
                                                                     ('date_to', '>', date_from),
                                                                     ('employee_id', '=', leave_id.employee_id.id),
                                                                     ('id', '!=', leave_id.id),
                                                                     ('state', 'not in', ['cancel', 'refuse']),
                                                                     ])
            if nholidays:
                return request.render("ooto_hr_holidays_front.registration_leave", {
                    'leave_types': request.env['hr.leave.type'].sudo().search(
                        [('company_id', '=', employee_id.company_id.id)]),
                    'overlaps': True,
                })

            if type_id.allocation_type != 'no' and type_id.allow_credit == False:
                leave_days = type_id.get_days(leave_id.employee_id.id)[type_id.id]
                _logger.info("Leave Days ----------------------------->>>>>>>>>>>>>>>>>")
                _logger.info(leave_days)
                if float_compare(leave_days['remaining_leaves'], 0, precision_digits=2) == -1 or \
                        float_compare(leave_days['remaining_leaves'], 0, precision_digits=2) == 0 or \
                        float_compare(leave_days['virtual_remaining_leaves'], 0, precision_digits=2) == 0 or \
                        float_compare(leave_days['virtual_remaining_leaves'], 0, precision_digits=2) == -1:
                    return request.render("ooto_hr_holidays_front.registration_leave", {
                        'leave_types': request.env['hr.leave.type'].sudo().search(
                            [('company_id', '=', employee_id.company_id.id)]),
                        'sufficient': True,
                    })

            leave_id.write({
                'holiday_status_id': int(kw.get('state_id')),
                'request_date_from': kw.get('request_date_from'),
                'request_date_to': kw.get('request_date_from'),
                'date_from': kw.get('request_date_from'),
                'date_to': kw.get('request_date_to'),
                'request_date_from_period': period,
                'number_of_days': 0.5,
                'request_unit_half': kw.get('halfday'),
                'name': kw.get('name'),
            })
            if not leave_id.request_date_from:
                leave_id.date_from = False
                return

            if leave_id.request_unit_half or leave_id.request_unit_hours:
                leave_id.request_date_to = leave_id.request_date_from

            if not leave_id.request_date_to:
                leave_id.date_to = False
                return

            domain = [('calendar_id', '=',
                       leave_id.employee_id.resource_calendar_id.id or request.env.user.company_id.resource_calendar_id.id)]
            attendances = request.env['resource.calendar.attendance'].search(domain, order='dayofweek, day_period DESC')

            # find first attendance coming after first_day
            attendance_from = next(
                (att for att in attendances if int(att.dayofweek) >= leave_id.request_date_from.weekday()),
                attendances[0])
            # find last attendance coming before last_day
            attendance_to = next(
                (att for att in reversed(attendances) if int(att.dayofweek) <= leave_id.request_date_to.weekday()),
                attendances[-1])

            if leave_id.request_unit_half:
                if leave_id.request_date_from_period == 'am':
                    hour_from = float_to_time(attendance_from.hour_from)
                    hour_to = float_to_time(attendance_from.hour_to)
                else:
                    hour_from = float_to_time(attendance_to.hour_from)
                    hour_to = float_to_time(attendance_to.hour_to)
            else:
                hour_from = float_to_time(attendance_from.hour_from)
                hour_to = float_to_time(attendance_to.hour_to)

            tz = request.env.user.tz if request.env.user.tz and not leave_id.request_unit_custom else 'UTC'  # custom -> already in UTC
            leave_id.write(
                {'date_from': timezone(tz).localize(datetime.combine(leave_id.request_date_from, hour_from)).astimezone(
                    UTC).replace(tzinfo=None),
                 'date_to': timezone(tz).localize(datetime.combine(leave_id.request_date_to, hour_to)).astimezone(
                     UTC).replace(tzinfo=None)})
            if leave_id.date_from and leave_id.date_to:
                nb_days_hours = leave_id._get_number_of_days(leave_id.date_from, leave_id.date_to,
                                                             leave_id.employee_id.id)
                leave_id.write(
                    {'number_of_days': nb_days_hours['days']})
            else:
                leave_id.write({'number_of_days': 0})

            leave_id.activity_update(send_now=True)

        if not kw.get('halfday'):
            domain = [('calendar_id', '=',
                       leave_id.employee_id.resource_calendar_id.id or request.env.user.company_id.resource_calendar_id.id)]
            attendances = request.env['resource.calendar.attendance'].search(domain, order='dayofweek, day_period DESC')
            # find first attendance coming after first_day
            attendance_from = next((att for att in attendances if int(att.dayofweek) >= from_date.weekday()),
                                   attendances[0])
            # find last attendance coming before last_day
            attendance_to = next((att for att in reversed(attendances) if int(att.dayofweek) <= to_date.weekday()),
                                 attendances[-1])
            hour_from = float_to_time(attendance_from.hour_from)
            hour_to = float_to_time(attendance_to.hour_to)
            tz = request.env.user.tz or 'UTC'  # custom -> already in UTC
            date_from = timezone(tz).localize(datetime.combine(from_date, hour_from)).astimezone(
                UTC).replace(tzinfo=None)
            date_to = timezone(tz).localize(datetime.combine(to_date, hour_to)).astimezone(UTC).replace(tzinfo=None)
            nholidays = request.env['hr.leave'].sudo().search_count([('request_date_from', '<=', date_to),
                                                                     ('date_to', '>', date_from),
                                                                     ('employee_id', '=', leave_id.employee_id.id),
                                                                     ('id', '!=', leave_id.id),
                                                                     ('state', 'not in', ['cancel', 'refuse']),
                                                                     ])
            if nholidays:
                return request.render("ooto_hr_holidays_front.registration_leave", {
                    'leave_types': request.env['hr.leave.type'].sudo().search(
                        [('company_id', '=', employee_id.company_id.id)]),
                    'overlaps': True,
                })
            if type_id.allocation_type != 'no' and type_id.allow_credit == False:
                leave_days = type_id.get_days(leave_id.employee_id.id)[type_id.id]
                _logger.info("Leave Days ----------------------------->>>>>>>>>>>>>>>>>")
                _logger.info(leave_days)
                if float_compare(leave_days['remaining_leaves'], 0, precision_digits=2) == -1 or \
                        float_compare(leave_days['remaining_leaves'], 0, precision_digits=2) == 0 or \
                        float_compare(leave_days['virtual_remaining_leaves'], 0, precision_digits=2) == 0 or \
                        float_compare(leave_days['virtual_remaining_leaves'], 0, precision_digits=2) == -1:
                    return request.render("ooto_hr_holidays_front.registration_leave", {
                        'leave_types': request.env['hr.leave.type'].sudo().search(
                            [('company_id', '=', employee_id.company_id.id)]),
                        'sufficient': True,
                    })

            leave_id.write({
                'holiday_status_id': int(kw.get('state_id')),
                'request_date_from': kw.get('request_date_from'),
                'request_date_to': kw.get('request_date_to'),
                'date_from': kw.get('request_date_from'),
                'date_to': kw.get('request_date_to'),
                'request_unit_half': False,
                'name': kw.get('name'),
            })
            if not leave_id.request_date_from:
                leave_id.date_from = False
                return

            if leave_id.request_unit_half or leave_id.request_unit_hours:
                leave_id.request_date_to = leave_id.request_date_from

            if not leave_id.request_date_to:
                leave_id.date_to = False
                return

            domain = [('calendar_id', '=',
                       leave_id.employee_id.resource_calendar_id.id or request.env.user.company_id.resource_calendar_id.id)]
            attendances = request.env['resource.calendar.attendance'].search(domain, order='dayofweek, day_period DESC')

            # find first attendance coming after first_day
            attendance_from = next(
                (att for att in attendances if int(att.dayofweek) >= leave_id.request_date_from.weekday()),
                attendances[0])
            # find last attendance coming before last_day
            attendance_to = next(
                (att for att in reversed(attendances) if int(att.dayofweek) <= leave_id.request_date_to.weekday()),
                attendances[-1])

            if leave_id.request_unit_half:
                if leave_id.request_date_from_period == 'am':
                    hour_from = float_to_time(attendance_from.hour_from)
                    hour_to = float_to_time(attendance_from.hour_to)
                else:
                    hour_from = float_to_time(attendance_to.hour_from)
                    hour_to = float_to_time(attendance_to.hour_to)
            else:
                hour_from = float_to_time(attendance_from.hour_from)
                hour_to = float_to_time(attendance_to.hour_to)

            tz = request.env.user.tz if request.env.user.tz and not leave_id.request_unit_custom else 'UTC'  # custom -> already in UTC
            leave_id.write(
                {'date_from': timezone(tz).localize(datetime.combine(leave_id.request_date_from, hour_from)).astimezone(
                    UTC).replace(tzinfo=None),
                 'date_to': timezone(tz).localize(datetime.combine(leave_id.request_date_to, hour_to)).astimezone(
                     UTC).replace(tzinfo=None)})
            if leave_id.date_from and leave_id.date_to:
                nb_days_hours = leave_id._get_number_of_days(leave_id.date_from, leave_id.date_to,
                                                             leave_id.employee_id.id)
                leave_id.write(
                    {'number_of_days': nb_days_hours['days']})
            else:
                leave_id.write({'number_of_days': 0})

            leave_id.activity_update(send_now=True)
        if kw.get('base64textarea'):
            leave_id.add_attachment(leave_id.id, kw.get('base64textarea'), kw.get('name_file'))
            leave_id.write({
                'justificatory': kw.get('base64textarea'),
                'justificatory_filename': kw.get('name_file')
            })
        else:
            attach_id = request.env['ir.attachment'].search(
                [('res_id', '=', leave_id.id), ('res_model', '=', 'hr.leave')])
            if attach_id:
                attach_id.sudo().unlink()
            leave_id.write({
                'justificatory': False,
                'justificatory_filename': False
            })
        return request.redirect("/my/leaves")

    @http.route('/get/justificatory', type='json', auth='user', csrf=False)
    def get_leave_justificatory(self, leave_id, **kw):
        leave_id = request.env['hr.leave'].sudo().browse(int(leave_id))
        if leave_id and leave_id.justificatory:
            base64_data = leave_id.justificatory
            return {'base64_data': base64_data, 'file_name': leave_id.justificatory_filename}
        else:
            return {'error': 'Leave error'}

    @http.route('/absence/request', type='http', auth='user', website=True)
    def get_absence_request_template(self, **kw):
        user = request.env.user
        values = request.env['hr.leave'].browse(1).get_leave_data(user.id)
        return request.render("ooto_hr_holidays_front.absence_request_templates", values)

    @http.route('/leave/date', type="json", auth="none", csrf=False)
    def _get_leave_date(self):
        user = request.env.user
        if user:
            employee = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)])
            leaves = request.env['hr.leave'].sudo().search([('employee_id', '=', employee.id)]).mapped('date_from')
            leaves += request.env['hr.leave'].sudo().search([('employee_id', '=', employee.id)]).mapped('date_to')
            leave_list = list()
            leaves = [leave.strftime("%Y-%m-%d") for leave in leaves]
            for date in list(dict.fromkeys(leaves)):
                leave_list.append({'name': 'leave', 'date': date})
            return leave_list
        else:
            return {'access': False}

    def _get_number_of_days(self, date_from, date_to, employee_id):
        """ Returns a float equals to the timedelta between two dates given as string."""
        if employee_id:
            employee = request.env['hr.employee'].browse(employee_id)
            for i in [1, 2]:
                if date_to.weekday() == 4 + i and date_from.weekday() <= 4:
                    date_to -= timedelta(days=i)
            return employee.sudo()._get_work_days_data(date_from, date_to)

        today_hours = request.env.company.resource_calendar_id.sudo().get_work_hours_count(
            datetime.combine(date_from.date(), time.min),
            datetime.combine(date_from.date(), time.max),
            False)

        hours = request.env.company.resource_calendar_id.sudo().get_work_hours_count(date_from, date_to)

        return {'days': hours / (today_hours or HOURS_PER_DAY), 'hours': hours}


class CustomerPortalHrHolidays(OotoCustomerPortal):

    @route(['/my/account'], type='http', auth='user', website=True)
    def account(self, redirect=None, **post):
        if request.env.user.partner_id.employee_id:
            res = super(CustomerPortalHrHolidays, self).account(redirect, **post)
            user = request.env.user
            leave_data = request.env['hr.leave'].get_leave_data(user.id)
            res.qcontext.update(leave_data)
            return res
        else:
            return super(CustomerPortalHrHolidays, self).account(redirect, **post)
