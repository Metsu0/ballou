# -*- coding: utf-8 -*-


from odoo import models, _, fields, api, SUPERUSER_ID, sql_db, registry
from odoo.tools import config
import datetime

onboarding_states = [
    ('draft', 'Draft'),
    ('before_the_arrival', 'Before the arrival'),
    ('first_week', 'First week'),
    ('first_month', 'First month'),
    ('after_first_month', 'After first month')
]


class HrOnboarding(models.Model):
    _name = 'hr.onboarding'
    _description = 'HR onboarding'
    _rec_name = 'employee_id'

    # name = fields.Text("Name", required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    employee_image = fields.Binary(string='Employee image', related='employee_id.image_1920')
    employee_position_id = fields.Many2one('hr.job', string='Employee position', related='employee_id.job_id')
    employee_department_id = fields.Many2one('hr.department', string='Employee department',
                                             related='employee_id.department_id')
    onboarding_progression = fields.Integer(string='Progression', compute='get_onboarding_progression',
                                            compute_sudo=True)
    onboarding_state = fields.Selection(onboarding_states, string='State', default='draft')
    appointment_count = fields.Integer('Number of Appointment', compute='_compute_appointment_count')
    task_ids = fields.One2many("hr.onboarding.task", "onboarding_id", string="Task")
    arrival_date = fields.Date("Arrival date", related="employee_id.hiring_date")
    trial_date_end = fields.Date("End of Trial Period", compute="_compute_trial_date_end")
    trial_date_end_name = fields.Char(compute="_compute_trial_date_end")
    state = fields.Selection([('draft', _('Draft')), ('active', _('Active')), ], string="Status",
                             compute="_compute_state_onboarding")
    remaining_day = fields.Integer("Remaining dat", compute="_compute_remaining_day")
    period = fields.Selection([
        ('before_arrival', _('Before arrival')),
        ('arrival_day', _('Arrival day')),
        ('first_week', _('First week')),
        ('first_month', _('First month')),
        ('after_first_month', _('After first month')),
    ], string="Period", compute="_compute_period_employee")
    period_display = fields.Selection([
        ('1before_arrival', _('Before arrival')),
        ('2arrival_day', _('Arrival day')),
        ('3first_week', _('First week')),
        ('4first_month', _('First month')),
        ('5after_first_month', _('After first month')),
    ], string="Period", compute="_compute_period_employee", store=True)
    renewal_contract_name = fields.Text(compute="_compute_renewal_contract")
    admin_ratio = fields.Integer(compute="_compute_statistics", string='Received Ratio')
    others_ratio = fields.Integer(compute="_compute_statistics", string='Received Ratio')
    content_ratio = fields.Integer(compute="_compute_statistics", string='Opened Ratio')
    signature_ratio = fields.Integer(compute="_compute_statistics", string='Replied Ratio')
    form_ratio = fields.Integer(compute="_compute_statistics", String='Bounced Ratio')
    email_ratio = fields.Integer(compute="_compute_statistics", String='Bounced Ratio')
    before_arrival = fields.Integer(compute="_compute_period_progress", string='Before arrival')
    arrival_day = fields.Integer(compute="_compute_period_progress", string='Arrival day')
    first_week = fields.Integer(compute="_compute_period_progress", string='First week')
    first_month = fields.Integer(compute="_compute_period_progress", string='First month')
    after_first_month = fields.Integer(compute="_compute_period_progress", String='After first month')
    before_arrival_n_x = fields.Char(compute="_compute_progress_n_x", string='Before arrival')
    arrival_day_n_x = fields.Char(compute="_compute_progress_n_x", string='Arrival day')
    first_week_n_x = fields.Char(compute="_compute_progress_n_x", string='First week')
    first_month_n_x = fields.Char(compute="_compute_progress_n_x", string='First month')
    after_first_month_n_x = fields.Char(compute="_compute_progress_n_x", String='After first month')
    active = fields.Boolean("Active", default=True)
    option = fields.Selection([
        ('send_notification', _('Send / schedule an invitation by email')),
        ('set_password', _('Set the password (without sending an email)')),
        ('send_email_onboarding', _('Send an email to the creation of onboarding')),
        ('do_nothing', _('Do Nothing')),
    ], 'Creation Option', related='employee_id.option')

    @api.depends('employee_id')
    def _compute_state_onboarding(self):
        for rec in self:
            if rec.employee_id.user_id.state == 'active':
                rec.state = 'active'
            else:
                rec.state = 'draft'

    def _get_task_value(self, period="", task_type="", state=False):
        for rec in self:
            if period and task_type == "" and not state:
                return len(rec.task_ids.filtered(lambda t: t.period == period))
            if task_type and period == "" and not state:
                return len(rec.task_ids.filtered(lambda t: t.task_type == task_type))
            if task_type == "" and period == "" and state:
                return len(rec.task_ids.filtered(lambda t: t.task_state == 'terminated'))
            if period and state and task_type == "":
                task_ids = rec.task_ids.filtered(lambda t: t.period == period)
                return len(task_ids.filtered(lambda t: t.task_state == 'terminated'))
            if period and not state and task_type:
                task_ids = rec.task_ids.filtered(lambda t: t.period == period)
                return len(task_ids.filtered(lambda t: t.task_type == task_type))
            if period == "" and state and task_type:
                task_ids = rec.task_ids.filtered(lambda t: t.task_state == 'terminated')
                return len(task_ids.filtered(lambda t: t.task_type == task_type))

    @api.depends('task_ids')
    def _compute_progress_n_x(self):
        for rec in self:
            rec.before_arrival_n_x = "%s/%s" % (
                rec._get_task_value(period='before_arrival', state=True),
                rec._get_task_value(period='before_arrival'))
            rec.arrival_day_n_x = "%s/%s" % (
                rec._get_task_value(period='arrival_day', state=True),
                rec._get_task_value(period='arrival_day'))
            rec.first_week_n_x = "%s/%s" % (
                rec._get_task_value(period='first_week', state=True),
                rec._get_task_value(period='first_week'))
            rec.first_month_n_x = "%s/%s" % (
                rec._get_task_value(period='first_month', state=True),
                rec._get_task_value(period='first_month'))
            rec.after_first_month_n_x = "%s/%s" % (
                rec._get_task_value(period='after_first_month', state=True),
                rec._get_task_value(period='after_first_month'))

    @api.depends('task_ids', 'task_ids.task_state')
    def _compute_statistics(self):
        for rec in self:
            rec.admin_ratio = 0
            rec.others_ratio = 0
            rec.content_ratio = 0
            rec.signature_ratio = 0
            rec.form_ratio = 0
            rec.email_ratio = 0
            admin_ratio = rec._get_task_value(task_type='administrative')
            others_ratio = rec._get_task_value(task_type='others')
            content_ratio = rec._get_task_value(task_type='content')
            signature_ratio = rec._get_task_value(task_type='signature')
            form_ratio = rec._get_task_value(task_type='form')
            email_ratio = rec._get_task_value(task_type='email')
            if admin_ratio and admin_ratio > 0:
                rec.admin_ratio = (rec._get_task_value(task_type='administrative', state=True) / admin_ratio) * 100
            if others_ratio and others_ratio > 0:
                rec.others_ratio = (rec._get_task_value(task_type='others', state=True) / others_ratio) * 100
            if content_ratio and content_ratio > 0:
                rec.content_ratio = (rec._get_task_value(task_type='content', state=True) / content_ratio) * 100
            if signature_ratio and signature_ratio > 0:
                rec.signature_ratio = (rec._get_task_value(task_type='signature', state=True) / signature_ratio) * 100
            if form_ratio and form_ratio > 0:
                rec.form_ratio = (rec._get_task_value(task_type='form', state=True) / form_ratio) * 100
            if email_ratio and email_ratio > 0:
                rec.email_ratio = (rec._get_task_value(task_type='email', state=True) / email_ratio) * 100

    @api.depends('task_ids')
    def _compute_period_progress(self):
        for rec in self:
            rec.before_arrival = 0
            rec.arrival_day = 0
            rec.first_week = 0
            rec.first_month = 0
            rec.after_first_month = 0
            before_arrival = rec._get_task_value(period='before_arrival')
            arrival_day = rec._get_task_value(period='arrival_day')
            first_week = rec._get_task_value(period='first_week')
            first_month = rec._get_task_value(period='first_month')
            after_first_month = self._get_task_value(period='after_first_month')
            if before_arrival and before_arrival > 0:
                rec.before_arrival = (rec._get_task_value(period='before_arrival', state=True) / before_arrival) * 100
            if arrival_day and arrival_day > 0:
                rec.arrival_day = (rec._get_task_value(period='arrival_day', state=True) / arrival_day) * 100
            if first_week and first_week > 0:
                rec.first_week = (rec._get_task_value(period='first_week', state=True) / first_week) * 100
            if first_month and first_month > 0:
                rec.first_month = (rec._get_task_value(period='first_month', state=True) / first_month) * 100
            if after_first_month and after_first_month > 0:
                rec.after_first_month = (rec._get_task_value(period='after_first_month', state=True) /
                                         after_first_month) * 100

    @api.depends('arrival_date')
    def _compute_period_employee(self):
        for rec in self:
            now = datetime.datetime.now().date()
            rec.period = rec.period_display = False
            if rec.arrival_date:
                if rec.arrival_date == now:
                    rec.period = 'arrival_day'
                    rec.period_display = '2arrival_day'
                elif rec.arrival_date > now:
                    rec.period = 'before_arrival'
                    rec.period_display = '1before_arrival'
                elif now > rec.arrival_date > now - datetime.timedelta(weeks=1):
                    rec.period = 'first_week'
                    rec.period_display = '3first_week'
                elif now > rec.arrival_date > now - datetime.timedelta(weeks=4):
                    rec.period = 'first_month'
                    rec.period_display = '4first_month'
                else:
                    rec.period = 'after_first_month'
                    rec.period_display = '5after_first_month'

    def automatic_update_period_employee(self):
        onboardings = self.env['hr.onboarding'].search([('id', '!=', None)])
        for rec in onboardings:
            now = datetime.datetime.now().date()
            if rec.arrival_date:
                if rec.arrival_date == now:
                    # rec.period = 'arrival_day'
                    rec.period_display = '2arrival_day'
                elif rec.arrival_date > now:
                    # rec.period = 'before_arrival'
                    rec.period_display = '1before_arrival'
                elif now > rec.arrival_date > now - datetime.timedelta(weeks=1):
                    # rec.period = 'first_week'
                    rec.period_display = '3first_week'
                elif now > rec.arrival_date > now - datetime.timedelta(weeks=4):
                    # rec.period = 'first_month'
                    rec.period_display = '4first_month'
                else:
                    # rec.period = 'after_first_month'
                    rec.period_display = '5after_first_month'

    @api.depends('task_ids')
    def get_onboarding_progression(self):
        for rec in self:
            rec.onboarding_progression = 0
            terminated = rec.task_ids.filtered(lambda t: t.task_state == 'terminated')
            if len(rec.task_ids) > 0:
                rec.onboarding_progression = (len(terminated) / len(rec.task_ids)) * 100

    def _compute_appointment_count(self):
        for rec in self:
            rec.appointment_count = 0

    def _compute_remaining_day(self):
        for onboarding in self:
            onboarding.remaining_day = False
            if onboarding.trial_date_end:
                date_now = datetime.datetime.now().date()
                contracts = self.env['hr.contract'].search([('employee_id', '=', onboarding.employee_id.id)])
                if self.env['hr.contract'].search_count(
                        [('employee_id', '=', onboarding.employee_id.id)]) > 0:
                    contracts_count = self.env['hr.contract'].search_count(
                        [('employee_id', '=', onboarding.employee_id.id)])
                    if contracts:
                        if contracts[contracts_count - 1].trial_date_end > date_now:
                            onboarding.remaining_day = (contracts[contracts_count - 1].trial_date_end - date_now).days
                        else:
                            onboarding.remaining_day = 0

    def open_appointment(self):
        self.ensure_one()
        result = {
            'name': _("Appointment list"),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.onboarding.task',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'domain': [('id', 'in', self.task_ids.ids), ('task_type', '=', 'appointment')],
            'context': {'create': False},
        }
        return result

    def open_contents(self):
        self.ensure_one()
        result = {
            'name': _("Contents list"),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.onboarding.task',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'domain': [('id', 'in', self.task_ids.ids), ('task_type', '=', 'content')],
            'context': {'create': False},
        }
        return result

    def open_others(self):
        self.ensure_one()
        result = {
            'name': _("Others list"),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.onboarding.task',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'domain': [('id', 'in', self.task_ids.ids), ('task_type', '=', 'others')],
            'context': {'create': False},
        }
        return result

    def open_form(self):
        self.ensure_one()
        result = {
            'name': _("Form list"),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.onboarding.task',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'domain': [('id', 'in', self.task_ids.ids), ('task_type', '=', 'form')],
            'context': {'create': False},
        }
        return result

    def open_email(self):
        self.ensure_one()
        result = {
            'name': _("Form list"),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.onboarding.task',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'domain': [('id', 'in', self.task_ids.ids), ('task_type', '=', 'email')],
            'context': {'create': False},
        }
        return result

    def open_administrative(self):
        self.ensure_one()
        result = {
            'name': _("Administrative list"),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.onboarding.task',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'domain': [('id', 'in', self.task_ids.ids), ('task_type', '=', 'administrative')],
            'context': {'create': False},
        }
        return result

    def open_signature(self):
        self.ensure_one()
        result = {
            'name': _("Signature list"),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.onboarding.task',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'domain': [('id', 'in', self.task_ids.ids), ('task_type', '=', 'signature')],
            'context': {'create': False},
        }
        return result

    def open_activity(self):
        self.ensure_one()
        result = {
            'name': _("Activity list"),
            'type': 'ir.actions.act_window',
            'res_model': 'mail.message',
            'view_mode': 'tree',
            'domain': [('onboarding_id', '=', self.id)],
            'view_type': 'form',
        }
        return result

    def open_on_boarded(self):
        self.ensure_one()
        emp = self.employee_id
        domain = [emp.parent_id.id, emp.coach_id.id, emp.admin_responsible_id.id, emp.software_responsible_id.id]
        result = {
            'name': _("On boarded list"),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'domain': [('id', 'in', domain)],
            'context': {'create': False},
        }
        return result

    def open_employee_action(self):
        self.ensure_one()
        result = {
            'name': _("Employee"),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.employee_id.id
        }
        return result

    @api.depends('employee_id')
    def _compute_trial_date_end(self):
        hr_contract_obj = self.env['hr.contract']
        for onboarding in self:
            onboarding.trial_date_end = False
            onboarding.trial_date_end_name = False
            contracts = hr_contract_obj.search([('employee_id', '=', onboarding.employee_id.id)])
            if len(contracts) > 0:
                contracts_count = len(contracts)
                trial_date_end = contracts[contracts_count - 1].trial_date_end
                onboarding.trial_date_end = trial_date_end
                if trial_date_end:
                    onboarding.trial_date_end_name = str(trial_date_end.strftime("%d %B"))

    def _compute_renewal_contract(self):
        for onboarding in self:
            onboarding.renewal_contract_name = False
            contracts = self.env['hr.contract'].search([('employee_id', '=', onboarding.employee_id.id)])
            if self.env['hr.contract'].search_count(
                    [('employee_id', '=', onboarding.employee_id.id)]) > 0:
                contracts_count = self.env['hr.contract'].search_count(
                    [('employee_id', '=', onboarding.employee_id.id)])
                if contracts:
                    if contracts[contracts_count - 1].renew_date_end_trial:
                        onboarding.renewal_contract_name = _("renewed")
                    else:
                        onboarding.renewal_contract_name = _("not renewed")

    @api.model
    def create(self, vals):
        """
        Method to generate task for new employee
        :param vals: Created onboarding fields dict
        :return: create result
        """
        res = super(HrOnboarding, self).create(vals)
        employee_id = res.employee_id
        task_ids = self.env['hr.onboarding.task'].search(
            [('parent_id', '=', False), ('is_from_onboarding', '=', False), ('is_onboarder', '=', False)])
        for task in task_ids:
            task.action_publish_task(employee_id) if task.task_type != 'appointment' else None

        if employee_id.is_new_employee:
            manager_task_ids = self.env['hr.onboarding.task'].search(
                [('parent_id', '=', False), ('is_from_onboarding', '=', False), ('is_onboarder', '=', True)])

            for manager_task_id in manager_task_ids:
                manager_task_id.action_publish_task_onboarder(employee_id) if manager_task_id.task_type != 'appointment' else None

        return res

    def send_my_invitation(self):
        return self.action_invitation_send(self.id)

    @api.model
    def action_invitation_send(self, on_id):
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        onboarding_id = self.browse(on_id)
        user_id = self.env['res.users'].search([('login', '=', onboarding_id.employee_id.user_id.login)])
        if not user_id.partner_id.signup_valid:
            user_id.partner_id.signup_prepare(signup_type="reset", expiration=False)
        template_id = self.env.ref('ooto_onboarding.set_password_email_ooto', raise_if_not_found=False)
        # assert template_id._name == 'mail.template'
        template_values = {
            'email_to': '${object.email|safe}',
            'email_cc': False,
            'auto_delete': True,
            'partner_to': False,
            'scheduled_date': False,
        }
        template_id.write(template_values)
        ctx = {
            'default_model': 'res.users',
            'default_res_id': user_id.id,
            'default_use_template': bool(template_id),
            'default_template_id': template_id.id,
            'default_partner_ids': [(4, user_id.partner_id.id)],
            'force_email': True,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    def write(self, values):
        res = super(HrOnboarding, self).write(values)
        if values.get('task_ids', False):
            for rec in self:
                new_tasks = rec.task_ids.filtered(lambda l: not l.onboarding_id)
                if new_tasks:
                    new_tasks.write({'onboarding_id': rec.id})
        if values.get('task_ids', False):
            self.update_sign_request()
        return res

    def update_sign_request(self):
        for rec in self:
            for task in rec.task_ids.filtered(lambda l: l.task_type == 'signature' and l.is_from_onboarding):
                if task.is_from_onboarding and task.sign_template_id and not task.sign_request_id:
                    task.create_sign_request(rec, task)

    def get_onboarding_task_action(self):
        """
        Method to manage child tasks from kanban, tree and form views
        :return: child task views
        """
        tree_view_id = self.env.ref('ooto_onboarding.onboarding_task_tree_views').id
        form_view_id = self.env.ref('ooto_onboarding.onboarding_task_form_views').id
        kanban_view_id = self.env.ref('ooto_onboarding.ooto_hr_onboarding_task_kanban_view').id
        result = {
            "name": self.employee_id.display_name,
            "type": "ir.actions.act_window",
            "res_model": "hr.onboarding.task",
            "views": [[kanban_view_id, "kanban"], [form_view_id, "form"], [tree_view_id, "tree"]],
            "view_type": "form",
            "view_id": kanban_view_id,
            "view_mode": "kanban,form,tree",
            "domain": [('id', 'in', self.task_ids.mapped('id'))],
            "context": {
                'onboarding_id': self.id,
                'current_employee_id': self.employee_id.id,
                'option_emp': self.employee_id.option,
                'mailing_model_id': self.env.ref('base.model_res_partner').id,
                'current_employee_email': self.employee_id.work_email,
                'search_default_group_by_period': 1,
                'default_task_state': 'to_do',
                'is_create_child_task': True,
                'default_is_from_onboarding': True,
            },
        }
        return result
