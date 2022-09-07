# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta

from odoo import models, fields, _


class HrContract(models.Model):
    _inherit = 'hr.contract'

    renew_date_end_trial = fields.Boolean(string="Renew Trial Date End", default=False)

    def action_renew_trial(self):
        return {
            'name': _('Renew contract template'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.ooto.contract.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
