# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class HrPayslipConfig(models.Model):
    _inherit = 'hr.payslip.config'

    def generate_payslip_resume(self):
        self.ensure_one()
        self.payslip_resume_ids.unlink()
        domain = [('date_from', '>=', self.date_from), ('date_to', '<=', self.date_to)]
        payslip_obj = self.env['hr.payslip']
        payslips = payslip_obj.sudo().search(domain)
        new_payslips = []
        # get dynamic model column
        ir_model_fields = self.env['ir.model.fields'].sudo().search(
            [('name', '=like', 'x_%'), ('model_id', '=', self.env['ir.model']._get_id('payslip.resume'))])
        ir_model_fields = ir_model_fields.filtered(lambda f: f.name[0:2] == 'x_')
        ir_model_fields_name = [f.name[2:] for f in ir_model_fields]
        payslip_resume_columns = self.env['payslip.resume.column'].search([])
        # ('appears_in_payslip_resume', '=', True)
        for payslip_resume_column in payslip_resume_columns or []:
            if payslip_resume_column.code.lower() in ir_model_fields_name or []:
                # pass
                if not payslip_resume_column.appears_in_payslip_resume:
                    ir_model_field = self.env['ir.model.fields'].sudo().search(
                        [('name', '=', 'x_' + payslip_resume_column.code.lower())], limit=1)
                    # ir_model_field = ir_model_fields.filtered(
                    #     lambda f: f.name == 'x_' + hr_salary_rule.code.lower())
                    if ir_model_field:
                        self.env['ir.model.fields'].sudo().browse(ir_model_field.id).unlink()
                        ir_model_fields_name.pop(ir_model_fields_name.index(payslip_resume_column.code.lower()))

            else:
                # pass
                if payslip_resume_column.appears_in_payslip_resume:
                    self.env['ir.model.fields'].create({
                        'name': 'x_' + payslip_resume_column.code.lower(),
                        'model_id': self.env['ir.model']._get_id('payslip.resume'),
                        'ttype': 'float',

                    })
        for payslip in payslips:
            payslip_lines = payslip.mapped('line_ids')
            payslip_input_lines = payslip.mapped('input_line_ids')
            values = {'payslip_config_id': self.id,
                      'payslip_reference': payslip.number,
                      'employee_id': payslip.employee_id.id if payslip.employee_id else False,
                      'department_id': payslip.employee_id.department_id.id if payslip.employee_id and payslip.employee_id.department_id else False,
                      'department_parent_id': payslip.employee_id.department_id.parent_id.id if payslip.employee_id and payslip.employee_id.department_id and payslip.employee_id.department_id.parent_id else False,
                      'company_id': payslip.company_id.id,
                      'nom_employe': payslip.employee_id.name if payslip.employee_id else False,
                      'poste': payslip.employee_id.job_id.name if payslip.employee_id and payslip.employee_id.job_id else '',
                      'matricule': payslip.employee_id.registration_number if payslip.employee_id else '',
                      'sexe': payslip.employee_id.gender if payslip.employee_id else '',
                      'numero_cnaps': payslip.employee_id.cnaps_number if payslip.employee_id else '',
                      'numero_cin': payslip.employee_id.identification_id if payslip.employee_id else '',
                      'nom_lot_bulletin': payslip.payslip_run_id.name if payslip.payslip_run_id else '',
                      'lot_bulletin_id': payslip.payslip_run_id.id if payslip.payslip_run_id else '',
                      'payslip_run_id': payslip.payslip_run_id.id if payslip.payslip_run_id else False,
                      'code_banque': payslip.employee_id.bank_account_id.bank_id.bic if payslip.employee_id and payslip.employee_id.bank_account_id else '',
                      'guichet': payslip.employee_id.bank_account_id.agency_code if payslip.employee_id and payslip.employee_id.bank_account_id else '',
                      'numero_compte': payslip.employee_id.bank_account_id.acc_number if payslip.employee_id and payslip.employee_id.bank_account_id else '',
                      'banque': payslip.employee_id.bank_account_id.bank_id.name if payslip.employee_id and payslip.employee_id.bank_account_id and payslip.employee_id.bank_account_id.bank_id else '',
                      'debut_fiche_bulletin': payslip.date_from,
                      'fin_fiche_bulletin': payslip.date_to,
                      'mode_paiement': payslip.contract_id.payslip_payment_mode_id.name if payslip.contract_id and payslip.contract_id.payslip_payment_mode_id else '',
                      'etat_bulletin': payslip.state,
                      # 'test': sum([hpi.amount for hpi in payslip_input_lines.filtered(lambda l: l.code == 'AUG')]),

                      'sb': sum([hpl.total for hpl in payslip_lines.filtered(
                          lambda l: l.code in ('BASIC', 'BASIC_SANS_OSTIE', 'BASIC_SANS_OSTIE_SANS_CNAPS'))]),
                      'tj': sum([hpl.total for hpl in payslip_lines.filtered(
                          lambda l: l.code in ('TJ', 'TJ_SANS_OSTIE', 'TJ_SANS_OSTIE_SANS_CNAPS'))]),
                      'th': sum([hpl.total for hpl in payslip_lines.filtered(
                          lambda l: l.code in ('TH', 'TH_SANS_OSTIE', 'TH_SANS_OSTIE_SANS_CNAPS'))]), }

            ir_model_fields_to_show = self.env['ir.model.fields'].sudo().search(
                [('name', '=like', 'x_%'), ('model_id', '=', self.env['ir.model']._get_id('payslip.resume'))])
            if ir_model_fields_to_show:
                model_column_tuple = [(f.name, [x for x in payslip_resume_columns if x.code.lower() == f.name[2:]])
                                      for f in
                                      ir_model_fields_to_show or []]
                model_column_tuple = [(k, [x.code for x in v[0].hr_salary_rule_ids]) for k, v in model_column_tuple if
                                      v]

                model_dict = {k: sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in v)]) for k, v in
                              model_column_tuple}

                if model_dict:
                    values.update(model_dict)

            new_payslips.append(values)

        if new_payslips:
            print(new_payslips)
            self.env['payslip.resume'].create(new_payslips)
