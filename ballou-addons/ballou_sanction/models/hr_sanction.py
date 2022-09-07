# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrSanction(models.Model):
    _name = 'hr.sanction'

    name = fields.Char(string='Name', required=True)
    motif = fields.Text(string="Motif")
    type_id = fields.Many2one(comodel_name="hr.sanction.type", string="Type", required=True, default=lambda self: self.env.ref('ballou_sanction.sanction_information').id)
    delivery_date = fields.Date(string="Delivery date", required=True, default=fields.Date.context_today)
    end_date = fields.Date(string="End date", required=True)
    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee", required=True, )
    company_id = fields.Many2one(comodel_name="res.company", string="Company", related="employee_id.company_id", store=True)
    department_id = fields.Many2one(comodel_name="hr.department", string="Service",
                                    related="employee_id.department_id", store=True)
    department_parent_id = fields.Many2one(comodel_name="hr.department", string="Département parent",
                                           related="employee_id.department_id.parent_id", store=True)


class HrSanctionType(models.Model):
    _name = 'hr.sanction.type'

    name = fields.Char(string="Name", required=True, translate=True)
