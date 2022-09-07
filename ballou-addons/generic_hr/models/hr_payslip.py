# coding: utf-8

import math
from datetime import datetime, date, timedelta
from locale import Error
from dateutil.relativedelta import MO, relativedelta
import calendar
from odoo.exceptions import UserError
from lxml import etree
from odoo import models, fields, api, _


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    leave_allocation = fields.Float(readonly=True,
                                    string='Leave allocation',
                                    compute='_compute_leave_allocation')

    @api.depends('employee_id')
    @api.onchange('employee_id')
    def _compute_leave_allocation(self):
        for payslip in self:
            if payslip.date_from:
                # payslip.leave_allocation = 0
                payslip.leave_allocation = payslip.get_leave_allocation_from_date(payslip.date_from.year)
            else:
                payslip.leave_allocation = 0

    @api.model
    def get_leave_allocation_from_date(self, year):
        # ('employee_id.id', '=',
        #  self.employee_id.id),
        # ('holiday_status_id.validity_start', '>=',
        #  date(
        #      year, 1, 1)),
        # ('holiday_status_id.validity_stop', '<=',
        #  date(year, 12, 31))
        leave_allocations = self.env['hr.leave.allocation'].sudo().search([('state', '=', 'validate'),
                                                                           ('employee_id.id', '=',
                                                                            self.employee_id.id),
                                                                           ('holiday_status_id.display_in_payslip',
                                                                            '=', True),
                                                                           ('holiday_status_id.simple_leave_allocation',
                                                                            '=', True)])

        if not leave_allocations:
            return 0
        leave_allocations_count = sum(
            [leave_allocation.number_of_days - leave_allocation.leaves_taken for leave_allocation in leave_allocations]
        ) if len(leave_allocations) > 0 else leave_allocations.leaves_taken

        # décrémente leave allocation
        payslip_month = self.date_from.month
        number_per_interval = leave_allocations[0].number_per_interval if len(
            leave_allocations) > 0 else leave_allocations.number_per_interval
        current_date = date.today().month
        while payslip_month < current_date:
            leave_allocations_count -= number_per_interval
            payslip_month += 1

        leaves = self.env['hr.leave'].sudo().search(
            [('state', '=', 'validate'), ('employee_id.id', '=', self.employee_id.id),
             ('request_date_from', '<=', self.date_from),
             ('request_date_from', '>', self.date_to)])
        leave_allocations_count -= sum(
            [leave.number_of_days for leave in leaves])

        return leave_allocations_count

    def _fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        """ Set the correct label for `unit_amount`, depending on company UoM """
        res = super(HrPayslip, self)._fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                      submenu=submenu)
        if view_type == 'form':
            params = self.env.context.get('params')
            if params:
                self = self.env['hr.payslip'].browse(params.get('id'))
                is_simple = self.struct_id.simple_leave_allocation
                doc = etree.XML(res['arch'])
                if is_simple:
                    for node in doc.xpath("//field[@name='leave_allocation_current_year']"):
                        node.set('invisible', '1')
                    for node in doc.xpath("//field[@name='leave_allocation_previous_year']"):
                        node.set('invisible', '1')
                    res['arch'] = etree.tostring(doc)
                    eview = etree.fromstring(res['arch'])
                    summary = eview.xpath("//field[@name='struct_id']")
                    if len(summary):
                        summary = summary[0]
                        summary.addnext(etree.Element('field', {'name': 'leave_allocation',
                                                                'string': 'Solde de congé',
                                                                }))
                        res['arch'] = etree.tostring(eview)

        return res
