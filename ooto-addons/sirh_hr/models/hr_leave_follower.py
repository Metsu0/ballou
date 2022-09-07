# -*- coding: utf-8 -*-
from odoo import api, fields, models


class LeaveFollower(models.Model):
    _name = 'hr.leave.follower'

    admin_follower = fields.Many2one('hr.employee', string='Admin Leave Follower', required=True)