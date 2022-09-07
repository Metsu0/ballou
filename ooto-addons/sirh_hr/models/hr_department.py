# -*- coding: utf-8 -*-

import base64
import logging

from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError, AccessError
from odoo.modules.module import get_module_resource

_logger = logging.getLogger(__name__)


class DepartmentInherit(models.Model):
    _inherit = 'hr.department'

    code = fields.Char(string='Code')
    deputy_ids = fields.Many2many('hr.employee', string='Deputy')
    direction_id = fields.Many2one('hr.direction', string='Direction')
    default_company_ids = fields.Many2many('res.company', default=lambda self: self.env.user.company_ids)
    company_ids = fields.Many2many('res.company', compute='_compute_default_company_ids')
    is_rrh = fields.Boolean(string="is rrh", compute="_compute_deputy_ids", store=True)

    @api.onchange('manager_id')
    def _compute_default_company_ids(self):
        self.company_ids = self.env.ref('base.main_company')

    @api.depends('deputy_ids')
    def _compute_deputy_ids(self):
        deputy_ids = self.env['hr.department'].search([]).mapped('deputy_ids')
        not_deputy_ids = self.env['hr.employee'].search([('id', 'not in', deputy_ids.mapped('id'))])
        for deputy_id in deputy_ids:
            deputy_id.is_rrh = True
        for not_deputy_id in not_deputy_ids:
            not_deputy_id.is_rrh = False
