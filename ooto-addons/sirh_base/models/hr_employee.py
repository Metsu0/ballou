# -*- coding: utf-8 -*-

from odoo import api, models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    resource_calendar_id = fields.Many2one('resource.calendar',
                                           domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    def write(self, values):
        if values.get('resource_calendar_id', False) and self.sudo().contract_id.resource_calendar_id.id != values.get(
                'resource_calendar_id'):
            self.contract_id.write({'resource_calendar_id': values.get('resource_calendar_id')})
        return super(HrEmployee, self).write(values)
