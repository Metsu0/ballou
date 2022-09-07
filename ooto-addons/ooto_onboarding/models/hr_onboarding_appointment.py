# -*- coding: utf-8 -*-
import time
from datetime import datetime, timedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import safe_eval


class HrOnboardingAppointment(models.Model):
    _inherit = "calendar.event"
    _description = "Hr Onboarding Appointment"

    is_onboarding_appointment = fields.Boolean(default=False, string='Onboarding appointment')
    employee_ids = fields.Many2many("hr.employee", string="Employee", copy=False)
    employee_domain = fields.Char(string='Employee domain', copy=False)
    task_id = fields.Many2one("hr.onboarding.task", "Task")
    validation_msg = fields.Char('Starting at', default='')
    appointment_task_id = fields.Many2one("hr.onboarding.task", "Appointment task")
    status = fields.Selection([
        ('to_do', _('To do')),
        ('done', _('Done')),
    ], string='State', compute='_compute_appointment_state', store=True)
    
    #HRN ADD status in public fields for group by
    @api.model
    def _get_public_fields(self):
        public_fields = super(HrOnboardingAppointment, self)._get_public_fields()
        public_fields |= {'status'}
        return public_fields

    @api.onchange('employee_domain')
    def onchange_employee_domain(self):
        """
        Method to change employee_ids according to domain
        :return: None
        """
        domain = safe_eval(self.employee_domain) if self.employee_domain else None
        if domain:
            employee_ids = self.env['hr.employee'].search(domain).ids
            self.employee_ids = [(6, 0, employee_ids)]

    @api.onchange("employee_ids")
    def onchange_employee_ids(self):
        """
        Method to get partner_ids linked to employee_ids and add these to partner_ids field.
        :return: None
        """
        partner_ids = []
        employee_ids = self.employee_ids
        for employee_id in employee_ids:
            partner_id = employee_id.user_id.partner_id
            if partner_id:
                partner_ids.append(partner_id.id)
        existing_partner = self.partner_ids.filtered(lambda p: len(p.user_ids.employee_ids) == 0).ids
        self.partner_ids = [(6, 0, partner_ids + existing_partner)]

    def write(self, vals):

        """
        Method to postpone an appointment (change start_datetime or start_date).
        :param self: calendar.event object
        :param vals: modified fields
        :return: res
        """

        is_waiting_for_validation = False
        if not self._context.get('from_validation') and (
                vals.get('start_datetime', False) or vals.get('start_date', False) or vals.get('start', False)):
            # Prevent modification when start date is waiting for validation
            if self.validation_msg:
                raise UserError(_("Can't accept modification. Start date is waiting for validation."))
            # Variables initialization
            current_user_id = self.env.user
            employee_id = current_user_id.employee_ids[0] if current_user_id.employee_ids else None
            attendee_ids = None
            if vals.get('partner_ids', False):
                new_attendee_ids = vals.get('partner_ids')[0][2]
                attendee_ids = self.env['res.partner'].browse(new_attendee_ids).mapped('user_ids')
            else:
                attendee_ids = self.partner_ids.mapped('user_ids')
            # If current user is admin or manager
            is_manager = False if employee_id.responsible_ids else True
            # If current user have a superior and in in attendees
            if current_user_id.id in attendee_ids.ids and is_manager == False:
                # Define postpone appointment object parametters
                responsible_ids = employee_id.responsible_ids
                tmp_ids = [e.user_id.partner_id.id for e in responsible_ids if e in attendee_ids.mapped('employee_ids')]
                tmp_ids.append(0)
                resp_ids = tmp_ids if tmp_ids else [self.user_id.partner_id, ]
                new_date = vals.get('start_datetime') if vals.get('start_datetime') else vals.get('start_date')
                new_date = new_date if new_date else vals.get('start')
                new_vals = {
                    'onboarding_appointment_id': self.id,
                    'old_date': self.start_datetime if vals.get('start_datetime') else self.start_date,
                    'new_date': new_date,
                    'request_sender_id': current_user_id.partner_id.id,
                    'validator_ids': [(6, 0, resp_ids)],
                    'allday': vals.get('allday', False)
                }
                # Create resquest to postpone appointment object
                postpone_id = self.env['hr.onboarding.appointment.postpone'].create(new_vals)
                # Remove all date in vals dict
                is_waiting_for_validation = True
                # set validation message
                vals.update({'validation_msg': _('%s (Waiting for validation)' % new_date)})
        if is_waiting_for_validation:
            keys = ['start_date', 'start_datetime', 'stop_date', 'stop_datetime', 'stop_date', 'start', 'stop']
            for key in keys:
                if key in vals.keys(): del vals[key]
        res = super(HrOnboardingAppointment, self).write(vals)

        # Update appointment task
        self.update_appointment_task(self)

        return res

    @api.model
    def create(self, vals):
        """
        Create task when creating appointment
        :param vals:
        :return:
        """
        res = super(HrOnboardingAppointment, self).create(vals)
        # Variable paramaters initialization
        default_description = "Description"
        if self._context.get('default_is_onboarding_appointment'):
            new_task = {
                'name': res.name,
                'to_do_for': 'specific',
                'period': 'specific',
                'date_start': res.start if res.start else None,
                'date_end': res.stop if res.stop else None,
                'task_type': 'appointment',
                'type_domain': 'contact',
                'description': res.description if res.description else default_description,
                'stain_label': _('appointment'),
                'location': res.location,
                'employee_ids': [(6, 0, res.partner_ids.mapped('user_ids').mapped('employee_ids').mapped('id'))],
            }
            # Create task
            res.appointment_task_id = self.env['hr.onboarding.task'].create(new_task)
        return res

    def update_appointment_task(self, vals):
        self.appointment_task_id.write(
            {
                'name': vals.name,
                'date_start': vals.start,
                'date_end': vals.stop,
                'description': vals.description if vals.description else "description",
                'location': vals.location,
                'employee_ids': [(6, 0, vals.partner_ids.mapped('user_ids').mapped('employee_ids').mapped('id'))],
            }
        )

    @api.depends('stop')
    def _compute_appointment_state(self):
        for rec in self:
            #HRN Change start_datetime to start v14
            if rec.start and rec.duration:
                date_end = time.mktime(rec.stop.timetuple())
                current_date = time.mktime(datetime.utcnow().timetuple())
                rec.status = 'done' if date_end < current_date else 'to_do'
            else:
                rec.status = False


