# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrContractCategory(models.Model):
    _name = 'hr.contract.category'

    name = fields.Char(string="Name")
    # group = fields.Selection(string="Group", selection=[('group_1', 'Group 1'), ('group_2', 'Group 2'),
    #                                                     ('group_3', 'Group 3'), ('group_4', 'Group 4'),
    #                                                     ('group_5', 'Group 5')
    #                                                     ], required=False, )
    group_id = fields.Many2one(comodel_name="hr.contract.group", string="Groupe")
    description = fields.Text(string="Description")


class HrContractGroup(models.Model):
    _name = 'hr.contract.group'

    name = fields.Char(string="Name", required=True, translate=True)
    month = fields.Float(string="Duration",  required=True, )


class HrContract(models.Model):
    _inherit = 'hr.contract'

    category_id = fields.Many2one(comodel_name="hr.contract.category", string="Catégorie Professionelle", required=True, )
    group_id = fields.Many2one(comodel_name="hr.contract.group", string="Groupe", related="category_id.group_id", store=True)
    period_ids = fields.One2many(comodel_name="hr.trial.period", inverse_name="contract_id", string="Trial Period")

    @api.onchange('category_id')
    def _onchange_category_id(self):
        if self.period_ids:
            for line in self.period_ids:
                line.group_id = self.group_id.id


