# -*- coding: utf-8 -*-

from odoo import fields, models


class OnboardingRole(models.Model):
    _name = 'onboarding.role'

    name = fields.Char(string='Name', required=True)
    image = fields.Binary(string='Image')
    image_name = fields.Char(string='Image name')
