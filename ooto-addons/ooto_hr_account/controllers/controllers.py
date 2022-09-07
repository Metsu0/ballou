# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import re
from datetime import datetime

from odoo import tools, _, SUPERUSER_ID
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.exceptions import ValidationError
from odoo.http import request, route

_logger = logging.getLogger(__name__)


class CustomerPortal(CustomerPortal):
    # mandatory fields for user with employee
    MANDATORY_BILLING_FIELDS_OOTO = ["firstname", "lastname", "email"]
    OPTIONAL_BILLING_FIELDS_PARTNER = ["zip", "state_id", "title", "city", "country_id", "street"]
    OPTIONAL_BILLING_FIELDS_EMPLOYEE = ["work_phone"]
    OPTIONAL_BILLING_FIELDS_EMPLOYEE_DYNAMIC = ["job_id", "admin_responsible_id", "software_responsible_id",
                                                "department_id", "parent_id", "coach_id", "bank_account_id"]
    # mandatory fields for user without employee
    MANDATORY_BILLING_FIELDS = ["name", "phone", "email", "street", "city", "country_id"]
    OPTIONAL_BILLING_FIELDS = ["zipcode", "state_id", "vat", "company_name"]

    DYNAMIC_FIELDS = []
    DYNAMIC_FIELDS_DATE = []
    DYNAMIC_FIELDS_INTEGER = []
    DYNAMIC_FIELDS_BOOLEAN = []
    DYNAMIC_FIELDS_MANY2ONE = []

    @route(['/my/account'], type='http', auth='user', website=True)
    def account(self, redirect=None, **post):
        partner = request.env.user.partner_id
        employee = request.env['hr.employee'].sudo().search([('id', '=', partner.employee_id.id)])
        values = self._prepare_portal_layout_values()
        values.update({
            'error': {},
            'error_message': [],
        })
        hide_home = request.env['ir.config_parameter'].sudo().get_param('ooto_hr_account.hide_home')
        if employee:
            field_ids = []
            ir_model_field_obj = request.env['ir.model.fields']
            onboarding_model = request.env['ir.model'].sudo().search([('model', '=', 'hr.onboarding')])
            if onboarding_model:
                request.env.cr.execute("""
                                                  SELECT onb_emp_fields_id 
                                                  FROM employee_fields_document_onboarding_rel 
                                                  RIGHT JOIN onboarding_employee_fields_document 
                                                  ON employee_fields_document_onboarding_rel.onb_emp_fields_id = onboarding_employee_fields_document.id 
                                                  WHERE emp_id = %s
                                                  UNION ALL
                                                  SELECT onb_emp_fields_id 
                                                  FROM employee_fields_uploads_onboarding_rel 
                                                  RIGHT JOIN onboarding_employee_fields_upload 
                                                  ON employee_fields_uploads_onboarding_rel.onb_emp_fields_id = onboarding_employee_fields_upload.id 
                                                  WHERE emp_id = %s""", (employee.id, employee.id,)
                                       )

                onb_emp_fields_id = str(request.env.cr.fetchall())
                pattern = "\d+"
                onb_emp_fields = re.findall(pattern, onb_emp_fields_id)
                onb_emp_field_document_obj = request.env['onboarding.employee.fields.document']
                onb_emp_field_upload_obj = request.env['onboarding.employee.fields.upload']
                nbr_fields_list = []
                nbr = 0
                champ = []
                for onb_emp_field in onb_emp_fields:
                    if int(onb_emp_field) in request.env['onboarding.employee.fields.document'].search([]).mapped('id'):
                        onb_emp_field_document_id = onb_emp_field_document_obj.browse(int(onb_emp_field))
                        ir_model_field_document_id = ir_model_field_obj.browse(onb_emp_field_document_id.fields_id.id)
                        if ir_model_field_document_id.name not in champ:
                            champ.append(ir_model_field_document_id.name)
                            field_ids.append(ir_model_field_document_id)
                            nbr_fields_list.append(nbr)
                            nbr = nbr + 1
                    if int(onb_emp_field) in request.env['onboarding.employee.fields.upload'].search([]).mapped('id'):
                        onb_emp_field_upload_id = onb_emp_field_upload_obj.browse(int(onb_emp_field))
                        ir_model_field_upload_id = ir_model_field_obj.browse(onb_emp_field_upload_id.fields_id.id)
                        if ir_model_field_upload_id.name not in champ:
                            champ.append(ir_model_field_upload_id.name)
                            field_ids.append(ir_model_field_upload_id)
                            nbr_fields_list.append(nbr)
                            nbr = nbr + 1

                for i in nbr_fields_list:
                    if field_ids[i].ttype == 'date':
                        self.DYNAMIC_FIELDS_DATE.append(field_ids[i].name)
                    elif field_ids[i].ttype == 'integer':
                        self.DYNAMIC_FIELDS_INTEGER.append(field_ids[i].name)
                    elif field_ids[i].ttype == 'boolean':
                        self.DYNAMIC_FIELDS_BOOLEAN.append(field_ids[i].name)
                    elif field_ids[i].ttype != 'binary' and field_ids[i].name not in ['country_id', 'job_id',
                                                                                      'admin_responsible_id',
                                                                                      'software_responsible_id',
                                                                                      'parent_id',
                                                                                      'coach_id', 'department_id',
                                                                                      'bank_account_id']:
                        self.DYNAMIC_FIELDS.append(field_ids[i].name)

            if post:
                # error, error_message = self.details_form_validate(post)
                error, error_message = {}, []
                values.update({'error': error, 'error_message': error_message})
                values.update(post)
                if not error:
                    values = {key: post[key] for key in self.MANDATORY_BILLING_FIELDS_OOTO}
                    values.update({key: post[key] for key in self.OPTIONAL_BILLING_FIELDS_PARTNER if key in post})
                    values_employee = {key: post[key] for key in self.OPTIONAL_BILLING_FIELDS_EMPLOYEE if key in post}
                    values_dynamic = {key: post[key] for key in self.DYNAMIC_FIELDS if key in post}
                    values_dynamic_date = {key: post[key] for key in self.DYNAMIC_FIELDS_DATE if key in post}
                    values_dynamic_integer = {key: int(post[key]) for key in self.DYNAMIC_FIELDS_INTEGER if key in post}
                    values_dynamic_boolean = {key: bool(post[key]) for key in self.DYNAMIC_FIELDS_BOOLEAN if
                                              key in post}
                    values_employee_dynamic = {key: int(post[key]) for key in
                                               self.OPTIONAL_BILLING_FIELDS_EMPLOYEE_DYNAMIC
                                               if key in post}
                    # values_dynamic_many2one = {key: post[key] for key in self.DYNAMIC_FIELDS_MANY2ONE if key in post}
                    for date in values_dynamic_date:
                        values_dynamic_date.update(
                            {date: datetime.strptime(values_dynamic_date.get(date), '%Y-%m-%d').strftime('%Y-%m-%d')}
                        )

                    country_id = values.pop('country_id', None)
                    if country_id != None:
                        c = int(country_id)
                        country_id = {'country_id': c}
                        partner.sudo().write(country_id)

                    # job_id = values_employee_dynamic.pop('job_id', None)
                    # if job_id != None:
                    # 	j = int(job_id)
                    # 	jobs_id = {'job_id': j}
                    # 	employee.sudo().write(jobs_id)
                    #
                    # admin_responsible_id = values_employee_dynamic.pop('admin_responsible_id', None)
                    # if admin_responsible_id != None:
                    # 	admin_res = int(admin_responsible_id)
                    # 	admin_responsible_ids = {'admin_responsible_id': admin_res}
                    # 	employee.sudo().write(admin_responsible_ids)
                    #
                    # software_responsible_id = values_employee_dynamic.pop('software_responsible_id', None)
                    # if software_responsible_id != None:
                    # 	soft_res = int(software_responsible_id)
                    # 	software_responsible_ids = {'software_responsible_id': soft_res}
                    # 	employee.sudo().write(software_responsible_ids)

                    country_of_birth = values_dynamic.pop('country_of_birth', None)
                    # partner.sudo().write(values_dynamic_many2one)
                    employee.sudo().write(values_dynamic)
                    if country_of_birth != None:
                        request.env.cr.execute(
                            "update hr_employee set country_of_birth = " + str(country_of_birth) + " where id=" + str(
                                employee.id) + "")
                        request.env.cr.commit()
                    employee.sudo().write(values_dynamic_date)
                    employee.sudo().write(values_employee)
                    employee.sudo().write(values_employee_dynamic)
                    employee.sudo().write(values_dynamic_integer)
                    employee.sudo().write(values_dynamic_boolean)
                    partner.sudo().write(values)
                    if onboarding_model:
                        self.check_task_administrative()
                    if redirect:
                        return request.redirect(redirect)
                    return request.redirect('/my/account')

            countries = request.env['res.country'].sudo().search([])
            departments = request.env['hr.department'].sudo().search([])
            posts = request.env['hr.job'].sudo().search([])
            sirh_hr_employee_front_state = request.env['ir.module.module'].sudo().search(
                [('name', '=', 'sirh_hr_employee_front')]).state
            if sirh_hr_employee_front_state == 'installed':
                managers = employee.parent_id
                mentor = employee.coach_id
            else:
                managers = request.env['hr.employee'].sudo().search([('id', '!=', partner.user_ids.employee_id.id)])
                mentor = request.env['hr.employee'].sudo().search([('id', '!=', partner.user_ids.employee_id.id)])
            accounts = request.env['res.partner.bank'].sudo().search([])
            states = request.env['res.country.state'].sudo().search([])
            titles = request.env['res.partner.title'].sudo().search([])
            employees = request.env['hr.employee'].sudo().search([])
            values.update({
                'partner': partner,
                'employee': employee,
                'countries': countries,
                'getattr': getattr,
                'departments': departments,
                'accounts': accounts,
                'managers': managers,
                'posts': posts,
                'mentor': mentor,
                'states': states,
                'titles': titles,
                'has_check_vat': hasattr(request.env['res.partner'], 'check_vat'),
                'redirect': redirect,
                'page_name': 'my_details',
                'child_ids': partner.user_ids.employee_id.child_ids,
                'fields_dynamic': field_ids,
                'ir_model_fields': ir_model_field_obj,
                'datetime_cust': datetime,
                'employees': employees,
                'hide_home': hide_home
            })
        else:
            if post and request.httprequest.method == 'POST':
                error, error_message = self.details_form_validate(post)
                values.update({'error': error, 'error_message': error_message})
                values.update(post)
                if not error:
                    values = {key: post[key] for key in self.MANDATORY_BILLING_FIELDS}
                    values.update({key: post[key] for key in self.OPTIONAL_BILLING_FIELDS if key in post})
                    values.update({'country_id': int(values.pop('country_id', 0))})
                    values.update({'zip': values.pop('zipcode', '')})
                    if values.get('state_id') == '':
                        values.update({'state_id': False})
                    partner.sudo().write(values)
                    if redirect:
                        return request.redirect(redirect)
                    return request.redirect('/my/home')

            countries = request.env['res.country'].sudo().search([])
            states = request.env['res.country.state'].sudo().search([])

            values.update({
                'partner': partner,
                'countries': countries,
                'states': states,
                'has_check_vat': hasattr(request.env['res.partner'], 'check_vat'),
                'redirect': redirect,
                'page_name': 'my_details',
                'hide_home': hide_home,
            })
        response = request.render("portal.portal_my_details", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response


    # @route(['/my', '/my/home'], type='http', auth="user", website=True)
    # def home(self, **kw):
    #     """
    #     redirection to my account
    #     :param redirect:
    #     :param post:
    #     :return:
    #     """
    #     return request.redirect('/my/account')

    def details_form_validate(self, data):
        error = dict()
        error_message = []

        if request.env.user.partner_id.employee_id:
            # email validation
            if data.get('email') and not tools.single_email_re.match(data.get('email')):
                error["email"] = 'error'
                error_message.append(_('Invalid Email! Please enter a valid email address.'))

            # vat validation
            partner = request.env.user.partner_id
            if data.get("vat") and partner and partner.vat != data.get("vat"):
                if partner.can_edit_vat():
                    if hasattr(partner, "check_vat"):
                        if data.get("country_id"):
                            data["vat"] = request.env["res.partner"].fix_eu_vat_number(int(data.get("country_id")),
                                                                                       data.get("vat"))
                        partner_dummy = partner.new({
                            'vat': data['vat'],
                            'country_id': (int(data['country_id'])
                                           if data.get('country_id') else False),
                        })
                        try:
                            partner_dummy.check_vat()
                        except ValidationError:
                            error["vat"] = 'error'
                else:
                    error_message.append(_(
                        'Changing VAT number is not allowed once document(s) have been issued for your account. Please contact us directly for this operation.'))
        else:
            # Validation
            for field_name in self.MANDATORY_BILLING_FIELDS:
                if not data.get(field_name):
                    error[field_name] = 'missing'

            # email validation
            if data.get('email') and not tools.single_email_re.match(data.get('email')):
                error["email"] = 'error'
                error_message.append(_('Invalid Email! Please enter a valid email address.'))

            # vat validation
            partner = request.env.user.partner_id
            if data.get("vat") and partner and partner.vat != data.get("vat"):
                if partner.can_edit_vat():
                    if hasattr(partner, "check_vat"):
                        if data.get("country_id"):
                            data["vat"] = request.env["res.partner"].fix_eu_vat_number(int(data.get("country_id")),
                                                                                       data.get("vat"))
                        partner_dummy = partner.new({
                            'vat': data['vat'],
                            'country_id': (int(data['country_id'])
                                           if data.get('country_id') else False),
                        })
                        try:
                            partner_dummy.check_vat()
                        except ValidationError:
                            error["vat"] = 'error'
                else:
                    error_message.append(_(
                        'Changing VAT number is not allowed once document(s) have been issued for your account. Please contact us directly for this operation.'))

            # error message for empty required fields
            if [err for err in error.values() if err == 'missing']:
                error_message.append(_('Some required fields are empty.'))

            unknown = [k for k in data if k not in self.MANDATORY_BILLING_FIELDS + self.OPTIONAL_BILLING_FIELDS]
            if unknown:
                error['common'] = 'Unknown field'
                error_message.append("Unknown field '%s'" % ','.join(unknown))

        return error, error_message

    @route('/user/change_user_avatar', type='json', auth="user", methods=['POST'], website=True, csrf=False)
    def change_avatar(self, image_bin=None, **kwargs):
        request.env(user=SUPERUSER_ID)['res.users'].browse(request.session.uid).write({'image_1920': image_bin})

    @route('/user/upload_file_dynamic', type='json', auth="user", methods=['POST'], website=True, csrf=False)
    def upload_file_dynamic(self, input_name, file_name, file):
        employee_id = request.env['hr.employee'].search([('user_id', '=', request.session.uid)])[0]
        employee_id.write({
            input_name: file,
            'x_filename_of_{}'.format(input_name): file_name
        })

    def check_task_administrative(self):
        employee = request.env.user.employee_id

        # fields_value = []
        binary_fields_value = []
        is_fields_filled = False

        all_task_admin = request.env['hr.onboarding.task'].search(
            [('parent_id', '=', False), ('task_type', '=', 'administrative')])
        for task in all_task_admin:
            fields_value = []
            if task and task.task_state != 'terminated':
                all_fields_document_onb = request.env['onboarding.employee.fields.document'].search(
                    [('onboarding_task', '=', task.id)])
                all_fields_upload_onb = request.env['onboarding.employee.fields.upload'].search(
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
