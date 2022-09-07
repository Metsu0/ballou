# coding: utf-8

from odoo import models, fields


class HrPayslipStructure(models.Model):
    _inherit = 'hr.payroll.structure'

    domain = "[('name','=', gross_daily_id.struct_id.name)]"

    cnaps_employer_id = fields.Many2one('hr.salary.rule', 'CNAPS employer',
                                        domain="[('struct_id.id','=', id)]")
    ostie_employer_id = fields.Many2one('hr.salary.rule', 'OSTIE employer',
                                        domain="[('struct_id.id','=', id)]")
    cnaps_id = fields.Many2one(
        'hr.salary.rule', 'CNAPS employee', domain="[('struct_id.id','=', id)]")
    ostie_id = fields.Many2one(
        'hr.salary.rule', 'OSTIE employee or assimilated', domain="[('struct_id.id','=', id )]")
    fmfp_id = fields.Many2one('hr.salary.rule', 'FMFP',
                              domain="[('struct_id.id','=', id)]")
    irsa_id = fields.Many2one('hr.salary.rule', 'IRSA',
                              domain="[('struct_id.id','=', id)]")
    gross_salary_id = fields.Many2one('hr.salary.rule', 'Gross salary',
                                      domain="[('struct_id.id','=', id)]")
    net_salary_id = fields.Many2one(
        'hr.salary.rule', 'Net salary', domain="[('struct_id.id','=', id)]")
    advantage_ids = fields.Many2many(
        'hr.salary.rule.category', string='Advantage category')
    additional_hour_id = fields.Many2one(
        'hr.salary.rule.category', string='Additional Hour')
    workday_code = fields.Char('Worked days code')
    gross_daily_id = fields.Many2one('hr.salary.rule', 'Gross daily salary',
                                     domain="[('struct_id.id','=', id)]")
    taxable_amount_id = fields.Many2one(
        "hr.salary.rule", string="Taxable Amount", domain="[('struct_id.id', '=', id)]")
    taxable_allowance_ids = fields.Many2many(
        "hr.salary.rule", "taxable_allowance_rel", string="Taxable allowance", domain="[('struct_id.id', '=', id)]")
    non_taxable_allowance_ids = fields.Many2many(
        "hr.salary.rule", "non_taxable_allowance_rel", string="Non taxable allowance", domain="[('struct_id.id', '=', id)]")
    taxable_benefit_in_kind_ids = fields.Many2many(
        "hr.salary.rule", "taxable_benefit_in_kind_rel", string="Taxable benefit in kind", domain="[('struct_id.id', '=', id)]")
    exempt_benefits_in_kind_ids = fields.Many2many(
        "hr.salary.rule", "exempt_benefits_in_kind_rel", string="Exempt benefits in kind", domain="[('struct_id.id', '=', id)]")
    bonus_and_gratuity_ids = fields.Many2many(
        "hr.salary.rule", "bonus_and_gratuity_rel", string="Bonus and gratuity", domain="[('struct_id.id', '=', id)]")
    others_ids = fields.Many2many(
        "hr.salary.rule", "others_rel", string="Others", domain="[('struct_id.id', '=', id)]")
    other_deduction_ids = fields.Many2many(
        "hr.salary.rule", "other_deduction_rel", string="Other deduction", domain="[('struct_id.id', '=', id)]")
    non_taxable_additional_hour = fields.Boolean(
        string="Non taxable additional hour", default=False)