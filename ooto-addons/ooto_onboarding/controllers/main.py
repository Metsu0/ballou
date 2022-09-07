# -*- coding: utf-8 -*-
import json
import os
import re
import subprocess

from odoo import http, tools
from odoo.addons.web.controllers.main import content_disposition
from odoo.addons.ooto_hr_account.controllers.controllers import CustomerPortal

from odoo.http import request

DYNAMIC_FIELDS = ['country_id', 'country_of_birth', 'bank_account_id', 'job_id', 'parent_id', 'coach_id',
                  'admin_responsible_id', 'software_responsible_id', 'department_id']


class DataAdminController(http.Controller):

    @http.route('/server/log', type='http', auth='none', csrf=False)
    def get_log_file(self, **kw):
        log_url = tools.config.get('logfile', '') or ''
        if log_url:
            file_name = os.path.basename(log_url)
            try:
                log_file = open(log_url, 'r')
                data_file = log_file.read()
                logheader = [('Content-Type', 'application/octet-stream'),
                             ('Content-Disposition', content_disposition(file_name))]
                return http.request.make_response(data_file, logheader)
            except IOError:
                return "Log file not found"
        else:
            return "No log file"

    @http.route('/server/wkhtmltopdf/version', type='http', auth='none', csrf=False)
    def get_wkhtmltopdf_verion(self, **kw):
        return subprocess.check_output("wkhtmltopdf -V", shell=False)

    @http.route('/task/notify', type='json', auth="user")
    def notify_task(self):
        return http.request.env['task.reminder.notif'].get_next_notif()


