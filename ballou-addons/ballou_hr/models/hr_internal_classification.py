# coding: utf-8

from odoo import models, fields, _, api


class HrInternalClassification(models.Model):
    _name = 'hr.internal.classification'
    _description = 'Internal classification'

    name = fields.Char(String='Name', required=1)