class HrOnboardingAppointmentPostpone(models.Model):
    _name = 'hr.onboarding.appointment.postpone'
    _description = 'Hr Onboarding Appointment Postpone'
    _rec_name = 'onboarding_appointment_id'

    onboarding_appointment_id = fields.Many2one('calendar.event', 'Onboarding Appointment')
    old_date = fields.Datetime(string='Old date')
    new_date = fields.Datetime(string='New date')
    state = fields.Selection([
        ('waiting_for_validation', 'Waiting for validation'),
        ('validate', 'Validate'),
        ('refused', 'Refused')
    ], default='waiting_for_validation')
    request_sender_id = fields.Many2one('res.partner', string='Request Sender')
    validator_ids = fields.One2many('res.partner', 'validator_id', string='Validator')
    allday = fields.Boolean('All days', default=False)

    def validate_request(self):
        """
        Method to validate the request to postpone appointment
        :return: None
        """
        for rec in self:
            # Write appointment validation msg
            rec.onboarding_appointment_id.with_context(from_validation=True).write({
                'validation_msg': '',
                'start_date': rec.new_date.date() if rec.allday else False,
                'start_datetime': rec.new_date if not rec.allday else False,
                'stop_date': rec.new_date.date() + timedelta(
                    hours=rec.onboarding_appointment_id.duration) if rec.allday else False,
                'stop_datetime': rec.new_date + timedelta(
                    hours=rec.onboarding_appointment_id.duration) if not rec.allday else False
            })
            # Write postpone request
            rec.write({'state': 'validate'})

    def refuse_request(self):
        """
        Method to refuse the request to postpone appointment
        :return: None
        """
        for rec in self:
            # Write appointment validation msg
            allday = rec.allday
            rec.onboarding_appointment_id.write({'validation_msg': ''})
            # Write postpone request
            rec.write({'state': 'refused'})
