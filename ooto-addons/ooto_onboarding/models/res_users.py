# -*- coding: utf-8 -*-

import datetime
from datetime import timedelta
from odoo.exceptions import UserError
from odoo.addons.auth_signup.models.res_partner import SignupError, now
from odoo.tools import config
from odoo import api, fields, models, modules, _, SUPERUSER_ID, sql_db
from odoo.tools.image import image_data_uri
import logging

_logger = logging.getLogger(__name__)


class Users(models.Model):
    _inherit = 'res.users'

    is_onboarding_first_connection = fields.Boolean()

    def get_signup_url(self):
        user_id = self.env['res.users'].search([('login', '=', self.login)])
        if user_id:
            if not user_id.partner_id.signup_valid:
                user_id.partner_id.signup_prepare(signup_type="reset", expiration=False)
            return user_id.partner_id.signup_url
        return False

    @api.model
    def systray_get_activities(self):
        res = super(Users, self).systray_get_activities()
        task_reminders = self.env['task.reminder.notif']
        all_task_reminders = self.env['task.reminder.notif'].sudo().search(
            [('is_done', '=', False), ('task_id.onboarding_id.employee_id.user_id', '=', self.env.uid)],
            order='notify_date DESC')
        cur_date = fields.Datetime.now()
        for task in all_task_reminders.mapped('task_id'):
            for reminder in all_task_reminders.filtered(lambda l: l.task_id == task):
                if reminder.notify_date <= cur_date:
                    task_reminders += reminder
                    break
        if task_reminders:
            onboarding_role = self.env.ref('ooto_onboarding.onboarding_role_onboarder', raise_if_not_found=False)
            meeting_label = _("Onboarding tasks")
            reminder_systray = {
                'type': 'onboarding_task',
                'name': meeting_label,
                'model': 'hr.onboarding.task',
                'icon': onboarding_role and (
                    image_data_uri(onboarding_role.image) if onboarding_role.image else None) or False,
                'task_reminders': task_reminders.sudo().read(['task_id', 'alarm_id', 'notify_date']),
            }
            res.insert(0, reminder_systray)
        return res
    
    #HRN ADD: modify odoo natif function
    @api.constrains('groups_id')
    def _check_one_user_type(self):
        """We check that no users are both portal and users (same with public).
           This could typically happen because of implied groups.
        """
        user_types_category = self.env.ref('base.module_category_user_type', raise_if_not_found=False)
        user_types_groups = self.env['res.groups'].search(
            [('category_id', '=', user_types_category.id)]) if user_types_category else False
        if user_types_groups and user_types_groups.ids in self.groups_id.ids:  # needed at install
            if self._has_multiple_groups(user_types_groups.ids):
                raise ValidationError(_('The user cannot have more than one user types.'))
