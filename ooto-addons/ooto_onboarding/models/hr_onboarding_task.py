# -*- coding: utf-8 -*-

import datetime
from datetime import timedelta, MAXYEAR
import time
import re

from dateutil.relativedelta import relativedelta
from werkzeug import urls
from odoo import api, _, fields, models, exceptions
from odoo.tools.safe_eval import safe_eval
from odoo.http import request
from odoo.exceptions import ValidationError

no_write_fields = [
    'image_task',
    'partner_ids',
    'partner_domain',
    'employee_ids',
    'employee_domain',
    'support'
]
order_period = [
    'before_arrival',
    'arrival_day',
    'first_week',
    'first_month',
    'after_first_month'
]
FIELD_TYPES = [(key, key) for key in sorted(fields.Field.by_type)]


class IrModelTask(models.Model):
    _name = 'ir.model.task'
    _description = 'Creation fields model task'

    name = fields.Char('Field Name', required=True, index=True)
    title = fields.Char("Field Title", required=True)
    description = fields.Char("Field Description", required=True, )
    field_description = fields.Char(string='Field Label', default='', required=True)
    ttype = fields.Selection(selection=FIELD_TYPES, string='Field Type', required=True)
    required = fields.Boolean("Required")
    need_validation = fields.Boolean("Need validation")


class HrOnboardingTaskType(models.Model):
    _name = 'hr.onboarding.task.type'
    _description = 'Hr Onboarding Task type'

    name = fields.Char("Title", required=True, translate=True)


