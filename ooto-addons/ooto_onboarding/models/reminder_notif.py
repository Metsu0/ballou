# -*- coding: utf-8 -*-

import datetime
from datetime import timedelta

from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, pycompat


class TaskReminderNotif(models.Model):
    _name = 'task.reminder.notif'
    _description = 'Task Reminder Notification'

    task_id = fields.Many2one('hr.onboarding.task', required=True, ondelete='cascade')
    alarm_id = fields.Many2one('calendar.alarm', string='Calendar alarm', required=True, ondelete='cascade')
    is_done = fields.Boolean(string='Is done', default=False)
    is_showed = fields.Boolean(string='Is showed', default=False)
    is_mail_send = fields.Boolean(string='Is mail sent', default=False)
    notify_date = fields.Datetime(string='Notify date', compute='_compute_reminder', compute_sudo=True, store=True)
    display_time = fields.Char('Event Time', compute='_compute_reminder')

    @api.model
    def create(self, vals):
        res = super(TaskReminderNotif, self).create(vals)
        self.notify_next_alarm(res.task_id.onboarding_id.employee_id.user_id)
        return res

    @api.model
    def _get_date_formats(self):
        lang = self._context.get("lang")
        lang_params = {}
        if lang:
            record_lang = self.env['res.lang'].search([("code", "=", lang)], limit=1)
            lang_params = {
                'date_format': record_lang.date_format,
                'time_format': record_lang.time_format
            }
        format_date = pycompat.to_text(lang_params.get("date_format", '%B-%d-%Y'))
        format_time = pycompat.to_text(lang_params.get("time_format", '%I-%M %p'))
        return (format_date, format_time)

    @api.depends('task_id.date_end', 'alarm_id.duration_minutes')
    def _compute_reminder(self):
        timezone = self._context.get('tz') or self.env.user.partner_id.tz or 'UTC'
        timezone = pycompat.to_text(timezone)
        format_date, format_time = self._get_date_formats()
        self_tz = self.with_context(tz=timezone)
        for rec in self:
            rec.notify_date = False
            rec.display_time = False
            if rec.task_id.date_end:
                rec.notify_date = rec.task_id.date_end - timedelta(minutes=rec.alarm_id.duration_minutes)
                date = fields.Datetime.context_timestamp(self_tz, fields.Datetime.from_string(rec.task_id.date_end))
                to_text = pycompat.to_text
                date_str = to_text(date.strftime(format_date))
                time_str = to_text(date.strftime(format_time))
                rec.display_time = _("End date: %s") % (date_str)
                

    @api.model
    def done_reminder_notif(self, reminder_id):
        reminder = self.sudo().browse(reminder_id)
        reminders = self.sudo().search([('is_done', '=', False), ('task_id', '=', reminder.task_id.id),
                                        ('notify_date', '<=', reminder.notify_date)])
        if reminders:
            reminders.sudo().write({'is_done': True})
            return True
        return False

    @api.model
    def done_reminder_mail(self, reminder_id):
        reminder = self.sudo().browse(reminder_id)
        reminders = self.sudo().search([('is_mail_send', '=', False), ('task_id', '=', reminder.task_id.id),
                                        ('notify_date', '<=', reminder.notify_date)])
        if reminders:
            reminders.sudo().write({'is_mail_send': True})
            return True
        return False

    @api.model
    def mark_as_shown_reminder_notif(self, reminder_id):
        reminder = self.sudo().browse(reminder_id)
        reminder.sudo().write({'is_showed': True})

    @api.model
    def do_notif_reminder(self, reminder):
        message = reminder.display_time
        delta = reminder.notify_date - datetime.datetime.now()
        delta = delta.seconds + delta.days * 3600 * 24
        return {
            'event_id': reminder.task_id.id,
            'reminder_id': reminder.id,
            'title': reminder.task_id.name,
            'message': message,
            'timer': delta,
            'notify_at': reminder.notify_date,
        }

    @api.model
    def get_next_notif(self):
        all_notif = []
        task_reminders = self.sudo()
        all_task_reminders = self.sudo().search(
            [('is_done', '=', False), ('is_showed', '=', False),
             ('task_id.onboarding_id.employee_id.user_id', '=', self.env.uid)],
            order='notify_date DESC')
        cur_date = fields.Datetime.now()
        for task in all_task_reminders.mapped('task_id'):
            for reminder in all_task_reminders.filtered(lambda l: l.task_id == task):
                if reminder.notify_date <= cur_date:
                    task_reminders += reminder
                    break
        for reminder in task_reminders:
            all_notif.append(self.sudo().do_notif_reminder(reminder))
        return all_notif

    def notify_next_alarm(self, user):
        notifications = []
        notif = self.with_user(user.id).get_next_notif()
        notifications.append([(self._cr.dbname, 'hr.onboarding.task', user.partner_id.id), notif])
        if len(notifications) > 0:
            self.env['bus.bus'].sendmany(notifications)

    @api.model
    def send_mail_task_reminder(self):
        task_reminders = self.sudo()
        all_task_reminders = self.sudo().search([('is_mail_send', '=', False)], order='notify_date DESC')
        for task in all_task_reminders.mapped('task_id'):
            for reminder in all_task_reminders.filtered(lambda l: l.task_id == task):
                if reminder.notify_date <= fields.Datetime.now():
                    task_reminders += reminder
                    break
        for reminder in task_reminders:
            email_template_ = self.env.ref('ooto_onboarding.email_template_task_reminder')
            send_mail = self.env['mail.template'].browse(email_template_.id).send_mail(reminder.id)
            if send_mail:
                self.done_reminder_mail(reminder.id)
