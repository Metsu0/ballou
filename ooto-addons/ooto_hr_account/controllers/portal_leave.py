# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.portal_leave.controllers.main import CustomerPortal as CustomerPortalLeave
from odoo.http import request, route

_logger = logging.getLogger(__name__)


class CustomerPortalLeave(CustomerPortalLeave):

    def _prepare_portal_layout_values(self):
        values = CustomerPortal()._prepare_portal_layout_values()
        user = request.env.user
        employees = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)])
        for employee in employees:
            domain = [('employee_id', '=', employee.id)]
            values['leave_count'] = request.env['hr.leave'].sudo().search_count(domain)
        return values
