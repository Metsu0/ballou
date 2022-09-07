# -*- coding: utf-8 -*-
from lxml import etree
from odoo import api, fields, models, tools


class PayslipResume(models.Model):
    _inherit = "payslip.resume"
    _description = "Hr Payslip Report"

    @api.model
    def _fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(PayslipResume, self)._fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                          submenu=submenu)
        if view_type == 'tree':
            ir_model_fields = self.env['ir.model.fields'].sudo().search(
                [('name', '=like', 'x_%'), ('model_id', '=', self.env['ir.model']._get_id('payslip.resume'))])
            ir_model_fields = ir_model_fields.filtered(lambda f: f.name[0:2] == 'x_')
            # ir_model_fields_name = [f.name[2:] for f in ir_model_fields]
            payslip_resume_columns = self.env['payslip.resume.column'].search([])

            ir_model_fields_to_show = self.env['ir.model.fields'].sudo().search(
                [('name', '=like', 'x_%'), ('model_id', '=', self.env['ir.model']._get_id('payslip.resume'))])
            if ir_model_fields_to_show:
                model_tuple = [(f.name, [x.name for x in payslip_resume_columns if x.code.lower() == f.name[2:]]) for f
                               in
                               ir_model_fields_to_show or []]
                model_tuple = [(k, v[0]) for k, v in model_tuple if v]
                eview = etree.fromstring(res['arch'])
                summary = eview.xpath("//field[@name='fin_fiche_bulletin']")
                if len(summary):
                    summary = summary[0]
                    for n, s in model_tuple:
                        summary.addnext(etree.Element('field', {'name': n, 'string': s, }))
                res['arch'] = etree.tostring(eview)

        return res


class PayslipResumeColumn(models.Model):
    _name = "payslip.resume.column"
    _description = "Hr Payslip Report dynamic column"

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    hr_salary_rule_ids = fields.Many2many('hr.salary.rule', column1='payslip_resume_column_id',
                                          column2='hr_salary_rule_id', required=True)
    appears_in_payslip_resume = fields.Boolean(default=False)
