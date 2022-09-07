# -*- coding:utf-8 -*-
import json

import odoo
from odoo import http, registry, SUPERUSER_ID
from odoo.addons.ooto_onboarding.controllers.web_editor import Web_Editor
from odoo.api import Environment
from odoo.http import request
from odoo.tools import pycompat, config


class Onboarding_Web_Editor(Web_Editor):
    employee_mail = None

    @http.route('/web_editor/field/html', type='http', auth="user")
    def FieldTextHtml(self, model=None, res_id=None, field=None, callback=None, **kwargs):
        kwargs.update(
            model=model,
            res_id=res_id,
            field=field,
            datarecord=json.loads(kwargs['datarecord']),
            debug=request.debug)

        for k in kwargs:
            if isinstance(kwargs[k], pycompat.string_types) and kwargs[k].isdigit():
                kwargs[k] = int(kwargs[k])

        trans = dict(
            lang=kwargs.get('lang', request.env.context.get('lang')),
            translatable=kwargs.get('translatable'),
            edit_translations=kwargs.get('edit_translations'),
            editable=kwargs.get('enable_editor'))

        kwargs.update(trans)

        content = None
        if model:
            Model = request.env[model].with_context(trans)
            if kwargs.get('res_id'):
                record = Model.browse(kwargs.get('res_id'))
                content = record and getattr(record, field)
            else:
                content = Model.default_get([field]).get(field)

        kwargs.update(content=content or '')
        mailing_model_id = kwargs.get('datarecord').get('mailing_model_id')
        context = mailing_model_id.get('context')
        self.employee_mail = context.get('employee_mail') if context else None
        context = request.env.context.copy()
        context.update({'employee_mail': self.employee_mail})
        request.env.context = context
        return request.render(kwargs.get("template") or "web_editor.FieldTextHtml", kwargs, uid=request.uid)

    @http.route(['/mass_mailing/snippets'], type='json', auth="user", website=True)
    def mass_mailing_snippets(self):
        db_name = config['central_db']
        signup_url = ''
        registry = odoo.registry(db_name)
        with registry.cursor() as cse_cr:
            cse_env = Environment(cse_cr, SUPERUSER_ID, {})
            usr_id = cse_env['res.users'].sudo().search([('login', '=', self.employee_mail)])
            signup_url = usr_id.signup_url
        user_id = request.env['res.users'].search([('login', '=', self.employee_mail)])
        values = {
            'company_id': user_id.company_id,
            'user_id': user_id,
            'signup_url': signup_url,
        }
        return request.env.ref('ooto_onboarding.email_designer_snippets').render(values)
