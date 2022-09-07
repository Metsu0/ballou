# -*- coding: utf-8 -*-

from odoo import fields, models, _


class HrContractCategory(models.Model):
    _name = 'hr.contract.category'
    _description = 'Contract category (ex: HC)'

    name = fields.Char(string='Name', required=True)
    note = fields.Text(string='Description')
    contract_ids = fields.One2many('hr.contract', 'contract_category_id', 'Contracts')
    group = fields.Selection([
        ('group_1', _('Group 1')),
        ('group_2', _('Group 2')),
        ('group_3', _('Group 3')),
        ('group_4', _('Group 4')),
        ('group_5', _('Group 5')),
    ])
    active = fields.Boolean('Active', default=True)
