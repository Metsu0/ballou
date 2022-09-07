# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrSanctionType(models.Model):
    _inherit = 'hr.sanction.type'

    type = fields.Selection([('caution', 'Avertissement'), ('layoff', 'Mise à pied')])
