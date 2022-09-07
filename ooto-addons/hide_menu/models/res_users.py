# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _

class resUsers(models.Model):
    _inherit = 'res.users'

    menu_hide_ids = fields.Many2many('ir.ui.menu', 'res_user_menu_hide_rel', 'user_id', 'menu_hide_id', string='Menu to hide')