# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    rule_id_2 = fields.Many2one('ooto.annuaire.rules', string='Rule')
    is_empty = fields.Boolean(string="Is empty", default=True)

    contact_fields_ids = fields.One2many(
        'annuaire.associated.contacts',
        'employee_id',
        compute='_compute_contacts',
        store=False,
        string="Associated Contact"
    )

    def _compute_contacts(self):
        for employee in self:
            configuration = self.env.ref('ooto_annuaire.employee_sect_config_data')
            contacts = configuration.contact_fields_ids.ids
            employee.contact_fields_ids = [(6, 0, contacts)]

    def update_rules(self):
        an_rules = self.env['ooto.annuaire.rules'].search([])

        for rule in an_rules:
            if rule.target_employee_domain:
                domain_employee = safe_eval(rule.target_employee_domain)
                target_employee_ids = self.env['hr.employee'].search(domain_employee).ids
                rule.target_employee_ids = [(6, 0, target_employee_ids)]
                rule.target_employee_number = len(target_employee_ids)

            if rule.visible_contact_domain:
                domain_contact = safe_eval(rule.visible_contact_domain)
                visible_contact_employee_ids = self.env['hr.employee'].search(domain_contact).ids
                rule.visible_contact_employee_ids = [(6, 0, visible_contact_employee_ids)]
                rule.visible_contact_number = len(visible_contact_employee_ids)

            employees = self.env['hr.employee'].search(safe_eval(rule.target_employee_domain))
            user_employee = employees.mapped("user_id")
            for user in user_employee:
                user.write({'visible_contact_employee_ids': [(6, 0, rule.visible_contact_employee_ids.ids)]})

    @api.model
    def create(self, vals):
        emp = super(HrEmployee, self).create(vals)
        self.update_rules()
        return emp

    def write(self, values):
        emp = super(HrEmployee, self).write(values)
        self.update_rules()
        return emp
