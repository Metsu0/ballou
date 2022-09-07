# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class HrPayrollReport(models.Model):
    _inherit = "hr.payroll.report"

    hourly_rate_productif = fields.Float(
        "Hourly rate productif", readonly=True)
    hourly_rate_non_productif = fields.Float(
        "Hourly rate no productif", readonly=True)

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        employee_productif_ids = self.env["hr_employee"].search([
            '|',
            ("internal_classification.name", "in", ("Productif", "PRODUCTIF")),
            ("category_ids", "in", self.env["hr.employee.category"].search(
                [("name", "in", ("Productif", "PRODUCTIF"))]).ids)
        ]).ids
        employee_non_productif_ids = self.env["hr_employee"].search([
            '|',
            ("internal_classification.name", "in",
             ("Non Productif", "NON PRODUCTIF")),
            ("category_ids", "in", self.env["hr.employee.category"].search(
                [("name", "in", ("Non Productif", "NON PRODUCTIF"))]).ids)
        ]).ids

        fields['hourly_rate_productif'] = ", CASE WHEN wd.id = min_id.min_line THEN plp.total ELSE 0 END as hourly_rate_productif"
        fields['hourly_rate_non_productif'] = ", CASE WHEN wd.id = min_id.min_line THEN plnp.total ELSE 0 END as hourly_rate_non_productif"

        from_clause += '''
            left join hr_payslip_line plp on (plp.slip_id = p.id and (plp.code = 'TH' or plp.code = 'TH_SANS_OSTIE') and plp.employee_id IN %(employee_productif_ids)s)
            left join hr_payslip_line plnp on (plnp.slip_id = p.id and (plnp.code = 'TH' or plnp.code = 'TH_SANS_OSTIE') and plnp.employee_id IN %(employee_non_productif_ids)s)
        '''

        groupby += '''
            , plp.total
            , plnp.total
        '''

        print(fields)

        return super(HrPayrollReport, self)._query(with_clause, fields, groupby, from_clause)
