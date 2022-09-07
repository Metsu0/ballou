# -*- encoding: utf-8 -*-
from odoo import models, fields

class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    parent_id = fields.Many2one(comodel_name='hr.salary.rule', 
                                                    string='Basic Salary Rule', 
                                                    ondelete='restrict', 
                                                    index=True, 
                                                    default=False)
    show_on_amount_column = fields.Boolean(default=True)
    amount_column_position = fields.Selection([('left','Left'), ('right','Right')], 
                                                                            default='left')
    regulatory_deduction = fields.Boolean(default=False)