class HrOnboardingTask(models.Model):
    _name = 'hr.onboarding.task'
    _description = 'Hr Onboarding Task'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin']

    @api.model
    def _default_role(self):
        onboarding_role = self.env.ref('ooto_onboarding.onboarding_role_onboarder', raise_if_not_found=False)
        return onboarding_role.id if onboarding_role else False

    name = fields.Char("Title", required=True)
    description = fields.Text("Description", required=True)
    # domain
    type_domain = fields.Selection([('contact', 'Contact'), ('employee', 'Employee'), ], string="Onboarding filter",
                                   default='employee')
    # partner_ids = fields.Many2many("res.partner", string="Partner", copy=False)
    # partner_domain = fields.Char(string='Contact domain', default=[], copy=False)
    employee_ids = fields.Many2many("hr.employee", string="Employee", copy=False)

    employee_domain = fields.Char(string='Employee domain', default=[], copy=False)
    #
    task_type_id = fields.Many2one("hr.onboarding.task.type", string="", required=False, )
    task_type = fields.Selection([
        ('form', _('Form')),
        ('content', _('Content')),
        ('software', _('Software')),
        ('signature', _('Signature')),
        ('others', _('Others')),
        ('administrative', _('administrative')),
        ('appointment', _('Appointment')),
        ('equipment', _('Equipment')),
        ('advice', _('Advice')),
        ('email', _('Email')),
    ], string="Task type", required=True)
    stain_label = fields.Char("Stain label", compute="compute_stain_label", store=True)
    is_retroactive = fields.Boolean("Retroactive")
    arrival_x = fields.Integer("Arrival X", default=1)
    to_do_for = fields.Selection([
        ('day_arrival', _('The of day arrival')),
        ('x_day_before', _('X days before arrival')),
        ('x_day_after', _('X days after arrival')),
        ('first_week', _('The first week')),
        ('first_month', _('The first month')),
        ('before_x_month', _('Before the first X months')),
        ('after_x_month', _('After the first X months')),
        ('specific', _('Specific')),
    ], string="To do for", required=True)
    period = fields.Selection([
        ('before_arrival', _('Before arrival')),
        ('arrival_day', _('Arrival day')),
        ('first_week', _('First week')),
        ('first_month', _('First month')),
        ('after_first_month', _('After first month')),
        ('specific', _('Specific')),
    ], string="Period", compute="_compute_period_task", store=True)
    period_display = fields.Selection([
        ('1before_arrival', _('Before arrival')),
        ('2arrival_day', _('Arrival day')),
        ('3first_week', _('First week')),
        ('4first_month', _('First month')),
        ('5after_first_month', _('After first month')),
        ('6specific', _('Specific')),
    ], string="Period", compute="_compute_period_task", store=True)
    # task_state_id = fields.Many2one("hr.task.state", "Task state", compute="_compute_task_state")
    task_state = fields.Selection([
        ('draft', _('Draft')),
        ('to_do', _('To do')),
        ('terminated', _('Terminated')),
        ('late', _('Late')),
        ('done', _('Done')),
        ('published', _('Published')),
        ('unpublished', _('Unpublished')),
    ], string="Task state", compute="_compute_task_state", compute_sudo=True)
    state_late = fields.Boolean()
    status_late = fields.Boolean()
    status_to_do = fields.Boolean()
    finished_in_time = fields.Boolean("Finished in time")
    status_terminated = fields.Boolean()
    parent_task_state = fields.Selection(related="parent_id.task_state")
    date_start = fields.Datetime("Date start")
    date_end = fields.Datetime("Date end", required=False, compute="_compute_date_end")
    date_end_char = fields.Char("Date end", compute="_compute_date_end")
    location = fields.Char("Location")
    is_from_onboarding = fields.Boolean("From onboarding")
    # Parent and childs task
    parent_id = fields.Many2one('hr.onboarding.task', 'Task parent', ondelete="cascade")
    child_ids = fields.One2many('hr.onboarding.task', 'parent_id', string='Childs task')
    # Additional field for each type of task
    survey_id = fields.Many2one("survey.survey", "Form")
    image_task_child = fields.Binary("Image task", related="parent_id.image_task")
    image_task = fields.Binary("Image task", copy=False)
    icon_task_child = fields.Binary("Icon task", related="parent_id.icon_task")
    icon_task = fields.Binary("Icon task", copy=False)
    support = fields.Binary("Support", copy=False)
    support_name = fields.Char()
    support_child = fields.Binary("Support", related="parent_id.support")
    url = fields.Char("URL")
    page_id = fields.Many2one("website.page", "Page")
    content_type = fields.Selection([
        ('document', 'Document'),
        ('video', 'Video'),
        ('url', _('External URL')),
        ('internal_url', _('Internal URL'))
    ], string="Content type")
    administrative_type = fields.Selection([
        ('document_fill', 'Document to fill'),
        ('upload_file', 'Upload file'),
    ], string="Administrative type")
    timer = fields.Float('Timer')
    timer_check = fields.Boolean('Activate timer')
    scroll_check = fields.Boolean('Verification scroll')
    # Validation task
    is_terminated_validator = fields.Boolean("Validate by responsible")
    is_published = fields.Boolean("Is published")
    is_unpublished = fields.Boolean("Is unpublished")
    publication_state = fields.Selection([
        ('draft', _('Draft')),
        ('published', _('Published')),
        ('unpublished', _('Unpublished'))], default="draft", string="Task state")
    # onboarding
    onboarding_ids = fields.Many2many("hr.onboarding", string="On Boarding", compute="_compute_onboarding")
    onboarding_id = fields.Many2one("hr.onboarding", string="On Boarding", ondelete="cascade")
    onboarding_count = fields.Integer("On boarding count", compute="_compute_onboarding")
    # calendar
    calendar_event_id = fields.Many2one("calendar.event", "Task event")
    task_recall_ids = fields.Many2many("calendar.alarm", string="Recall")
    #
    order_seq = fields.Integer("order seq", compute="_compute_period_task")
    is_survey_filled = fields.Boolean("Is survey filled", default=False)
    role_id = fields.Many2one("onboarding.role", string="Role", default=_default_role)
    role_image = fields.Binary(related="role_id.image")
    employee_image = fields.Binary(related="onboarding_id.employee_image")
    late_days = fields.Integer(string="Late days", compute="_compute_late_days")
    sign_template_id = fields.Many2one('sign.template', string='Sign template')
    sign_request_id = fields.Many2one('sign.request', string='Sign request')
    delay = fields.Integer("Delay (Month nb)")

    employee_fields_documents_ids = fields.One2many('onboarding.employee.fields.document', 'onboarding_task',
                                                    string="Section employee", )
    employee_fields_uploads_ids = fields.One2many('onboarding.employee.fields.upload', 'onboarding_task',
                                                  string="Section employee", )
    subject = fields.Char("Subject")
    email_to_ids = fields.Many2many('res.partner', string='To', domain=lambda self: [("email", "<>", '')])
    new_user_ids = fields.Many2many('res.users', string='New employee')

    is_onboarder = fields.Boolean(string="Onboarder", default=False)
    subordinate_id = fields.Many2one("hr.employee", string="Subordinate")
    embed_code = fields.Text('Embed Code', readonly=True, compute='_compute_task_embed_code')
    is_youtube = fields.Boolean('Is youtube', compute='_compute_task_embed_code')

    @api.depends('url')
    def _compute_task_embed_code(self):
        self.is_youtube = False
        self.embed_code = False
        if self.url:
            youtube_url = '//www.youtube.com/embed/%s?theme=light'
            url_obj = urls.url_parse(self.url)
            if url_obj.ascii_host == 'youtu.be':
                document_id = url_obj.path[1:] if url_obj.path else False
                self.embed_code = youtube_url % (document_id)
                self.is_youtube = True
            elif url_obj.ascii_host in ('youtube.com', 'www.youtube.com', 'm.youtube.com'):
                document_id = url_obj.decode_query().get('v')
                if document_id:
                    self.embed_code = youtube_url % (document_id)
                    self.is_youtube = True
                split_path = url_obj.path.split('/')
                if len(split_path) >= 3 and split_path[1] in ('v', 'embed'):
                    document_id = split_path[2]
                    self.embed_code = youtube_url % (document_id)
                    self.is_youtube = True

    def get_all_new_employee(self):
        user_ids = [user_id.id for user_id in self.new_user_ids]
        return self.env['hr.employee'].search([('user_id', 'in', user_ids)])

    def send_task_email(self):
        self.ensure_one()
        template = self.env.ref('ooto_onboarding.onboarding_task_email', raise_if_not_found=False)
        list_email_to = ""
        if self.email_to_ids:
            for receipt in self.email_to_ids:
                list_email_to = list_email_to + receipt.email + ","
        template.sudo().send_mail(self.id, email_values={'subject': self.subject,
                                                         'email_to': list_email_to[:len(list_email_to) - 1],
                                                         'email_from': self.env.user.email or ''}, force_send=True)

    @api.constrains('delay')
    def _check_task_delay(self):
        if self.to_do_for == 'after_x_month' and self.delay <= 0:
            raise ValidationError(_("Task %s : Set delay field (month number)") % self.name)

    def _calculate_date_end(self, task_id, hiring_date, emp_arrival_date):
        date_end = False
        date_end_char = False
        if task_id.to_do_for == "day_arrival":
            date_end = hiring_date if hiring_date else False
            date_end_char = str(date_end)
        elif task_id.to_do_for == "x_day_before" and task_id.arrival_x > 0:
            date_end = emp_arrival_date - relativedelta(days=task_id.arrival_x)
            date_end = datetime.datetime.combine(date_end, datetime.time())
            date_end_char = str(date_end)
        elif task_id.to_do_for == "x_day_after" and task_id.arrival_x > 0:
            date_end = emp_arrival_date + relativedelta(days=task_id.arrival_x)
            date_end = datetime.datetime.combine(date_end, datetime.time())
            date_end_char = str(date_end)
        elif task_id.to_do_for == "first_week":
            date_end = emp_arrival_date + relativedelta(days=7)
            date_end = datetime.datetime.combine(date_end, datetime.time())
            date_end_char = str(date_end)
        elif task_id.to_do_for == "first_month":
            date_end = emp_arrival_date + relativedelta(months=1)
            date_end = datetime.datetime.combine(date_end, datetime.time())
            date_end_char = str(date_end)
        elif task_id.to_do_for == "before_x_month" and task_id.arrival_x > 0:
            date_end = emp_arrival_date + relativedelta(months=task_id.arrival_x)
            date_end = datetime.datetime.combine(date_end, datetime.time())
            date_end_char = str(date_end)
        elif task_id.to_do_for == "after_x_month" and task_id.arrival_x > 0 and task_id.delay > 0:
            starting_period = emp_arrival_date + relativedelta(
                months=task_id.arrival_x)
            date_end = starting_period + relativedelta(months=task_id.delay)
            date_end = datetime.datetime.combine(date_end, datetime.time())
            date_end_char = str(date_end)

        return {'date_end': date_end, 'date_end_char': date_end_char}

    @api.depends("employee_ids.hiring_date", "period", "to_do_for", "arrival_x", "task_type", "date_start",
                 "subordinate_id.hiring_date")
    def _compute_date_end(self):
        for rec in self:
            date_end = False
            date_end_char = False
            if rec.onboarding_id.employee_id.hiring_date:
                hiring_date = datetime.datetime.combine(rec.onboarding_id.employee_id.hiring_date, datetime.time())
                if rec.is_onboarder and rec.subordinate_id.hiring_date:
                    subordinate_arrival_date = datetime.datetime.combine(rec.subordinate_id.hiring_date,
                                                                         datetime.time())
                    list_date_end = self._calculate_date_end(rec.parent_id, subordinate_arrival_date,
                                                             rec.subordinate_id.hiring_date)
                    date_end = list_date_end.get('date_end')
                    date_end_char = list_date_end.get('date_end_char')
                else:
                    if rec.task_type != 'appointment':
                        list_date_end = self._calculate_date_end(rec, arrival_date,
                                                                 rec.onboarding_id.employee_id.hiring_date)
                        date_end = list_date_end.get('date_end')
                        date_end_char = list_date_end.get('date_end_char')
                    elif rec.task_type == 'appointment':
                        calendar = self.env['calendar.event'].sudo().search(
                            [('appointment_task_id', '=', rec.parent_id.id)])
                        if calendar:
                            date_end = calendar[0].stop
                            if date_end:
                                c = r"[+].*"
                                str_dt = str(fields.Datetime.context_timestamp(self, date_end))
                                dt_end_str = re.sub(c, r"", str_dt)
                                date_end_char = dt_end_str
                        else:
                            date_end = False
                            date_end_char = False
                    else:
                        rec.date_end = False
            rec.date_end = date_end
            rec.date_end_char = date_end_char

    @api.onchange
    def _on_sign_template_change(self):
        if self.sign_template_id and (self.parent_id or self.is_from_onboarding):
            self.url = '/sign/%s' % self.sign_template_id.share_link

    @api.depends('date_end')
    def _compute_late_days(self):
        for rec in self:
            late_days = 0
            if rec.date_end:
                today_date = fields.Date.from_string(fields.Date.today())
                task_end_date = fields.Datetime.from_string(rec.date_end).date()
                if task_end_date < today_date:
                    late_days = (today_date - task_end_date).days
            rec.late_days = late_days

    def _compute_onboarding(self):
        for rec in self:
            onboarding_ids = self.env['hr.onboarding'].search(
                ['|', ('task_ids', 'in', rec.id), ('task_ids', 'in', rec.child_ids.ids)])
            rec.onboarding_ids = [(6, 0, onboarding_ids.ids)]
            rec.onboarding_count = len(onboarding_ids)

    def open_onboarding(self):
        self.ensure_one()
        result = {
            'name': _("Administrative list"),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.onboarding',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'domain': [('id', 'in', self.onboarding_ids.ids)],
        }
        return result

    def on_state_change(self):
        if self.onboarding_id:
            message = ''
            if self.task_state == 'to_do' and not self.status_to_do:
                message = _("{employee_name} is in the process of learning {task_type} {task_name} task").format(
                    employee_name=self.onboarding_id.employee_id.name,
                    task_type=self.stain_label,
                    task_name=self.name)
                self.sudo().write({'status_to_do': True})
            elif self.task_state == 'late' and not self.status_late:
                message = _("{employee_name}  is late compared to {task_type} {task_name} task").format(
                    employee_name=self.onboarding_id.employee_id.name,
                    task_type=self.stain_label,
                    task_name=self.name)
                self.sudo().write({'status_late': True})
            elif self.task_state == 'terminated' and not self.status_terminated:
                message = _("{employee_name} finished reading {task_type} {task_name}").format(
                    employee_name=self.onboarding_id.employee_id.name,
                    task_type=self.stain_label,
                    task_name=self.name)
                if self.date_end and self.date_end > datetime.datetime.now():
                    self.sudo().write({'finished_in_time': True})
                self.sudo().write({'status_terminated': True})
            if message:
                if isinstance(self.id, int) and self.id > 0:
                    message = self.message_post(body=message, message_type='notification')
                    message.write({"onboarding_id": self.onboarding_id.id, "state_task": self.task_state})
            if self.task_state in ['terminated', 'done']:
                self.sudo().update_reminder_notif_state()

    def update_reminder_notif_state(self):
        reminder_notif_obj = self.env['task.reminder.notif']
        notifs = reminder_notif_obj.search([('task_id', '=', self.id), ('is_done', '=', False)])
        if notifs:
            notifs.write({'is_done': True})

    @api.depends('parent_id', 'child_ids', 'is_from_onboarding', 'is_terminated_validator',
                 'date_end', 'publication_state', 'survey_id.is_filled', 'is_survey_filled')
    def _compute_task_state(self):
        for rec in self:
            active_state = rec.task_state
            if rec.task_type == 'form' and rec.survey_id and rec.survey_id.is_filled == True and rec.is_survey_filled == True:
                rec.is_terminated_validator = True
                rec.task_state = 'terminated'
                rec.is_survey = False
                rec.state_late = False
            if rec.date_end:
                date_end = time.mktime(rec.date_end.timetuple())
                current_date = time.mktime(datetime.datetime.utcnow().timetuple())
            if rec.parent_id or rec.is_from_onboarding or rec._context.get('is_create_child_task'):
                if rec.task_type == 'appointment' and rec.date_end and rec.date_end < fields.Datetime.now():
                    rec.task_state = 'done'
                    rec.state_late = False
                elif rec.task_type == 'appointment':
                    rec.task_state = 'to_do'
                    rec.state_late = False
                elif rec.is_terminated_validator:
                    rec.task_state = 'terminated'
                    rec.state_late = False
                elif rec.task_type == 'signature' and rec.sign_request_id and rec.sign_request_id.state == 'signed':
                    rec.task_state = 'terminated'
                    rec.state_late = False
                elif rec.date_end and fields.Datetime.now() - timedelta(
                        minutes=1440) > rec.date_end and rec.task_type != 'advice':
                    rec.task_state = 'late'
                    rec.state_late = True
                else:
                    rec.task_state = 'to_do'
                    rec.state_late = False
            elif rec.publication_state in ['published', 'unpublished']:
                rec.task_state = rec.publication_state
                rec.state_late = False
            else:
                rec.task_state = 'draft'
                rec.state_late = False
            if active_state != rec.task_state:
                rec.on_state_change()

    @api.model
    def create(self, values):
        res = super(HrOnboardingTask, self.with_context(mail_create_nolog=True)).create(values)
        if res.task_recall_ids:
            res.update_reminder_notifications()
        employe_id = request.env['hr.employee'].search([('user_id', '=', request.session.uid)])
        if res.is_from_onboarding:
            res.write({
                'employee_domain': [['id', '=', res.id]]
            })
            # Post message that a task is create
            message = _('{author} created a new task {task_name}').format(author=employe_id.name, task_name=res.name)
            mail_message = res.message_post(body=message, message_type='notification')
            mail_message.write({"onboarding_id": self.onboarding_id.id})
        else:
            domain = safe_eval(res.employee_domain)
            employee_ids = self.env['hr.employee'].search(domain).ids
            res.employee_ids = [(6, 0, employee_ids)]

        # Write hr.onboarding when create child task from kanban or list
        if res._context.get('is_create_child_task'):
            hr_onboarding = self.env['hr.onboarding'].browse(self.env.context.get('onboarding_id'))
            res.write({'onboarding_id': hr_onboarding.id})

        return res

    # @api.onchange('is_onboarder')
    # def onchange_is_onboarder(self):
    #     if self.is_onboarder:
    #         self.write({
    #             'to_do_for': 'specific',
    #             'period': 'specific',
    #         })
    #     else:
    #         self.write({
    #             'to_do_for': '',
    #             'period': '',
    #         })

    def write(self, values):
        res = super(HrOnboardingTask, self).write(values)
        if values.get('task_recall_ids', False):
            self.update_reminder_notifications()
        if values.get('employee_domain', False) and not self.is_from_onboarding:
            domain = safe_eval(self.employee_domain)
            employee_ids = self.env['hr.employee'].search(domain).ids
            self.employee_ids = [(6, 0, employee_ids)]
        for _field in no_write_fields:
            if _field in values:
                del values[_field]
        for child in self.mapped('child_ids'):
            child.write(values)
        return res

    def update_reminder_notifications(self):
        reminder_notif_obj = self.env['task.reminder.notif']
        for rec in self:
            if rec.onboarding_id:
                notifs = reminder_notif_obj.sudo().search([('task_id', '=', rec.id)])
                for alarm in rec.task_recall_ids:
                    reminder_notif = notifs.filtered(lambda l: l.alarm_id.id == alarm.id)
                    if not reminder_notif:
                        reminder_notif_obj.sudo().create({'task_id': rec.id, 'alarm_id': alarm.id})
                notifs.filtered(lambda l: l.alarm_id.id not in rec.task_recall_ids.ids).sudo().unlink()

    @api.model
    def create_sign_request(self, onboarding, task):
        template_id = task.sign_template_id.id
        employee_role = self.env.ref('sign.sign_item_role_employee', raise_if_not_found=False)
        partner_id = onboarding.employee_id.user_id and onboarding.employee_id.user_id.partner_id.id or False
        signers = [{'partner_id': partner_id, 'role': employee_role.id}]
        reference = "%s - %s" % (task.sign_template_id.name, onboarding.employee_id.name)
        sign_request = self.env['sign.request'].create({'template_id': template_id, 'reference': reference})
        sign_request.set_signers(signers)
        task.write({'sign_request_id': sign_request.id})
        if sign_request.request_item_ids:
            sign_request.request_item_ids.action_sent()
            task.write(
                {'url': '/sign/document/%s/%s' % (sign_request.id, sign_request.request_item_ids[0].access_token)})

    @api.depends('to_do_for', 'arrival_x')
    def _compute_period_task(self):
        """
        calculate the period thanks to the selection "to do for" and its duration if there is any
        :return: period of task
        """
        for rec in self:
            if not rec.to_do_for:
                rec.period = ''
                rec.period_display = ''
            elif rec.to_do_for == 'day_arrival':
                rec.period = 'arrival_day'
                rec.period_display = '2arrival_day'
                rec.order_seq = 1
            elif rec.to_do_for == 'x_day_before':
                rec.period = 'before_arrival'
                rec.period_display = '1before_arrival'
                rec.order_seq = 0
            elif rec.to_do_for in ['first_week'] or (rec.to_do_for == 'x_day_after' and rec.arrival_x <= 7):
                rec.period = 'first_week'
                rec.period_display = '3first_week'
                rec.order_seq = 2
            elif rec.to_do_for == 'first_month' or (rec.to_do_for == 'before_x_month' and rec.arrival_x <= 1) or (
                    rec.to_do_for == 'x_day_after' and rec.arrival_x <= 28):
                rec.period = 'first_month'
                rec.period_display = '4first_month'
                rec.order_seq = 3
            elif rec.to_do_for == 'specific':
                rec.period = 'specific'
                rec.period_display = '6specific'
                rec.order_seq = 5
            else:
                rec.order_seq = 4
                rec.period = 'after_first_month'
                rec.period_display = '5after_first_month'

    @api.onchange('content_type')
    def onchange_content_type(self):
        self.timer_check = self.scroll_check = self.timer = False
        self.url = self.page_id = self.image_task = self.support = False

    @api.onchange('task_type')
    def onchange_task_type(self):
        self.content_type = False
        self.onchange_content_type()

    @api.depends('task_type')
    def compute_stain_label(self):
        for rec in self:
            task_type = dict(rec._fields['task_type'].selection).get(rec.task_type)
            rec.write({'stain_label': task_type})

    # @api.onchange('employee_domain')
    # def onchange_employee_domain(self):
    #     domain = safe_eval(self.employee_domain)
    #     employee_ids = self.env['hr.employee'].search(domain).ids
    #     self.employee_ids = [(6, 0, employee_ids)]

    @api.onchange('arrival_x')
    def onchange_arrival_x(self):
        if self.arrival_x <= 0:
            self.arrival_x = 1
            raise exceptions.ValidationError(_("The value of arrival x must be positve and greater than 0"))

    @api.onchange('period')
    def onchange_period(self):
        if self.period and self.task_type == 'form' and self.survey_id:
            self.survey_id.write({'period': self.period})

    @api.onchange('survey_id', 'period')
    def onchange_survey(self):
        if self.period and self.survey_id:
            self.survey_id.write({'period': self.period, 'task_belong': True})

    def create_new_event(self):
        values = {
            'name': " ".join([self.name, self.period]),
            'allday': True,
            'start': self.date_end,
            'stop': self.date_end,
            'task_id': self.id,
        }
        self.env['calendar.event'].create(values)

    def action_unpublish_task(self):
        self.ensure_one()
        self.write({'publication_state': 'unpublished'})

    def action_publish_task_onboarder(self, employee_id):
        self.ensure_one()
        employee_ids = [emp_id for emp_id in self.employee_ids if
                        emp_id == employee_id.parent_id or
                        emp_id in employee_id.deputy_ids or
                        emp_id == employee_id.quality_responsible_id or
                        emp_id == employee_id.admin_responsible_id or
                        emp_id == employee_id.software_responsible_id or
                        emp_id == employee_id.gpec_responsible_id]
        for emp_id in employee_ids:
            if employee_id != emp_id:
                onboarding_id = self.env['hr.onboarding'].search([('employee_id', '=', emp_id.id)])

                in_email_task = False
                in_task = False

                task_ids = onboarding_id.task_ids

                if self.task_type == 'email':
                    # get tasks type email
                    task_ids = onboarding_id.task_ids.filtered(
                        lambda t: t.task_type == 'email' and t.task_state != 'terminated')
                    # verify if employee is already in task email if not then create task email for manager
                    for task_id in task_ids:
                        if employee_id.user_id in task_id.new_user_ids:
                            in_email_task = True
                            break
                        else:
                            continue
                else:
                    for task_id in task_ids:
                        if task_id.parent_id == self and employee_id == task_id.subordinate_id:
                            in_task = True
                            break
                        else:
                            continue

                if not in_email_task and not in_task:
                    if onboarding_id and emp_id.arrival_date and emp_id in self.employee_ids:
                        today = fields.Date.today()
                        period = ''
                        period_display = ''
                        to_do_for = ''
                        # arrival_date = datetime.datetime.combine(employee_id.arrival_date, datetime.time())
                        arrival_date = emp_id.hiring_date
                        # dt_start = fields.Datetime.context_timestamp(self, self.date_start)
                        # get manager period
                        if arrival_date:
                            if arrival_date == today:
                                period = 'arrival_day'
                                period_display = '2arrival_day'
                                to_do_for = 'day_arrival'
                            elif arrival_date > today:
                                period = 'before_arrival'
                                period_display = '1before_arrival'
                                to_do_for = 'x_day_before'
                            elif today > arrival_date > today - relativedelta(days=7):
                                period = 'first_week'
                                period_display = '3first_week'
                                to_do_for = 'first_week'
                            elif today > arrival_date > today - relativedelta(months=1):
                                period = 'first_month'
                                period_display = '4first_month'
                                to_do_for = 'first_month'
                            else:
                                period = 'after_first_month'
                                period_display = '5after_first_month'
                                to_do_for = 'after_x_month'

                        default = {
                            'subordinate_id': employee_id.id,
                            'period': period,
                            'parent_id': self.id,
                            'onboarding_id': onboarding_id.id,
                            'is_terminated_validator': False,
                            'description': employee_id.name + ' : ' + self.description if self.task_type != 'email' else self.description,
                            'is_onboarder': True,
                            'support': self.support,
                        }

                        new_task = self.with_context(no_sign_request=True).copy(default)
                        emp_fields_document_parent = self.env['onboarding.employee.fields.document'].search(
                            [('onboarding_task.id', '=', self.id)])

                        emp_fields_upload_parent = self.env['onboarding.employee.fields.upload'].search(
                            [('onboarding_task.id', '=', self.id)])
                        if not new_task.is_retroactive and new_task.to_do_for == 'after_x_month' and new_task.task_state == 'late':
                            new_task.unlink()
                        else:
                            emp = new_task.onboarding_id.employee_id
                            new_task.write({'period': period, 'period_display': period_display, 'to_do_for': to_do_for})
                            if emp_fields_document_parent:
                                for parent_field in emp_fields_document_parent:
                                    if parent_field:
                                        parent_field.copy({
                                            'fields_id': parent_field.fields_id.id,
                                            'onboarding_task': new_task.id,
                                            'employee_ids': [(4, emp.id, 0)],
                                        })
                            elif emp_fields_upload_parent:
                                for parent_field in emp_fields_upload_parent:
                                    if parent_field:
                                        parent_field.copy({
                                            'fields_id': parent_field.fields_id.id,
                                            'onboarding_task': new_task.id,
                                            'employee_ids': [(4, emp.id, 0)],
                                        })

                            if new_task.task_type == 'signature' and new_task.sign_template_id and not new_task.sign_request_id:
                                new_task.create_sign_request(onboarding_id, new_task)

        employe_id = request.env['hr.employee'].search([('user_id', '=', request.session.uid)])
        # Post message that a task is create
        message = '{author} created a new task {task_name}'.format(author=employe_id.name, task_name=self.name)
        mail_message = self.message_post(body=message, message_type='notification')
        mail_message.create({"onboarding_id": self.onboarding_id.id})
        self.write({'publication_state': 'published'})

    def action_publish_task(self, employee_ids=None):
        """
        Action to generate the spots in each onboarding selected with the filter
        :return: add task in onboarding
        """
        self.ensure_one()
        employee_ids = employee_ids if employee_ids and type(employee_ids) is not dict else self.employee_ids
        onboarding_ids = self.env['hr.onboarding'].search([('employee_id', 'in', employee_ids.mapped('id'))])

        if self.task_type == 'appointment':
            for employee_id in employee_ids:
                if employee_id.hiring_date:
                    period = ''
                    period_display = ''
                    to_do_for = ''
                    # arrival_date = datetime.datetime.combine(employee_id.arrival_date, datetime.time())
                    arrival_date = employee_id.hiring_date
                    dt_start = fields.Datetime.context_timestamp(self, self.date_start)
                    # get employee period
                    if arrival_date:
                        if arrival_date == dt_start.date():
                            period = 'arrival_day'
                            period_display = '2arrival_day'
                            to_do_for = 'day_arrival'
                        elif arrival_date > dt_start.date():
                            period = 'before_arrival'
                            period_display = '1before_arrival'
                            to_do_for = 'x_day_before'
                        elif dt_start.date() > arrival_date > dt_start.date() - relativedelta(days=7):
                            period = 'first_week'
                            period_display = '3first_week'
                            to_do_for = 'first_week'
                        elif dt_start.date() > arrival_date > dt_start.date() - relativedelta(months=1):
                            period = 'first_month'
                            period_display = '4first_month'
                            to_do_for = 'first_month'
                        else:
                            period = 'after_first_month'
                            period_display = '5after_first_month'
                            to_do_for = 'after_x_month'
                    # check if employee has onboarding
                    onboarding_id = onboarding_ids.filtered(lambda e: e.employee_id == employee_id)
                    if not onboarding_id:
                        onboarding_id = self.env['hr.onboarding'].create({
                            'employee_id': employee_id.id
                        })
                    default = {
                        'period': period,
                        'parent_id': self.id,
                        'onboarding_id': onboarding_id.id,
                    }
                    new_task = self.with_context(no_sign_request=True).copy(default)
                    if not new_task.is_retroactive and new_task.to_do_for == 'after_x_month' and new_task.task_state == 'late':
                        new_task.unlink()
                    else:
                        new_task.write({'period': period, 'period_display': period_display, 'to_do_for': to_do_for})
                        if new_task.task_type == 'signature' and new_task.sign_template_id and not new_task.sign_request_id:
                            new_task.create_sign_request(onboarding_id, new_task)
        else:
            emp_fields_document_parent = self.env['onboarding.employee.fields.document'].search(
                [('onboarding_task.id', '=', self.id)])

            emp_fields_upload_parent = self.env['onboarding.employee.fields.upload'].search(
                [('onboarding_task.id', '=', self.id)])

            if not self.is_retroactive:
                list_period = order_period[:order_period.index(self.period) + 1]
                employee_ids = employee_ids.filtered(lambda e: e.period in list_period)
                onboarding_ids = self.env['hr.onboarding'].search([('employee_id', 'in', employee_ids.mapped('id'))])
            for onboarding in onboarding_ids:
                new_task = self.with_context(no_sign_request=True).copy({
                    'parent_id': self.id,
                    'onboarding_id': onboarding.id,
                    'is_terminated_validator': False,
                })
                if not new_task.is_retroactive and new_task.to_do_for == 'after_x_month' and new_task.task_state == 'late':
                    new_task.unlink()
                else:
                    emp = new_task.onboarding_id.employee_id
                    # Create dynamic fields for child
                    if emp_fields_document_parent:
                        for parent_field in emp_fields_document_parent:
                            if parent_field:
                                parent_field.copy({
                                    'fields_id': parent_field.fields_id.id,
                                    'onboarding_task': new_task.id,
                                    'employee_ids': [(4, emp.id, 0)],
                                })
                    elif emp_fields_upload_parent:
                        for parent_field in emp_fields_upload_parent:
                            if parent_field:
                                parent_field.copy({
                                    'fields_id': parent_field.fields_id.id,
                                    'onboarding_task': new_task.id,
                                    'employee_ids': [(4, emp.id, 0)],
                                })

                    if new_task.task_type == 'signature' and new_task.sign_template_id and not new_task.sign_request_id:
                        new_task.create_sign_request(onboarding, new_task)

        employe_id = request.env['hr.employee'].search([('user_id', '=', request.session.uid)])
        # Post message that a task is create
        message = '{author} created a new task {task_name}'.format(author=employe_id.name, task_name=self.name)
        mail_message = self.message_post(body=message, message_type='notification')
        mail_message.create({"onboarding_id": self.onboarding_id.id})
        self.write({'publication_state': 'published'})

    def action_valid_task(self):
        employe_id = request.env['hr.employee'].search([('user_id', '=', request.session.uid)])
        for rec in self:
            rec.is_terminated_validator = True
            # Find employee's onboarding and post message
            for onboarding in rec.onboarding_ids:
                if onboarding.employee_id and onboarding.employee_id in rec.employee_ids:
                    if onboarding.employee_id.name != employe_id.name:
                        message = _("{author} validated {task_name} the task of {employee_name}").format(
                            employee_name=onboarding.employee_id.name, author=employe_id.name, task_name=self.name)
                    else:
                        message = _("{author} validated his task {task_name}").format(
                            author=employe_id.name, task_name=self.name)
                    mail_message = rec.message_post(body=message, message_type='notification')
                    mail_message.write({"onboarding_id": onboarding.id})
            child_tasks = self.search([('parent_id', '=', rec.id), ('is_from_onboarding', '=', False)])
            if child_tasks:
                child_tasks.action_valid_task()

    def convert_date(self, date_end):
        dt_end = fields.Datetime.context_timestamp(self, date_end)
        return dt_end


class HrOnboardingTaskState(models.Model):
    _name = 'hr.task.state'
    _description = 'Hr tasks state'

    name = fields.Char("Name", required=True, transtale=True)
