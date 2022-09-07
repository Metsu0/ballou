# -*- coding: utf-8 -*-

import json

from lxml import etree

from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    firstname = fields.Char("First name", related="user_id.firstname", index=True, store=True)
    lastname = fields.Char("Last name", related="user_id.lastname", index=True, store=True)
    # hr_code = fields.Char("HR Code", related="user_id.hr_code", index=True)
    admin_responsible_id = fields.Many2one("hr.employee", "Admin responsible")
    software_responsible_id = fields.Many2one("hr.employee", "software responsible")
    password = fields.Char("Password")
    not_send_mail = fields.Boolean("Invitation mail", )
    registration_number = fields.Char("Registration number")
    no_reset_mail = fields.Boolean("Reset mail")

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(HrEmployee, self).fields_view_get(
            view_id=view_id,
            view_type=view_type,
            toolbar=toolbar,
            submenu=submenu
        )
        all_fields = self.fields_get()

        annuaire_config_model = self.env['ir.model'].search([('model', '=', 'annuaire.configuration')])

        onboarding_model = self.env['ir.model'].search([('model', '=', 'hr.onboarding')])

        if annuaire_config_model:
            if 'annuaire' in self._context:
                view_types = ['tree', 'form', 'kanban']
                arch_db_eview = etree.XML(res['arch'])

                if view_type == 'form':
                    arch_db_eview = etree.XML(res['arch'])
                    annuaire_config = self.env.ref('ooto_annuaire.employee_sect_config_data')
                    if annuaire_config.contact_fields_ids.mapped('fields_id'):
                        eview_wrap_group = False
                        eview_wrap_group = arch_db_eview.xpath(
                            "//page[@name='dynamic_fields_page']/group[@name='parent']/group[@name='fields']")[0]

                        for field in annuaire_config.contact_fields_ids.mapped('fields_id'):
                            filename = "x_filename_of_%s" % field.name
                            binary_filename = self.env['ir.model.fields'].search([('name', '=', filename)])
                            if binary_filename:
                                binary_filename_data = self.init_data_input(all_fields[binary_filename.name],
                                                                            binary_filename)
                                eview_wrap_group.append(etree.Element('field', binary_filename_data))
                            field_data = self.init_data_input(all_fields[field.name], field)
                            eview_wrap_group.append(etree.Element('field', field_data))

                    res['arch'] = etree.tostring(arch_db_eview)

                    if annuaire_config.employees_fields_ids.mapped('fields_id'):

                        fields = annuaire_config.employees_fields_ids.mapped('fields_id')
                        employees_fields_ids = fields - fields[0]

                        eview_wrap_group_employee = False
                        eview_wrap_group_employee = \
                            arch_db_eview.xpath("//group[@name='fields']/field[@name='job_id']")[0]
                        for field in employees_fields_ids:
                            filename = "x_filename_of_%s" % field.name
                            binary_filename = self.env['ir.model.fields'].search([('name', '=', filename)])
                            if binary_filename:
                                binary_filename_data = self.init_data_input(all_fields[binary_filename.name],
                                                                            binary_filename)
                                eview_wrap_group.append(etree.Element('field', binary_filename_data))
                            field_data = self.init_data_input(all_fields[field.name], field)
                            eview_wrap_group_employee.addprevious(etree.Element('field', field_data))

                elif view_type == 'tree':
                    arch_db_eview = etree.XML(res['arch'])
                    annuaire_config_tree = self.env.ref('ooto_annuaire.employee_sect_config_data')
                    if annuaire_config_tree.contact_fields_ids.mapped('fields_id'):
                        eview_wrap_group_tree = False
                        eview_wrap_group_tree = arch_db_eview.xpath("//field[@name='mobile_phone']")[0]
                        for field in annuaire_config_tree.contact_fields_ids.mapped('fields_id'):
                            field_data = self.init_data_input(all_fields[field.name], field)
                            eview_wrap_group_tree.addnext(etree.Element('field', field_data))

                if view_type == 'search':
                    arch_db_eview = etree.XML(res['arch'])
                    annuaire_config_search = self.env.ref('ooto_annuaire.employee_sect_config_data')

                    if annuaire_config_search.contact_fields_ids.mapped('fields_id'):
                        eview_wrap_group_search = False
                        eview_wrap_group_search = arch_db_eview.xpath("//field[@name='mobile_phone']")[0]
                        for field in annuaire_config_search.contact_fields_ids.mapped('fields_id'):
                            field_data = self.init_data_input(all_fields[field.name], field)
                            eview_wrap_group_search.addnext(etree.Element('field', field_data))

                for type in view_types:
                    if type == 'form':
                        for node in arch_db_eview.xpath("//" + type):
                            node.attrib['delete'] = 'false'
                            node.attrib['create'] = 'false'
                            node.attrib['edit'] = 'true'
                    else:
                        for node in arch_db_eview.xpath("//" + type):
                            node.attrib['delete'] = 'false'
                            node.attrib['create'] = 'false'
                            node.attrib['edit'] = 'false'
                res['arch'] = etree.tostring(arch_db_eview)
                return res
            else:
                if view_type == 'form':
                    arch_db_eview = etree.XML(res['arch'])
                    annuaire_config = self.env.ref('ooto_annuaire.employee_sect_config_data')
                    if annuaire_config and annuaire_config.contact_fields_ids.mapped('fields_id'):
                        eview_wrap_group_native = \
                            arch_db_eview.xpath("//page[@name='annuaire']/group[@name='annuaire']")[0]
                        for field in annuaire_config.contact_fields_ids.mapped('fields_id'):
                            filename = "x_filename_of_%s" % field.name
                            binary_filename = self.env['ir.model.fields'].search([('name', '=', filename)])
                            if binary_filename:
                                binary_filename_data = self.init_data_input(all_fields[binary_filename.name],
                                                                            binary_filename)
                                eview_wrap_group_native.append(etree.Element('field', binary_filename_data))

                            field_data = self.init_data_input(all_fields[field.name], field)

                            eview_wrap_group_native.append(etree.Element('field', field_data))
                    if onboarding_model:
                        fields_document = []
                        fields_upload = []

                        onboarding_fields_document = self.env['onboarding.employee.fields.document'].search([])
                        onboarding_fields_upload = self.env['onboarding.employee.fields.upload'].search([])

                        if onboarding_fields_document:
                            ond = set(onboarding_fields_document)
                            for onboarding_employee_fields in ond:

                                if onboarding_employee_fields:
                                    # test = onboarding_employee_fields.mapped('fields_id')
                                    field = onboarding_employee_fields.mapped('fields_id')
                                    if field.name not in fields_document:
                                        fields_document.append(field.name)
                                        if field.state == 'manual':
                                            if field.is_work_information:
                                                eview_wrap_group_native = arch_db_eview.xpath(
                                                    "//page[@name='public']/div/div/group[@name='administrative_work_information']")[
                                                    0]
                                                filename = "x_filename_of_%s" % field.name
                                                binary_filename = self.env['ir.model.fields'].search(
                                                    [('name', '=', filename)])
                                                if binary_filename:
                                                    binary_filename_data = self.init_data_input(
                                                        all_fields[binary_filename.name],
                                                        binary_filename)
                                                    eview_wrap_group_native.append(
                                                        etree.Element('field', binary_filename_data))

                                                field_data = self.init_data_input(all_fields[field.name],
                                                                                  field)

                                                eview_wrap_group_native.append(etree.Element('field', field_data))
                                            elif field.is_personal_information:
                                                eview_wrap_group_native = arch_db_eview.xpath(
                                                    "//page[@name='personal_information']/group/group[@name='administrative_personal_information']")[
                                                    0]
                                                filename = "x_filename_of_%s" % field.name
                                                binary_filename = self.env['ir.model.fields'].search(
                                                    [('name', '=', filename)])
                                                if binary_filename:
                                                    binary_filename_data = self.init_data_input(
                                                        all_fields[binary_filename.name],
                                                        binary_filename)
                                                    eview_wrap_group_native.append(
                                                        etree.Element('field', binary_filename_data))

                                                field_data = self.init_data_input(all_fields[field.name],
                                                                                  field)

                                                eview_wrap_group_native.append(etree.Element('field', field_data))

                        if onboarding_fields_upload:
                            ond = set(onboarding_fields_upload)
                            for onboarding_employee_fields in ond:

                                if onboarding_employee_fields:
                                    # test = onboarding_employee_fields.mapped('fields_id')
                                    field = onboarding_employee_fields.mapped('fields_id')
                                    if field.name not in fields_upload:
                                        fields_upload.append(field.name)
                                        if field.state == 'manual':
                                            if field.is_work_information:
                                                eview_wrap_group_native = arch_db_eview.xpath(
                                                    "//page[@name='public']/div/div/group[@name='administrative_work_information']")[
                                                    0]
                                                filename = "x_filename_of_%s" % field.name
                                                binary_filename = self.env['ir.model.fields'].search(
                                                    [('name', '=', filename)])
                                                if binary_filename:
                                                    binary_filename_data = self.init_data_input(
                                                        all_fields[binary_filename.name],
                                                        binary_filename)
                                                    eview_wrap_group_native.append(
                                                        etree.Element('field', binary_filename_data))

                                                field_data = self.init_data_input(all_fields[field.name],
                                                                                  field)

                                                eview_wrap_group_native.append(etree.Element('field', field_data))
                                            elif field.is_personal_information:
                                                eview_wrap_group_native = arch_db_eview.xpath(
                                                    "//page[@name='personal_information']/group/group[@name='administrative_personal_information']")[
                                                    0]
                                                filename = "x_filename_of_%s" % field.name
                                                binary_filename = self.env['ir.model.fields'].search(
                                                    [('name', '=', filename)])
                                                if binary_filename:
                                                    binary_filename_data = self.init_data_input(
                                                        all_fields[binary_filename.name],
                                                        binary_filename)
                                                    eview_wrap_group_native.append(
                                                        etree.Element('field', binary_filename_data))

                                                field_data = self.init_data_input(all_fields[field.name],
                                                                                  field)

                                                eview_wrap_group_native.append(etree.Element('field', field_data))
                        res['arch'] = etree.tostring(arch_db_eview)
                        return res
        elif onboarding_model and not annuaire_config_model:
            if view_type == 'form':
                arch_db_eview = etree.XML(res['arch'])
                fields_document = []
                fields_upload = []

                onboarding_fields_document = self.env['onboarding.employee.fields.document'].search([])
                onboarding_fields_upload = self.env['onboarding.employee.fields.upload'].search([])

                if onboarding_fields_document:
                    ond = set(onboarding_fields_document)
                    for onboarding_employee_fields in ond:

                        if onboarding_employee_fields:
                            # test = onboarding_employee_fields.mapped('fields_id')
                            field = onboarding_employee_fields.mapped('fields_id')
                            if field.name not in fields_document:
                                fields_document.append(field.name)
                                if field.state == 'manual':
                                    if field.is_work_information:
                                        eview_wrap_group_native = arch_db_eview.xpath(
                                            "//page[@name='public']/div/div/group[@name='administrative_work_information']")[
                                            0]
                                        filename = "x_filename_of_%s" % field.name
                                        binary_filename = self.env['ir.model.fields'].search(
                                            [('name', '=', filename)])
                                        if binary_filename:
                                            binary_filename_data = self.init_data_input(
                                                all_fields[binary_filename.name],
                                                binary_filename)
                                            eview_wrap_group_native.append(
                                                etree.Element('field', binary_filename_data))

                                        field_data = self.init_data_input(all_fields[field.name],
                                                                          field)

                                        eview_wrap_group_native.append(etree.Element('field', field_data))
                                    elif field.is_personal_information:
                                        eview_wrap_group_native = arch_db_eview.xpath(
                                            "//page[@name='personal_information']/group/group[@name='administrative_personal_information']")[
                                            0]
                                        filename = "x_filename_of_%s" % field.name
                                        binary_filename = self.env['ir.model.fields'].search(
                                            [('name', '=', filename)])
                                        if binary_filename:
                                            binary_filename_data = self.init_data_input(
                                                all_fields[binary_filename.name],
                                                binary_filename)
                                            eview_wrap_group_native.append(
                                                etree.Element('field', binary_filename_data))

                                        field_data = self.init_data_input(all_fields[field.name],
                                                                          field)

                                        eview_wrap_group_native.append(etree.Element('field', field_data))

                if onboarding_fields_upload:
                    ond = set(onboarding_fields_upload)
                    for onboarding_employee_fields in ond:

                        if onboarding_employee_fields:
                            # test = onboarding_employee_fields.mapped('fields_id')
                            field = onboarding_employee_fields.mapped('fields_id')
                            if field.name not in fields_upload:
                                fields_upload.append(field.name)
                                if field.state == 'manual':
                                    if field.is_work_information:
                                        eview_wrap_group_native = arch_db_eview.xpath(
                                            "//page[@name='public']/div/div/group[@name='administrative_work_information']")[
                                            0]
                                        filename = "x_filename_of_%s" % field.name
                                        binary_filename = self.env['ir.model.fields'].search(
                                            [('name', '=', filename)])
                                        if binary_filename:
                                            binary_filename_data = self.init_data_input(
                                                all_fields[binary_filename.name],
                                                binary_filename)
                                            eview_wrap_group_native.append(
                                                etree.Element('field', binary_filename_data))

                                        field_data = self.init_data_input(all_fields[field.name],
                                                                          field)

                                        eview_wrap_group_native.append(etree.Element('field', field_data))
                                    elif field.is_personal_information:
                                        eview_wrap_group_native = arch_db_eview.xpath(
                                            "//page[@name='personal_information']/group/group[@name='administrative_personal_information']")[
                                            0]
                                        filename = "x_filename_of_%s" % field.name
                                        binary_filename = self.env['ir.model.fields'].search(
                                            [('name', '=', filename)])
                                        if binary_filename:
                                            binary_filename_data = self.init_data_input(
                                                all_fields[binary_filename.name],
                                                binary_filename)
                                            eview_wrap_group_native.append(
                                                etree.Element('field', binary_filename_data))

                                        field_data = self.init_data_input(all_fields[field.name],
                                                                          field)

                                        eview_wrap_group_native.append(etree.Element('field', field_data))
                res['arch'] = etree.tostring(arch_db_eview)
                return res
        return res

    @api.onchange('firstname', 'lastname')
    def onchange_fistname_lastname(self):
        """
        Set name field value on change of firstname and lastname
        :return: None
        """
        for rec in self:
            rec.name = "%s %s" % (self.lastname or '', self.firstname or '')

    @api.model
    def create(self, vals):
        """
        Create employee then create user linked to created employee
        :param vals: new employee values
        :return: result
        """
        if not vals.get('name', False):
            vals.update({'name': "%s %s" % (self.lastname, self.firstname)})
        if vals.get('registration', False):
            # Link new employee to the user created from registration
            del vals['registration']
            user_mail = vals.get('work_email')
            user_id = self.env['res.users'].sudo().search([('login', '=', user_mail)], limit=1)
            vals.update({'user_id': user_id and user_id.id or False})
        elif vals.get('work_email', False):
            # Create linked user
            new_user_id = self.sudo().create_employee_user(vals)
            vals.update({'user_id': new_user_id and new_user_id.id or False})
        return super(HrEmployee, self).create(vals)

    @api.model
    def create_employee_user(self, vals):
        """
        Create user from created employee
        :param vals:
        :return:
        """
        # Variable initialization
        main_company_id = self.env.ref('base.main_company').id
        company_id = vals.get('company_id', main_company_id)
        current_vals = {
            'lastname': vals.get('lastname'),
            'firstname': vals.get('firstname'),
            'name': vals.get('name'),
            'login': vals.get('work_email'),
            'email': vals.get('work_email'),
            'image_1920': vals.get('image_1920', False),
            'active': True,
            'not_send_mail': vals.get('not_send_mail', False),
            'no_reset_mail': vals.get('no_reset_mail', False),
            'company_id': company_id,
            'company_ids': [(6, 0, [company_id, main_company_id])]
        }
        if not vals.get('image_1920', False):
            image_binary = self.create_image(vals.get('name'))
            current_vals.update({'image_1920': image_binary})
        # Create user from template user
        new_user = self.env['res.users']._create_user_from_template(current_vals)
        return new_user

    @api.model
    def init_data_input(self, res_field, field):
        data = {
            'name': field.name,
            'options': '{"size" : [10, 10]}',
        }
        modifiers = {}

        if res_field['type'] == 'binary':
            # For file fields

            data.update({
                'filename': "x_filename_of_%s" % field.name,
            })

        if res_field['type'] == 'selection':
            # For file fields
            data.update({
                'widget': "selection",
            })

        if res_field['required']:
            data.update({
                'required': "1",
            })
            modifiers['required'] = True

        if res_field['type'] == 'char' and "x_filename_of" in field.name:
            data.update({
                'invisible': "1",
            })
            modifiers['invisible'] = True

        # if res_field['readonly'] or res_field['type'] == 'boolean' :
        #     domain_readonly = []
        #
        #     if not field.is_compute:
        #         data.update({
        #             # 'readonly': "1",
        #             "force_save": "1"
        #         })
        #         if res_field['type'] in ['integer', 'float']:
        #             domain_readonly = [(field.name, '!=', 0)]
        #         #      For opt in checkbox where chackbox is readonly
        #         elif res_field['type'] == 'boolean' :
        #             domain_readonly = [(field.name, '=', True)]
        #
        #         else:
        #             domain_readonly = [(field.name, '!=', False)]
        #     else:
        #         domain_readonly = True
        #
        #     modifiers['readonly'] = domain_readonly
        #
        # Add modifiers into data dumps it into json data
        if modifiers:
            data['modifiers'] = json.dumps(modifiers)

        return data
