# -*- coding: utf-8 -*-

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    validator_id = fields.Many2one('hr.onboarding.appointment.postpone', string='Validator')
