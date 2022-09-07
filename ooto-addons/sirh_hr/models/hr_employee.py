# -*- coding: utf-8 -*-

import base64
import logging

from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class EmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    firstname_tmp = fields.Char("First name")
    lastname_tmp = fields.Char("Last name")
    cnaps_number = fields.Char(string="Cnaps number")
    deputy_ids = fields.Many2many('hr.employee', string='Deputy', compute='_compute_deputy_ids')
    # registration_number = fields.Char("Registration number")
    document_ids = fields.One2many('ir.attachment', compute='_compute_document_ids', string="Documents")
    documents_count = fields.Integer(compute='_compute_document_ids', string="Document Count")
    level_id = fields.Many2one('hr.level', string='Level', track_visibility='onchange')
    spinneret_id = fields.Many2one("hr.spinneret", "Spinneret", track_visibility='onchange')
    job_id = fields.Many2one('hr.job', 'Job Position',
                             domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                             track_visibility='onchange')
    # cin = fields.Char(string="CIN")
    # date_cin = fields.Date(string="CIN Deliver date")
    # place_cin = fields.Char(string="CIN Delver place")
    # duplicate_date = fields.Date(string='CIN duplicate date')
    job_name = fields.Char(related='job_id.name')
    default_company_ids = fields.Many2many('res.company', default=lambda self: self.env.user.company_ids)
    company_ids = fields.Many2many('res.company', compute='_compute_default_company_ids')
    hiring_date = fields.Date(string='Hiring date')
    departure_date = fields.Date(string='Departure date')
    children_ids = fields.One2many('hr.employee.children', 'employee_id', 'Children lines')
    children = fields.Integer(compute='_compute_children_number', store=True)
    certificate = fields.Selection(selection_add=[
        ('patent', _('Patent')),
        ('license', _('Licence')),
        ('master_2', _('Master 2')),
        ('engeneer', _('Engeneer')),
    ])
    resignation_notice_days = fields.Integer(
        string='Resignation notice days',
        compute='_compute_resignation_notice_days'
    )
    departure_notice_group = fields.Char(
        string='Departure notice group',
        compute='_compute_resignation_notice_days'
    )
    expatriate = fields.Boolean(string='Expatriate')
    parent_id = fields.Many2one(related="department_id.manager_id", readonly=True, store=True)

    @api.onchange('manager_id')
    def _compute_default_company_ids(self):
        self.company_ids = self.env.ref('base.main_company')

    @api.depends('company_id')
    def set_default_company_ids(self):
        return self.env.user.company_ids

    def _get_direction_id(self):
        return self.department_id.direction_id.id

    direction_id = fields.Many2one('hr.direction', string='Direction', default=_get_direction_id)
    executive_id = fields.Many2one('hr.employee', string='Executive',
                                   compute='_compute_executive_id')
    is_manager = fields.Boolean(string="is manager", compute="_compute_is_responsible", store=True)
    is_rrh = fields.Boolean(string="is rrh", related="department_id.is_rrh", store=True)
    quality_responsible_id = fields.Many2one('hr.employee', string='Quality responsible')
    is_quality_responsible = fields.Boolean(string="is quality responsible", compute="_compute_is_responsible",
                                            store=True)
    gpec_responsible_id = fields.Many2one('hr.employee', string='Gpec responsible')
    is_gpec_responsible = fields.Boolean(string="is gpec responsible", compute="_compute_is_responsible",
                                         store=True)

    @api.depends('parent_id', 'quality_responsible_id', 'gpec_responsible_id')
    def _compute_is_responsible(self):
        employee_ids = self.env['hr.employee'].search([])
        manager_ids = employee_ids.mapped('parent_id')
        quality_ids = employee_ids.mapped('quality_responsible_id')
        gpec_ids = employee_ids.mapped('gpec_responsible_id')
        not_responsible_ids = employee_ids - manager_ids - quality_ids - gpec_ids

        for manager_id in manager_ids:
            manager_id.is_manager = True
        for quality_id in quality_ids:
            quality_id.is_quality_responsible = True

        for not_responsible_id in not_responsible_ids:
            not_responsible_id.is_manager = False
            not_responsible_id.is_quality_responsible = False
            not_responsible_id.is_gpec_responsible = False

    def _compute_deputy_ids(self):
        for employee in self:
            employee.deputy_ids = employee.department_id.deputy_ids

    def _compute_executive_id(self):
        for employee in self:
            employee.executive_id = employee.sudo().direction_id.sudo().executive_id.id

    def action_open_job(self):
        view_id = self.env.ref('hr.view_hr_job_form').id
        context = self._context.copy()
        return {
            'name': 'hr.job.form',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(view_id, 'form')],
            'res_model': 'hr.job',
            'binding_view_types': view_id,
            'type': 'ir.actions.act_window',
            'res_id': self.job_id.id,
            'target': 'current',
            'context': context,
        }

    @api.onchange('department_id')
    def _onchange_department(self):
        self.deputy_ids = self.department_id.deputy_ids
        self.direction_id = self.department_id.direction_id.id
        self.executive_id = self.department_id.direction_id.executive_id.id
        # self.parent_duplicate_id = self.department_id.manager_id.id
        self.parent_id = self.department_id.manager_id.id

    @api.onchange('direction_id')
    def _onchange_direction_id(self):
        self.executive_id = self.direction_id.executive_id.id

    @api.model
    def create(self, values):
        if 'firstname_tmp' in values.keys() or 'lastname_tmp' in values.keys():
            values.update({
                'firstname': values.get('firstname_tmp'),
                'lastname': values.get('lastname_tmp'),
                'name': '{} {}'.format(values.get('lastname_tmp'), values.get('firstname_tmp'))
            })
        else:
            values.update({'firstname_tmp': values.get('firstname'), 'lastname_tmp': values.get('lastname')})
        res = super(EmployeeInherit, self).create(values)
        res.direction_id = res.department_id.direction_id.id
        res.executive_id = res.department_id.direction_id.executive_id.id
        return res

    def write(self, vals):
        """
        Set lastname_tmp and firstname_tmp
        :param vals:
        :return:
        """
        for rec in self:
            if 'lastname' in vals.keys() or 'firstname' in vals.keys():
                firstname = vals.get('firstname', rec.firstname_tmp)
                lastname = vals.get('lastname', rec.firstname_tmp)
                if rec.user_id:
                    rec.user_id.write({
                        'firstname': firstname,
                        'lastname': lastname,
                    })
                vals.update({
                    'firstname_tmp': firstname,
                    'lastname_tmp': lastname
                })
            elif 'firstname_tmp' in vals.keys() or 'lastname_tmp' in vals.keys():
                vals.update({
                    'name': '{} {}'.format(vals.get('lastname_tmp'), vals.get('firstname_tmp'))
                })
            return super(EmployeeInherit, rec).write(vals)

    def _compute_document_ids(self):
        attachments = self.env['ir.attachment'].search([
            '&', ('res_model', '=', 'hr.employee'), ('res_id', 'in', self.ids)])
        result = dict.fromkeys(self.ids, self.env['ir.attachment'])
        for attachment in attachments:
            result[attachment.res_id] |= attachment
        for employee in self:
            employee.document_ids = result[employee.id]
            employee.documents_count = len(employee.document_ids)

    def action_get_attachment_tree_view(self):
        action = self.env.ref('base.action_attachment').read()[0]
        action['context'] = {
            'default_res_model': self._name,
            'default_res_id': self.ids[0]
        }
        action['domain'] = ['&', ('res_model', '=', 'hr.employee'), ('res_id', 'in', self.ids)]
        return action

    @api.depends('contract_id')
    def _compute_hiring_date(self):
        """
        Compute employee hiring date
        :return:
        """
        for rec in self:
            start_dates = rec.contract_ids.filtered(lambda c: c.state != 'cancel').mapped('date_start')
            rec.hiring_date = min(start_dates)

    @api.onchange('children_ids')
    def onchange_children_ids(self):
        """
        Set children number on change of children lines
        :return:
        """
        self.children = len(self.children_ids)

    @api.depends('children_ids')
    def _compute_children_number(self):
        """
        Compute children number
        :return:
        """
        for rec in self:
            rec.children = len(rec.children_ids)

    @api.depends('contract_id')
    def _compute_resignation_notice_days(self):
        """
        Compute resignation notice days
        :return:
        """
        for rec in self:
            # Variable init
            category_id = rec.sudo().contract_id.contract_category_id
            group = category_id.group
            diff = relativedelta(fields.date.today(), rec.sudo().contract_id.date_start)
            # Set departure notice group
            rec.departure_notice_group = dict(category_id._fields['group'].selection).get(category_id.group)
            # Set departure notice days
            if diff and group:
                if diff.years >= 5:
                    if group == 'group_1':
                        rec.resignation_notice_days = 30
                    elif group == 'group_2':
                        rec.resignation_notice_days = 45
                    elif group == 'group_3':
                        rec.resignation_notice_days = 60
                    elif group == 'group_4':
                        rec.resignation_notice_days = 90
                    else:
                        rec.resignation_notice_days = 180
                elif diff.years in [3, 4]:
                    if group == 'group_1':
                        rec.resignation_notice_days = 10 + (2 if diff.years == 3 else 4)
                    elif group == 'group_2':
                        rec.resignation_notice_days = 30 + (2 if diff.years == 3 else 4)
                    elif group == 'group_3':
                        rec.resignation_notice_days = 45 + (2 if diff.years == 3 else 4)
                    elif group == 'group_4':
                        rec.resignation_notice_days = 75 + (2 if diff.years == 3 else 4)
                    else:
                        rec.resignation_notice_days = 120 + (2 if diff.years == 3 else 4)
                elif diff.years in [1, 2]:
                    if group == 'group_1':
                        rec.resignation_notice_days = 10
                    elif group == 'group_2':
                        rec.resignation_notice_days = 30
                    elif group == 'group_3':
                        rec.resignation_notice_days = 45
                    elif group == 'group_4':
                        rec.resignation_notice_days = 75
                    else:
                        rec.resignation_notice_days = 120
                else:
                    if diff.months >= 3:
                        if group == 'group_1':
                            rec.resignation_notice_days = 8
                        elif group == 'group_2':
                            rec.resignation_notice_days = 15
                        elif group == 'group_3':
                            rec.resignation_notice_days = 30
                        elif group == 'group_4':
                            rec.resignation_notice_days = 45
                        else:
                            rec.resignation_notice_days = 90
                    elif diff.months in [2, 1] or diff.days >= 8:
                        if group == 'group_1':
                            rec.resignation_notice_days = 3
                        elif group == 'group_2':
                            rec.resignation_notice_days = 8
                        elif group == 'group_3':
                            rec.resignation_notice_days = 15
                        elif group == 'group_4':
                            rec.resignation_notice_days = 30
                        else:
                            rec.resignation_notice_days = 30
                    else:
                        if group == 'group_1':
                            rec.resignation_notice_days = 1
                        elif group == 'group_2':
                            rec.resignation_notice_days = 2
                        elif group == 'group_3':
                            rec.resignation_notice_days = 3
                        elif group == 'group_4':
                            rec.resignation_notice_days = 4
                        else:
                            rec.resignation_notice_days = 5
            else:
                rec.resignation_notice_days = 0

    @api.depends('contract_ids', 'initial_employment_date')
    def _compute_months_service(self):
        """
        Optimisation while computing month of service
        :return:
        """
        # Variable init
        for rec in self:
            contract_ids = rec.contract_ids
            active_contract_id = contract_ids.filtered(lambda c: c.state == 'open')
            today = fields.date.today()
            # Get date start
            date_start_list = contract_ids.filtered(lambda c: c.state in ['cancel', 'open']).mapped('date_start')
            date_start = min(date_start_list) if date_start_list else today


            date_start_max = max(date_start_list) if date_start_list else today
            end = contract_ids.filtered(lambda c: c.date_start == date_start_max).mapped('date_end')
            end = max(end) if end else ''

            date_end = today
            if end and end < today:
                date_end = end
            elif end and end > today:
                date_end = today

            print(date_start)
            diff = relativedelta(date_end, date_start)
            years = _('{} an(s)'.format(diff.years)) if diff.years else ''
            months = _(' {} mois'.format(diff.months)) if diff.months else ''
            days = _(' {} jour(s)'.format(diff.days)) if diff.days else ''
            rec.sudo().length_of_service = (diff.years * 12) + diff.months + (diff.days / 30)
            rec.sudo().length_of_service_text = '{}{}{}'.format(years, months, days)
