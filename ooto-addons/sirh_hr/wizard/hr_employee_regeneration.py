# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import UserError


class RegenerateDirection(models.TransientModel):
    _name = "hr.employee.regen"
    _description = "For the re write of direction value"

    def regen_direction(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []

        for record in self.env['hr.employee'].browse(active_ids):
            if record.department_id:
                if record.department_id.direction_id:
                    record.write({'direction_id': record.department_id.direction_id.id})
                    # record.direction_id = record.department_id.direction_id.id
        return {'type': 'ir.actions.act_window_close'}