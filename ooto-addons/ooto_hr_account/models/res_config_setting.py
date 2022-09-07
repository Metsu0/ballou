# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    hide_home = fields.Boolean("Hide home")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['hide_home'] = self.env['ir.config_parameter'].sudo().get_param('ooto_hr_account.hide_home')
        return res

    @api.model
    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param('ooto_hr_account.hide_home', self.hide_home)
        super(ResConfigSettings, self).set_values()
