# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	justificatory_size = fields.Integer(string='Justificatory Size',
	                                    config_parameter='ooto_hr_holidays_front._get_justificatory_size')

	@api.model
	def _get_justificatory_size(self):
		return self.env['ir.config_parameter'].sudo().get_param('ooto_hr_holidays_front._get_justificatory_size', '')
