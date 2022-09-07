# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import ValidationError
from odoo.osv import expression
from odoo.tools import config
from odoo.tools.safe_eval import safe_eval

active_model = {}


class DynamicBypassRule(models.Model):
    _name = 'dynamic.bypass.rule'
    _description = 'Dynamic bypass rule'
    _rec_name = 'model_id'

    model_id = fields.Many2one('ir.model', 'Select Main Model', copy=False,
                               help='Model on which you want to bypass the record rule.')
    model_ids = fields.Many2many('ir.model', string='Relational Models',
                                 help='Relational models for which you want to bypass the record rule.')

    @api.onchange('model_id')
    def onchange_model_id(self):
        self.model_ids = [(6, 0, [])]
