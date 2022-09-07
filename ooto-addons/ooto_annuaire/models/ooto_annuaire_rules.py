# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.tools.safe_eval import safe_eval


class OotoAnnuaireRules(models.Model):
    _name = "ooto.annuaire.rules"
    _description = "OOTO ANNUAIRE RULES"
    

    name = fields.Char("Title")
    target_employee_number = fields.Integer(string="Number of target collaborator", default=0, copy=False)
    visible_contact_number = fields.Integer(string="Number of visible contact", default=0, copy=False)
    target_employee_ids = fields.Many2many("hr.employee", 'employe_ooto_rules_rel_1', 'emp_id_1', 'rule_id_1',
                                           string="Target employee", copy=False)
    visible_contact_employee_ids = fields.Many2many("hr.employee", string="Visible contact", copy=False)
    target_employee_domain = fields.Char(string="Target employee domain", default="[]", copy=False)
    visible_contact_domain = fields.Char(string="Visible contact domain", default="[]", copy=False)
    emp_id_1 = fields.Many2one('hr.employee', string='Employee')

    @api.onchange('target_employee_domain', 'visible_contact_domain')
    def onchange_target_employee_domain(self):
        if self.target_employee_domain and self.visible_contact_domain:
            domain_employee = safe_eval(self.target_employee_domain)
            target_employee_ids = self.env['hr.employee'].search(domain_employee).ids
            self.target_employee_ids = [(6, 0, target_employee_ids)]
            self.target_employee_number = len(target_employee_ids)
 
            domain_contact = safe_eval(self.visible_contact_domain)
            visible_contact_employee_ids = self.env['hr.employee'].search(domain_contact).ids
            self.visible_contact_employee_ids = [(6, 0, visible_contact_employee_ids)]
            self.visible_contact_number = len(visible_contact_employee_ids)
 
    def write(self, values):
        if values.get('target_employee_domain', False) and values.get('visible_contact_domain', False):
            old_employees = self.env['hr.employee'].search(safe_eval(self.target_employee_domain))
            rules = self.search([('id', '!=', self.id), ('target_employee_ids', 'in', old_employees.ids)])
            old_user_contacts = rules.mapped("visible_contact_employee_ids")
            old_users = old_employees.mapped("user_id")
            for user in old_users:
                user.write({'visible_contact_employee_ids': [(6, 0, old_user_contacts.ids)]})
            employees = self.env['hr.employee'].search(safe_eval(values.get('target_employee_domain', False)))
            contacts = self.env['hr.employee'].search(safe_eval(values.get('visible_contact_domain', False)))
            users = employees.mapped('user_id')
            for user in users:
                employe = []
                employe.append(user.visible_contact_employee_ids.ids)
                employe.append(contacts.ids)
                user.write({'visible_contact_employee_ids': [(6, 0, employe[0] + employe[1])]})
 
        elif values.get('target_employee_domain', False) and not values.get('visible_contact_domain', False):
            old_employees = self.env['hr.employee'].search(safe_eval(self.target_employee_domain))
            rules = self.search([('id', '!=', self.id), ('target_employee_ids', 'in', old_employees.ids)])
            old_user_contacts = rules.mapped("visible_contact_employee_ids")
            old_users = old_employees.mapped("user_id")
            for user in old_users:
                user.write({'visible_contact_employee_ids': [(6, 0, old_user_contacts.ids)]})
            employees = self.env['hr.employee'].search(safe_eval(values.get('target_employee_domain', False)))
            contacts = self.env['hr.employee'].search(safe_eval(self.visible_contact_domain))
            users = employees.mapped('user_id')
            for user in users:
                employe = []
                employe.append(user.visible_contact_employee_ids.ids)
                employe.append(contacts.ids)
                user.write({'visible_contact_employee_ids': [(6, 0, employe[0] + employe[1])]})
 
        elif not values.get('target_employee_domain', False) and values.get('visible_contact_domain', False):
            employees = self.env['hr.employee'].search(safe_eval(self.target_employee_domain))
            contacts = self.env['hr.employee'].search(safe_eval(values.get('visible_contact_domain', False)))
            rules = self.search([('id', '!=', self.id), ('target_employee_ids', 'in', employees.ids)])
            all_contacts = rules.mapped("visible_contact_employee_ids")
            users = employees.mapped('user_id')
            for user in users:
                employe = []
                employe.append(all_contacts.ids)
                employe.append(contacts.ids)
                user.write({'visible_contact_employee_ids': [(6, 0, employe[0] + employe[1])]})
 
        elif not values.get('target_employee_domain', False) and not values.get('visible_contact_domain', False):
            employees = self.env['hr.employee'].search(safe_eval(self.target_employee_domain))
            contacts = self.env['hr.employee'].search(safe_eval(self.visible_contact_domain))
            users = employees.mapped('user_id')
            for user in users:
                employe = []
                employe.append(user.visible_contact_employee_ids.ids)
                employe.append(contacts.ids)
                user.write({'visible_contact_employee_ids': [(6, 0, employe[0] + employe[1])]})
 
        return super(OotoAnnuaireRules, self).write(values)
 
    @api.model
    def create(self, values):
        res = super(OotoAnnuaireRules, self).create(values)
        rules = self.search([])
        empty_employees = self.env['hr.employee'].search([('is_empty', '=', False)])
        if len(rules) == 1:
            users = self.env['res.users'].search([])
            for user in users:
                user.write({'visible_contact_employee_ids': [(6, 0, empty_employees.ids)]})
 
        if res.target_employee_ids or res.visible_contact_employee_ids:
            users = res.target_employee_ids.mapped('user_id')
            visible_contact_employee_ids = []
            for rule_visible_cnt_emp in res.visible_contact_employee_ids:
                visible_contact_employee_ids.append(rule_visible_cnt_emp.id)
            for user in users:
                employee = [user.visible_contact_employee_ids.ids, res.visible_contact_employee_ids.ids]
                for user_contact_emp in user.visible_contact_employee_ids:
                    visible_contact_employee_ids.append(user_contact_emp.id)
                user.write({'visible_contact_employee_ids': [(6, 0, visible_contact_employee_ids)]})
        return res
 
    def unlink(self):
        employees = self.env['hr.employee'].search([('is_empty', '=', False)])
        all_employees = self.env['hr.employee'].search([])
        rules_all = self.search([])
 
        if rules_all == self:
            users = self.env['res.users'].search([])
            for user in users:
                user.write({'visible_contact_employee_ids': [(6, 0, all_employees.ids)]})
        else:
            employees_to_delete = self.mapped('target_employee_ids')
            users = employees_to_delete.mapped("user_id")
            for user in users:
                user.write({'visible_contact_employee_ids': [(6, 0, employees.ids)]})
 
            for rules in self:
                employees = employees + rules.target_employee_ids
 
            empty_employee = self.env['hr.employee'].search([('is_empty', '=', False)])
            rules = self.search([('id', 'not in', self.ids), ('target_employee_ids', 'in', employees.ids)])
            if not rules:
                rule_employees = self.mapped('target_employee_ids')
                users = rule_employees.mapped("user_id")
                for user in users:
                    user.write({'visible_contact_employee_ids': [(6, 0, empty_employee.ids)]})
            else:
                rule_employees = rules.mapped('target_employee_ids')
                users = rule_employees.mapped("user_id")
                for user in users:
                    user.write({'visible_contact_employee_ids': [(6, 0, empty_employee.ids)]})
                for rule in rules:
                    rule_employees = rule.mapped('target_employee_ids')
                    users = rule_employees.mapped("user_id")
                    for user in users:
                        contacts = user.visible_contact_employee_ids + rule.mapped('visible_contact_employee_ids')
                        user.write({'visible_contact_employee_ids': [(6, 0, contacts.ids)]})
        return super(OotoAnnuaireRules, self).unlink()
 
    @api.model
    def _default_annuaire(self):
        users = self.env['res.users'].search([])
        employees = self.env['hr.employee'].search([])
        rules = self.env['ooto.annuaire.rules'].search([])
        if not rules:
            for user in users:
                user.write({'visible_contact_employee_ids': [(6, 0, employees.ids)]})
