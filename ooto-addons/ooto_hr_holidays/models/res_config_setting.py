# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    day_exceptional_permission = fields.Integer("Exceptional permission day")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['day_exceptional_permission'] = int(self.env['ir.config_parameter'].sudo().get_param(
            'ooto_hr_holidays.day_exceptional_permission', 0))
        return res

    @api.model
    def set_values(self):
        day_ex = self.day_exceptional_permission
        self.env['ir.config_parameter'].sudo().set_param('ooto_hr_holidays.day_exceptional_permission', day_ex)
        super(ResConfigSettings, self).set_values()
