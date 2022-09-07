# -*- coding: utf-8 -*-

import datetime

from odoo import models, _, fields, api, SUPERUSER_ID, sql_db, registry
from odoo.tools import config


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    onboarding_ids = fields.One2many("hr.onboarding", "employee_id", "On boarding", ondelete='cascade')
    # arrival_date = fields.Date("Arrival date")
    # leaving_date = fields.Date("Leaving date")
    admin_responsible_id = fields.Many2one("hr.employee", "Admin responsible")
    software_responsible_id = fields.Many2one("hr.employee", "software responsible")
    period = fields.Selection([
        ('arrival_day', _('Arrival day')),
        ('before_arrival', _('Before arrival')),
        ('first_week', _('First week')),
        ('first_month', _('First month')),
        ('after_first_month', _('After first month')),
    ], string="Period", compute="_compute_period_employee", store=True)
    responsible_ids = fields.One2many('hr.employee', compute='_compute_all_responsible_ids', string='Responsibles')
    date_sending_invitation = fields.Datetime('Date sending invitation mail')
    option = fields.Selection([
        ('send_notification', _('Send / schedule an invitation by email')),
        ('set_password', _('Set the password (without sending an email)')),
        ('send_email_onboarding', _('Send an email to the creation of onboarding')),
        ('do_nothing', _('Do Nothing')),
    ], 'Creation Option', default='do_nothing')
    is_invitation_send = fields.Boolean("Invitation Send")

    onb_emp_fields_document_ids = fields.Many2many('onboarding.employee.fields.document',
                                                   'employee_fields_document_onboarding_rel', 'emp_id',
                                                   'onb_emp_fields_id')

    onb_emp_fields_upload_ids = fields.Many2many('onboarding.employee.fields.upload',
                                                 'employee_fields_uploads_onboarding_rel', 'emp_id',
                                                 'onb_emp_fields_id')
    category_ids = fields.Many2many(
        'hr.employee.category', 'employee_category_rel',
        'emp_id', 'category_id', groups="hr.group_hr_manager",
        string='Tags')
    job_id = fields.Many2one(groups="hr.group_hr_user, ooto_onboarding.group_ooto_onboarding_user")
    address_home_id = fields.Many2one(groups="hr.group_hr_user, ooto_onboarding.group_ooto_onboarding_user")
    private_email = fields.Char(groups="hr.group_hr_user, ooto_onboarding.group_ooto_onboarding_user")
    country_id = fields.Many2one(groups="hr.group_hr_user, ooto_onboarding.group_ooto_onboarding_user")
    gender = fields.Selection(groups="hr.group_hr_user, ooto_onboarding.group_ooto_onboarding_user")
    marital = fields.Selection(groups="hr.group_hr_user, ooto_onboarding.group_ooto_onboarding_user")
    spouse_complete_name = fields.Char(groups="hr.group_hr_user, ooto_onboarding.group_ooto_onboarding_user")
    spouse_birthdate = fields.Date(groups="hr.group_hr_user, ooto_onboarding.group_ooto_onboarding_user")
    children = fields.Integer(groups="hr.group_hr_user, ooto_onboarding.group_ooto_onboarding_user")
    place_of_birth = fields.Char(groups="hr.group_hr_user, ooto_onboarding.group_ooto_onboarding_user")
    country_of_birth = fields.Many2one(groups="hr.group_hr_user, ooto_onboarding.group_ooto_onboarding_user")
    birthday = fields.Date(groups="hr.group_hr_user, ooto_onboarding.group_ooto_onboarding_user")
    ssnid = fields.Char(groups="hr.group_hr_user, ooto_onboarding.group_ooto_onboarding_user")
    sinid = fields.Char(groups="hr.group_hr_user, ooto_onboarding.group_ooto_onboarding_user")
    identification_id = fields.Char(groups="hr.group_hr_user, ooto_onboarding.group_ooto_onboarding_user")
    passport_id = fields.Char(groups="hr.group_hr_user, ooto_onboarding.group_ooto_onboarding_user")
    bank_account_id = fields.Many2one(groups="hr.group_hr_user, ooto_onboarding.group_ooto_onboarding_user")
    permit_no = fields.Char(groups="hr.group_hr_user, ooto_onboarding.group_ooto_onboarding_user")
    visa_no = fields.Char(groups="hr.group_hr_user, ooto_onboarding.group_ooto_onboarding_user")
    visa_expire = fields.Date(groups="hr.group_hr_user, ooto_onboarding.group_ooto_onboarding_user")
    additional_note = fields.Text(groups="hr.group_hr_user, ooto_onboarding.group_ooto_onboarding_user")
    certificate = fields.Selection(groups="hr.group_hr_user, ooto_onboarding.group_ooto_onboarding_user",
                                   translate=True)
    study_field = fields.Char(groups="hr.group_hr_user, ooto_onboarding.group_ooto_onboarding_user")
    study_school = fields.Char(groups="hr.group_hr_user, ooto_onboarding.group_ooto_onboarding_user")
    emergency_contact = fields.Char(groups="hr.group_hr_user, ooto_onboarding.group_ooto_onboarding_user")
    emergency_phone = fields.Char(groups="hr.group_hr_user, ooto_onboarding.group_ooto_onboarding_user")
    km_home_work = fields.Integer(groups="hr.group_hr_user, ooto_onboarding.group_ooto_onboarding_user")

    phone = fields.Char(groups="hr.group_hr_user, ooto_onboarding.group_ooto_onboarding_user")
    # misc
    notes = fields.Text(groups="hr.group_hr_user, ooto_onboarding.group_ooto_onboarding_user")
    color = fields.Integer(groups="hr.group_hr_user, ooto_onboarding.group_ooto_onboarding_user")
    barcode = fields.Char(groups="hr.group_hr_user, ooto_onboarding.group_ooto_onboarding_user")
    pin = fields.Char(groups="hr.group_hr_user, ooto_onboarding.group_ooto_onboarding_user")
    departure_reason = fields.Selection(groups="hr.group_hr_user, ooto_onboarding.group_ooto_onboarding_user")
    departure_description = fields.Text(groups="hr.group_hr_user, ooto_onboarding.group_ooto_onboarding_user")

    is_new_employee = fields.Boolean(string="is a new employee ?", default=True)

    is_resp_admin = fields.Boolean(string="is responsable administrative", compute="_compute_is_responsible",
                                   store=True)
    is_resp_soft = fields.Boolean(string="is responsable software", compute="_compute_is_responsible", store=True)

    @api.depends('parent_id', 'quality_responsible_id', 'gpec_responsible_id', 'admin_responsible_id',
                 'software_responsible_id')
    def _compute_is_responsible(self):
        employee_ids = self.env['hr.employee'].search([])
        manager_ids = employee_ids.mapped('parent_id')
        quality_ids = employee_ids.mapped('quality_responsible_id')
        admin_ids = employee_ids.mapped('admin_responsible_id')
        soft_ids = employee_ids.mapped('software_responsible_id')
        gpec_ids = employee_ids.mapped('gpec_responsible_id')
        not_responsible_ids = employee_ids - manager_ids - quality_ids - admin_ids - soft_ids - gpec_ids

        for manager_id in manager_ids:
            manager_id.is_manager = True
        for quality_id in quality_ids:
            quality_id.is_quality_responsible = True
        for admin_id in admin_ids:
            admin_id.is_resp_admin = True
        for soft_id in soft_ids:
            soft_id.is_resp_soft = True
        for gpec_id in gpec_ids:
            gpec_id.is_gpec_responsible = True

        for not_resp_id in not_responsible_ids:
            not_resp_id.is_manager = False
            not_resp_id.is_quality_responsible = False
            not_resp_id.is_resp_admin = False
            not_resp_id.is_resp_soft = False
            not_resp_id.is_gpec_responsible = False

    def change_is_new_employee(self):
        """
        Action change is new employee multiple employees
        :return:
        """
        for rec in self:
            rec.is_new_employee = False if rec.is_new_employee else True

    @api.model
    def create(self, values):
        """
        Add creation cron to send mail invitation for the user if employee have date_sending_invitation field
        :param values: values of create
        :return: return creation hr employee
        """
        emp = super(HrEmployee, self).create(values)
        if emp.date_sending_invitation and emp.user_id:
            emp.create_cron_mail_invitation()
        return emp

    def create_cron_mail_invitation(self):
        """
        Planned action for sending the user invitation email
        :return: creation cron
        """
        values = {
            "name": "Send email invitation for :  %s" % self.work_email,
            "model_id": self.env.ref('hr.model_hr_employee').id,
            "state": "code",
            "nextcall": self.date_sending_invitation,
            "code": "model.send_mail_invitation_template(%s)" % self.id
            # "code": "model.send_mail_invitation(%s)" % self.id
        }
        self.env['ir.cron'].sudo().create(values)

    @api.model
    def send_mail_invitation(self, emp_id):
        """
        Find the user link to the employee.
        Search for login to call the native action_reset_password
        method with the context create_user to send the invitation email
        :param emp_id: employee id
        :return: action_reset_password
        """
        user_db = self.browse(emp_id).user_id
        # user_db.sudo().write({'not_send_mail': False})
        login = user_db.login
        user = self.env['res.users'].search([('login', '=', login)])
        if user:
            user.sudo().write({'not_send_mail': False})
            user.with_context(create_user=True).sudo().action_reset_password()

    @api.model
    def send_mail_invitation_template(self, emp_id):
        employee_id = self.browse(emp_id)
        user = employee_id.user_id
        template_id = self.env['mail.template'].search([('user_onboarding_id', '=', user.id)],
                                                       order='create_date DESC', limit=1)
        if not template_id:
            template_id = self.env.ref('ooto_onboarding.set_password_email_ooto', raise_if_not_found=False)
        if template_id:
            template_values = {
                'email_to': '${object.email|safe}',
                'email_cc': False,
                'auto_delete': True,
                'partner_to': False,
                'scheduled_date': False,
            }
            template_id.write(template_values)
            mail = template_id.with_context(lang=user.lang).send_mail(user.id, force_send=True, raise_exception=True)
            if mail:
                employee_id.is_invitation_send = True
                template_ids = self.env['mail.template'].search([('user_onboarding_id', '=', user.id)])
                if template_ids:
                    template_ids.active = False

    def action_invitation_send(self):
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        user_id = self.env['res.users'].search([('login', '=', self.user_id.login)])
        if not user_id.partner_id.signup_valid:
            user_id.partner_id.signup_prepare(signup_type="reset", expiration=False)
        template_ids = self.env['mail.template'].search([('user_onboarding_id', '=', self.user_id.id)])
        template = self.env['mail.template'].search([('user_onboarding_id', '=', self.user_id.id)],
                                                    order='create_date DESC', limit=1)
        if template_ids:
            template_ids.active = False
        if template:
            template_id = template
        else:
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
        emp = self.env['hr.employee'].search([('work_email', '=', self.user_id.login)])
        ctx = {
            'default_model': 'res.users',
            'default_res_id': self.user_id.id,
            'default_use_template': bool(template_id),
            'default_template_id': template_id.id,
            'default_partner_ids': [(4, self.user_id.partner_id.id)],
            'default_user_onboarding_id': self.user_id.id if emp.option == 'send_notification' else False,
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

    @api.depends('parent_id', 'coach_id', 'admin_responsible_id', 'software_responsible_id')
    def _compute_all_responsible_ids(self):
        """
        Compute all user responsible
        :param self:
        :return:
        """
        for rec in self:
            all_responsible = [rec.parent_id, rec.coach_id, rec.admin_responsible_id, rec.software_responsible_id]
            resp_ids = [resp.id for resp in all_responsible if resp]
            rec.responsible_ids = [(6, 0, resp_ids)]

    @api.depends('hiring_date')
    def _compute_period_employee(self):
        for rec in self:
            now = datetime.datetime.now().date()
            rec.period = False
            if rec.hiring_date:
                if rec.hiring_date == now:
                    rec.period = 'arrival_day'
                elif rec.hiring_date > now:
                    rec.period = 'before_arrival'
                elif now >= rec.hiring_date > now - datetime.timedelta(weeks=1):
                    rec.period = 'first_week'
                elif now > rec.hiring_date > now - datetime.timedelta(weeks=4):
                    rec.period = 'first_month'
                else:
                    rec.period = 'after_first_month'

    # @api.onchange('lastname', 'firstname')
    # def onchange_lastname_firstname(self):
    #     """
    #     Method to fill employee name by concatenating lastname and firstname
    #     :return: None
    #     """
    #     self.name = "%s %s" % (self.lastname, self.firstname)

    def unlink(self):
        """
        Method to delete user at first when deleting employee
        :return: None
        """
        for rec in self:
            for o in self.env['hr.onboarding'].sudo().search([('employee_id', '=', rec.id)]):
                o.sudo().unlink()
                # delete linked user
                rec.user_id.unlink()
            return super(HrEmployee, self).unlink()

    def open_onboarding_action(self):
        self.ensure_one()
        result = {
            'name': _("Onboarding"),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.onboarding',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.onboarding_ids[0].id
        }
        return result

    @api.model
    def create_employee_user(self, vals):
        res = super(HrEmployee, self).create_employee_user(vals)
        if vals.get('password', False):
            res.sudo().write({'password': vals.get('password')})
        return res

    def upload_file(self, input_name, file_name, file):
        employee_id = self.search([('user_id', '=', self.env.user.id)])
        employee_id.sudo().write({
            input_name: file,
            'x_filename_of_{}'.format(input_name): file_name
        })
        self.check_task_administrative()

    def check_task_administrative(self):
        employee = self.env.user.employee_id

        # fields_value = []
        binary_fields_value = []
        is_fields_filled = False

        all_task_admin = self.env['hr.onboarding.task'].search(
            [('parent_id', '=', False), ('task_type', '=', 'administrative')])
        for task in all_task_admin:
            fields_value = []
            if task and task.task_state != 'terminated':
                all_fields_document_onb = self.env['onboarding.employee.fields.document'].search(
                    [('onboarding_task', '=', task.id)])
                all_fields_upload_onb = self.env['onboarding.employee.fields.upload'].search(
                    [('onboarding_task', '=', task.id)])
                for field_doc_onb in all_fields_document_onb:
                    field = field_doc_onb.mapped('fields_id')
                    if field and field.ttype == "many2one":
                        name_field_many2one = field.name
                        if name_field_many2one != 'bank_account_id':
                            object = employee.mapped(name_field_many2one)
                            if object.name:
                                fields_value.append(object.name) if object.name else ' '
                        else:
                            object = employee.mapped(name_field_many2one)
                            if object.acc_number:
                                fields_value.append(object.acc_number) if object.acc_number else ' '
                            else:
                                fields_value.append(None)
                    # elif field and field.ttype == "binary":
                    # 	binary_fields_value.append(getattr(employee, field.name))
                    elif field and field.ttype not in ['many2one', 'boolean']:
                        fields_value.append(getattr(employee, field.name))

                for field_up_onb in all_fields_upload_onb:
                    field = field_up_onb.mapped('fields_id')
                    if field and field.ttype == "many2one":
                        name_field_many2one = field.name
                        if name_field_many2one != 'bank_account_id':
                            object = employee.mapped(name_field_many2one)
                            if object.name:
                                fields_value.append(object.name) if object.name else ' '
                        else:
                            object = employee.mapped(name_field_many2one)
                            if object.acc_number:
                                fields_value.append(object.acc_number) if object.acc_number else ' '
                            else:
                                fields_value.append(None)
                    # elif field and field.ttype == "binary":
                    # 	binary_fields_value.append(getattr(employee, field.name))
                    elif field and field.ttype not in ['many2one', 'boolean']:
                        fields_value.append(getattr(employee, field.name))

                # is_fields_filled = False if False or None in fields_value else True
                is_fields_filled = False if False in fields_value or None in fields_value else True
                # is_binary_fields_filled = False if False in binary_fields_value else True
                if is_fields_filled:
                    task.sudo().state_late = False
                    task.sudo().action_valid_task()
