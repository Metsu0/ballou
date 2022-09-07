# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class IrModelFields(models.Model):
    _inherit = 'ir.model.fields'

    is_personal_information = fields.Boolean('Personal information', default=False)
    is_work_information = fields.Boolean('Work Information', default=False)
    custom_ttype = fields.Selection(string='Custom field type', selection=[
        ('binary', _('binary')),
        ('boolean', _('boolean')),
        ('char', _('char')),
        ('date', _('date')),
        ('datetime', _('date/time')),
        ('float', _('float')),
        ('integer', _('integer')),
        ('selection', _('selection')),
        ('many2one', _('many2one')),
        ('text', _('text')),
    ], onchange='_onchange_custom_ttype')
    can_not_be_modified_by_employee = fields.Boolean(default=False, string="Can not be modified by employee")

    @api.onchange('custom_ttype')
    def _onchange_custom_ttype(self):
        self.ttype = self.custom_ttype
