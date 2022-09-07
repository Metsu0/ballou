# -*- coding: utf-8 -*-

import base64

from odoo import models, fields, api, modules, _
from odoo.exceptions import UserError


class AnnuaireEmployeeSection(models.Model):
    _name = 'annuaire.employee.section'
    _description = 'Annuaire configuration employee section'

    fields_id = fields.Many2one(
        'ir.model.fields',
        string="Field name",
        domain="[('model', '=', 'hr.employee'), ('store', '=', True), ('ttype', 'not in', ['many2many', 'one2many', 'reference'])]"
    )
    an_configuration_id_1 = fields.Many2one('annuaire.configuration', sting="Configuration")
    is_visible_front_employee = fields.Boolean(string="Visible front", )
    is_readonly = fields.Boolean(string="Is readonly", default=False)

    @api.onchange('is_visible_front_employee')
    def on_change_employee_fields_id(self):
        if self.fields_id and self.is_visible_front_employee:
            self.fields_id.sudo().write({'is_visible_front_employee': True})

    def unlink(self):
        if self.id == self.env.ref("ooto_annuaire.image_employee_section_data").id or self.id == self.env.ref(
                'ooto_annuaire.work_email_employee_section_data').id or self.id == self.env.ref(
                'ooto_annuaire.name_employee_section_data').id:
            raise UserError(_('You can not remove image, name or email'))
        else:
            fields_id = self.mapped("fields_id")
            fields_id.write({'is_visible_front_employee': False})

        return super(AnnuaireEmployeeSection, self).unlink()


class AnnuaireConfigurationAssociatedContacts(models.Model):
    _name = 'annuaire.associated.contacts'
    _description = 'Annuaire configuration associated contacts'

    def _get_default_image(self):
        image_path = modules.get_module_resource('ooto_annuaire', 'static/src/img', 'default_logo_contact.svg')
        return base64.b64encode(open(image_path, 'rb').read())

    fields_id = fields.Many2one(
        'ir.model.fields',
        string="Field name",
        domain="[('model', '=', 'hr.employee'), ('store', '=', True), ('ttype', 'not in', ['many2many', 'one2many', 'reference'])]"
    )
    an_configuration_id_2 = fields.Many2one('annuaire.configuration', string="Configuration")
    is_visible_front_contact = fields.Boolean(string="Visible front", )
    logo = fields.Binary("logo", required=True, default=_get_default_image)
    employee_id = fields.Many2one('hr.employee', string="Employee")

    @api.onchange('is_visible_front_contact')
    def on_change_contact_fields_id(self):
        if self.fields_id and self.is_visible_front_contact:
            self.fields_id.sudo().write({'is_visible_front_contact': True})

    def unlink(self):
        fields_id = self.mapped("fields_id")
        fields_id.write({'is_visible_front_contact': False})

        return super(AnnuaireConfigurationAssociatedContacts, self).unlink()


class AnnuaireConfiguration(models.Model):
    _name = 'annuaire.configuration'
    _description = 'Annuaire configuration'

    name = fields.Char(readonly=True)
    employees_fields_ids = fields.One2many(
        'annuaire.employee.section',
        'an_configuration_id_1',
        string="Section employee"
    )
    contact_fields_ids = fields.One2many(
        'annuaire.associated.contacts',
        'an_configuration_id_2',
        string="Associated Contact"
    )
