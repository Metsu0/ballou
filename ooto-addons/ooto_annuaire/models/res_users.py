# -*- coding: utf-8 -*-

from odoo import fields, models, api


class Users(models.Model):
    _inherit = "res.users"

    def _get_default_contacts(self):
        rules_ids = self.env['ooto.annuaire.rules'].search([])
        employees = self.env['hr.employee'].search([])
        if not rules_ids:
            return employees

    visible_contact_employee_ids = fields.Many2many(
        "hr.employee",
        string="Visible contact",
        copy=False,
        store=True,
        default=_get_default_contacts
    )
    is_connected_front = fields.Boolean('Is connected to front')

    @api.model
    def set_is_connected_front(self, value):
        """
        Set value of is_connected_front field
        :return:
        """
        self.env.user.is_connected_front = value

    @api.model
    def get_is_connected_front(self):
        """
        Get value of is_connected_front field
        :return:
        """
        return self.env.user.is_connected_front
