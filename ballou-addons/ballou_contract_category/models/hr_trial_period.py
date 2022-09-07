# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError


class HrTrialPeriod(models.Model):
    _name = 'hr.trial.period'

    name = fields.Char(string="Name")
    state = fields.Selection([
        ('progress', 'In progress'),
        ('renew', 'Renew'),
        ('validate', 'Validate'),
        ('refuse', 'Refuse')
    ], string='Status')
    start_date = fields.Date(string="Start date", default=fields.Date.context_today)
    end_date = fields.Date(string="End date", compute="_get_end_date")
    duration = fields.Float(string="Duration",  related="group_id.month" )
    contract_id = fields.Many2one(comodel_name="hr.contract", string="Contract")
    group_id = fields.Many2one(comodel_name="hr.contract.group", string="Group", required=False, )

    @api.depends('contract_id.category_id', 'contract_id.group_id')
    def _get_end_date(self):
        for rec in self:
            if rec.start_date and rec.duration:
                rec.end_date = rec.start_date + relativedelta(months=+int(rec.duration))
            else:
                raise UserError(_(
                    "Veuillez renseigner une categorie Professionnel au Contrat de l'employer"
                ) )

    @api.constrains('contract_id', 'state')
    def _check_current_contract(self):
        for rec in self:
            domain = [('id', '!=', rec.id), ('contract_id', '=', rec.contract_id.id), ('state', 'not in', ['renew', False, 'refuse']), ('state', '=', rec.state)]
            if rec.search_count(domain):
                raise ValidationError(
                    _('A contract cannot have two trial periods at the same status. (Excluding Renew)'))