class CustomerPortalOnboarding(CustomerPortal):
    # mandatory fields for user without employee
    MANDATORY_BILLING_FIELDS = ["name", "phone", "email", "street", "city", "country_id"]
    OPTIONAL_BILLING_FIELDS = ["zipcode", "state_id", "vat", "company_name"]

    @http.route(['/my/account'], type='http', auth='user', website=True)
    def account(self, redirect=None, **post):
        if request.env.user.partner_id.employee_id:
            res = super(CustomerPortalOnboarding, self).account(redirect=None, **post)
            employee_id = request.env['hr.employee'].search([('user_id', '=', request.session.uid)])[0]
            onboarding_ids = request.env['hr.onboarding'].search([('employee_id', '=', employee_id.id)])
            form_task_ids = onboarding_ids.task_ids.filtered(
                lambda t: t.task_type == 'form' and t.task_state in ["to_do", "late"])[-3:]

            # Get employee dynamic fields
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
                                              WHERE emp_id = %s""", (employee_id.id, employee_id.id,)
                                   )

            onb_emp_fields_id = str(request.env.cr.fetchall())
            pattern = "\d+"
            onb_emp_fields = re.findall(pattern, onb_emp_fields_id)
            onb_emp_field_document_obj = request.env['onboarding.employee.fields.document']
            onb_emp_field_upload_obj = request.env['onboarding.employee.fields.upload']
            ir_model_field_obj = request.env['ir.model.fields']
            field_ids = []
            fields_value = []
            binary_fields_value = []
            is_fields_filled = False
            is_binary_fields_filled = False
            binary_fields_not_filled = []
            field = []
            for onb_emp_field in onb_emp_fields:
                if int(onb_emp_field) in request.env['onboarding.employee.fields.document'].search([]).mapped('id'):
                    onb_emp_field_document_id = onb_emp_field_document_obj.browse(int(onb_emp_field))
                    ir_model_field_document_id = ir_model_field_obj.browse(onb_emp_field_document_id.fields_id.id)
                    field_ids.append(ir_model_field_document_id)
                if int(onb_emp_field) in request.env['onboarding.employee.fields.upload'].search([]).mapped('id'):
                    onb_emp_field_upload_id = onb_emp_field_upload_obj.browse(int(onb_emp_field))
                    ir_model_field_upload_id = ir_model_field_obj.browse(onb_emp_field_upload_id.fields_id.id)
                    if ir_model_field_upload_id.name not in field:
                        field.append(ir_model_field_upload_id.name)
                        field_ids.append(ir_model_field_upload_id)
            for field_id in field_ids:
                if field_id and field_id.ttype == "many2one":
                    name_field_many2one = field_id.name
                    if name_field_many2one != 'bank_account_id':
                        object = employee_id.mapped(name_field_many2one)
                        if object.name:
                            fields_value.append(object.name)
                        else:
                            fields_value.append(False)
                    else:
                        object = employee_id.mapped(name_field_many2one)
                        if object.acc_number:
                            fields_value.append(object.acc_number) if object.acc_number else ' '
                        else:
                            fields_value.append(False)
                elif field_id and field_id.ttype == "binary":
                    binary_fields_value.append(getattr(employee_id, field_id.name))
                    if not getattr(employee_id, field_id.name):
                        binary_fields_not_filled.append(field_id)
                elif field_id and field_id.ttype not in ['binary', 'many2one', 'boolean']:
                    fields_value.append(getattr(employee_id, field_id.name))
            # is_fields_filled = False if False in fields_value or None in fields_value else True
            if False not in fields_value:
                is_fields_filled = True
            is_binary_fields_filled = False if False in binary_fields_value else True
            last_document_tasks = onboarding_ids.task_ids.filtered(
                lambda
                    t: t.task_type == 'administrative' and t.administrative_type == 'document_fill' and t.task_state in [
                    "to_do", "late"])[-3:]
            unachieved_tasks = onboarding_ids.task_ids.filtered(
                lambda t: t.task_state in ["to_do", "late"] and t.task_type != 'advice')
            last_binary_fields_not_filled = binary_fields_not_filled[-3:]
            last_unachieved_tasks = unachieved_tasks[-3:]
            res.qcontext.update({
                "unachieved_tasks": unachieved_tasks,
                "last_unachieved_tasks": last_unachieved_tasks,
                "form_task_ids": form_task_ids,
                "is_fields_filled": is_fields_filled,
                "is_binary_fields_filled": is_binary_fields_filled,
                "binary_fields_not_filled": binary_fields_not_filled,
                "last_binary_fields_not_filled": last_binary_fields_not_filled,
                "last_document_tasks": last_document_tasks,
            })
            return res
        else:
            return super(CustomerPortalOnboarding, self).account(redirect=None, **post)

    @http.route(['/my/account/document_tasks'], type='http', auth='user', website=True)
    def document_tasks(self):
        """
        Method to get all document tasks of an employee.
        Document task is administrative task that the employee has to fill fields
        :return: template with all document task
        """
        values = {}
        employee_id = request.env['hr.employee'].search([('user_id', '=', request.session.uid)])[0]
        onboarding_id = request.env['hr.onboarding'].search([('employee_id', '=', employee_id.id)])
        document_tasks = form_task_ids = onboarding_id.task_ids.filtered(
            lambda t: t.task_type == 'administrative' and t.administrative_type == 'document_fill' and t.task_state in [
                "to_do", "late"])[-3:]
        values.update({
            'document_tasks': document_tasks,
        })
        return request.render('ooto_onboarding.document_tasks', values)

    @http.route(['/my/account/form_tasks'], type='http', auth='user', website=True)
    def personal_form_task(self):
        employe_id = request.env['hr.employee'].search([('user_id', '=', request.session.uid)])[0]
        onboarding_ids = request.env['hr.onboarding'].search([('employee_id', '=', employe_id.id)])
        form_task_ids = onboarding_ids.task_ids.filtered(
            lambda t: t.task_type == 'form' and t.task_state in ["to_do", "late"])
        values = {
            "personal_form_task": form_task_ids
        }
        return request.render('ooto_onboarding.personal_form_task', values)

    @http.route(['/my/account/files_to_upload'], type='http', auth='user', website=True)
    def files_to_upload(self):
        value = {}
        employee_id = request.env['hr.employee'].search([('user_id', '=', request.session.uid)])[0]
        request.env.cr.execute("""
                                      SELECT onb_emp_fields_id 
                                      FROM employee_fields_uploads_onboarding_rel 
                                      RIGHT JOIN onboarding_employee_fields_upload 
                                      ON employee_fields_uploads_onboarding_rel.onb_emp_fields_id = onboarding_employee_fields_upload.id 
                                      WHERE emp_id = %s""", (employee_id.id,))
        onb_emp_fields_id = str(request.env.cr.fetchall())
        pattern = "\d+"
        onb_emp_fields = re.findall(pattern, onb_emp_fields_id)
        onb_emp_field_obj = request.env['onboarding.employee.fields.upload']
        ir_model_field_obj = request.env['ir.model.fields']
        field_ids = []
        binary_fields_to_fill = []
        champ = []
        for onb_emp_field in onb_emp_fields:
            onb_emp_field_id = onb_emp_field_obj.browse(int(onb_emp_field))
            ir_model_field_id = ir_model_field_obj.browse(onb_emp_field_id.fields_id.id)
            if ir_model_field_id.name not in champ:
                champ.append(ir_model_field_id.name)
                field_ids.append(ir_model_field_id)
        for field_id in field_ids:
            if field_id.ttype == 'binary' and not getattr(employee_id, field_id.name):
                binary_fields_to_fill.append(field_id)
        values = {
            "binary_fields_to_fill": binary_fields_to_fill
        }
        return request.render('ooto_onboarding.personal_binary_fields_to_fill', values)
