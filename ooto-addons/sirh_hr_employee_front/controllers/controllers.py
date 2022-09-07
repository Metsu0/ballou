# -*- coding: utf-8 -*-

import io
import base64
import logging
import ast
import json
from datetime import datetime
from werkzeug.datastructures import FileStorage
from werkzeug.utils import redirect

from odoo import tools, _, SUPERUSER_ID
from odoo.exceptions import ValidationError
from odoo.http import request, route
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo import http

_logger = logging.getLogger(__name__)


class CustomerPortal(CustomerPortal):
    OPTIONAL_BILLING_FIELDS_PARTNER_SIRH = ["gender", "marital_status", "birthday", "function"]

    OPTIONAL_BILLING_FIELDS_EMPLOYEE_SIRH = ["emergency_contact", "emergency_phone", "km_home_work", "identification_id",
                                        "passport_id", "place_of_birth", "country_of_birth", "visa_no", "permit_no",
                                        "visa_expire", "certificate", "study_field", "study_school"]

    @route(['/my/account', '/fr-_FR/fr-_FR/my/account'], type='http', auth='user', website=True)
    def account(self, redirect=None, **post):
        res = super(CustomerPortal, self).account(redirect=None, **post)
        user = request.env.user
        partner = request.env.user.partner_id
        employee = request.env['hr.employee'].sudo().search([('id', '=', partner.employee_id.id)])
        leave_data = request.env['hr.leave'].get_leave_data(user.id)
        res.qcontext.update(leave_data)
        if employee:
            if post:
                error, error_message = {}, []
                res.qcontext.update(post)
                if not error:
                    values = ({key: post.get(key) for key in self.OPTIONAL_BILLING_FIELDS_PARTNER_SIRH if key in post})
                    val = {key: post.get(key) for key in self.OPTIONAL_BILLING_FIELDS_EMPLOYEE_SIRH if key in post}
                    values.update({'zip': res.qcontext.pop('zipcode', '')})
                    if values.get('birthday'):
                        try:
                            values.update(
                                {'birthday': datetime.strptime(values.get('birthday'), '%Y-%m-%d').strftime('%Y-%m-%d')})
                        except:
                            values.update(
                                {'birthday': datetime.strptime(values.get('birthday'), '%d/%m/%Y').strftime('%Y-%m-%d')})
                    if val.get('visa_expire'):
                        try:
                            val.update(
                                {'visa_expire': datetime.strptime(val.get('visa_expire'), '%Y-%m-%d').strftime('%Y-%m-%d')})
                        except:
                            val.update(
                                {'visa_expire': datetime.strptime(val.get('visa_expire'), '%d/%m/%Y').strftime('%Y-%m-%d')})
                    partner.sudo().with_context(from_portal=True, set_name=True).write(values)

                    country_of_birth = val.pop('country_of_birth', None)
                    employee.sudo().with_context(set_name=True).write(val)

                    if country_of_birth != None:
                        request.env.cr.execute(
                            "update hr_employee set country_of_birth = " + str(country_of_birth) + " where id=" + str(
                                employee.id) + "")
                        request.env.cr.commit()
            spinnerets = request.env['hr.spinneret'].sudo().search([])  # maybe unused for ooto
            levels = request.env['hr.level'].sudo().search([])  # maybe unused for ooto
            sanctions = []
            directions = []
            stories = []
            if 'hr.sanction' in request.env:
                sanctions = request.env['hr.sanction'].sudo().search(
                    [('employee_id', '=', partner.employee_id.id)])  # maybe unused for ooto
            if 'hr.direction' in request.env:
                directions = request.env['hr.direction'].sudo().search([])  # maybe unused for ooto

            # TRACKING FOR EVOLUTION HISTORY: if needed
            evolutions = request.env['mail.message'].sudo().search([('model', '=', 'hr.employee'), ('res_id', '=', partner.employee_id.id)])
            for evolution in evolutions:
                field_tracked = ['job_id', 'level_id', 'spinneret_id']
                for line in evolution.tracking_value_ids:
                    if line.field in field_tracked:
                        stories.append(line)
            res.qcontext.update({
                'deputies': partner.employee_id.deputy_ids,
                'spinnerets': spinnerets,  # maybe unused for ooto
                'levels': levels,  # maybe unused for ooto
                'directions': directions,  # maybe unused for ooto
                'employee2dir': employee,
                'sanctions': sanctions,
                'stories': stories,
                'job': request.env['hr.job'].sudo().search([('id', '=', employee.job_id.id)]),
            })
        return res

    @route(['/my/account/download/<int:attachment_id>'], type='http', auth="user", website=True)
    def download_attachment(self, attachment_id=None, sortby=None, search=None, search_in='content', filter=None, **kw):
        attachment = request.env['ir.attachment'].sudo().search_read(
            [('id', '=', int(attachment_id))],
            ["name", "datas", "res_model", "res_id", "type", "url"]
        )
        if attachment:
            attachment = attachment[0]
            if attachment["url"]:
                return redirect(attachment["url"])
            elif attachment["datas"]:
                data = io.BytesIO(base64.standard_b64decode(attachment["datas"]))
                return http.send_file(data, filename=attachment['name'], as_attachment=True)
            else:
                return request.not_found()
