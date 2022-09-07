# coding: utF-8
from urllib.parse import urljoin

import werkzeug

from odoo import models, fields, api, _
from odoo.http import request
from odoo import exceptions


class OdCreation(models.TransientModel):
    _name = 'employee.option'
    _description = 'Wizard Option for employee creation'
    _rec_name = 'option'

    option = fields.Selection([
        ('send_notification', _('Send / schedule an invitation by email')),
        ('set_password', _('Set the password (without sending an email)')),
        ('send_email_onboarding', _('Send an email to the creation of onboarding')),
        ('do_nothing', _('Do Nothing')),
    ], 'Creation Option', default='do_nothing', required=True)
    date_sending_invitation = fields.Datetime('Date sending invitation mail')
    password = fields.Char('Password')
    confirm_password = fields.Char('Confirm Password')

    def get_wizard_view_id(self, **kwargs):
        """
        Method to get view id of employee
        :param kwargs:
        :return:
        """
        view_id = self.env.ref('ooto_onboarding.employee_option_wizard_form')
        return view_id.id

    def valid_option(self):
        pass

    @api.model
    def do_option_validation(self, vals, options):
        """
        Method call on Employee option validation
        :param vals: values of employee to create
        :param options:
        :return:
        """
        # get value for partner creation from context
        employee_id = self.env['hr.employee'].search([('work_email', '=', vals.get('work_email'))])
        employee_id.sudo().not_send_mail = True
        employee_id.sudo().option = options.get('option')
        if options.get('option') == 'do_nothing':
            employee_id.sudo().no_reset_mail = True
        elif options.get('option') == 'send_email_onboarding':
            employee_id.sudo().no_reset_mail = True
        elif options.get('option') == 'set_password':
            if not options.get('password') or options.get('password') != options.get('confirm_password'):
                raise exceptions.UserError(_("Password incorrect"))
            employee_id.sudo().password = employee_id.sudo().user_id.password = options.get('password')
        else:
            if not options.get('date_sending_invitation', False):
                raise exceptions.UserError(_("Date sending invitation empty"))
            employee_id.sudo().date_sending_invitation = options.get('date_sending_invitation')
            employee_id.sudo().no_reset_mail = False
        return employee_id.id
