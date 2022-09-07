# -*- coding: utf-8 -*-
import calendar

import xlsxwriter
from calendar import monthrange
from datetime import date
from odoo import models, fields, api, _


class PayslipStateExport(models.TransientModel):
    _inherit = 'payslip.state.export'
    _description = 'Payslip State Export'

    name = fields.Selection(selection_add=[('annexe_hs', 'Annexe heures supplémentaire')])

    def get_xls_file(self):
        if self.name == 'annexe_hs':
            print("ato no manao PDF Annexe")
            # export PDF
            data = {
                'name': self.name,
                'model_id': self.id,
                'year': self.year,
                'month': self.period,
                'company_id': self.company_id,
            }
            return self.env.ref('generic_hr.action_export_annexe').report_action(self, data=data)
        return super(PayslipStateExport, self).get_xls_file()


class PayslipStateExportPDF(models.AbstractModel):
    _name = "report.generic_hr.payslip_state_pdf_export_template"
    _description = "PDF export"

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env['payslip.state.export'].browse(data.get('model_id'))

        domain = [('date_from', '>=', date(int(data.get('year')), int(data.get('month')), 1)),
                  ('date_to', '<=', date(int(data.get('year')), int(data.get('month')),
                                         monthrange(int(data.get('year')), int(data.get('month')))[1]))]
        hr_payslip_ids = self.env['hr.payslip'].search(domain)
        hr_payslip_employee_ids = self.env['hr.payslip'].read_group(domain, fields=['employee_id'],
                                                                    groupby=['employee_id'])
        irsa_20_in_second = 20 * 3600
        annexe_hs_lines = []
        for hr_payslip_employee_id in hr_payslip_employee_ids:
            employee_id = self.env['hr.employee'].browse(hr_payslip_employee_id['employee_id'][0])
            annexe_hs_line = {'name': employee_id.name,
                              'matricule': employee_id.registration_number if employee_id.registration_number else "",
                              'total_hs': 0, 'hourly_wage': 0, 'hs_30_ni': 0, 'rate_30_ni': 0, 'value_30_ni': 0,
                              'hs_40_ni': 0, 'rate_40_ni': 0, 'value_40_ni': 0, 'hs_50_ni': 0, 'rate_50_ni': 0,
                              'value_50_ni': 0, 'hs_100_ni': 0, 'rate_100_ni': 0, 'value_100_ni': 0, 'hs_30_i': 0,
                              'rate_30_i': 0, 'value_30_i': 0, 'hs_40_i': 0, 'rate_40_i': 0, 'value_40_i': 0,
                              'hs_50_i': 0, 'rate_50_i': 0, 'value_50_i': 0, 'hs_100_i': 0, 'rate_100_i': 0,
                              'value_100_i': 0, 'total_hs_i': 0, 'total_rate_i': 0, 'total_value_i': 0,
                              'total_hs_i_ni': 0}
            hr_contract_list = []

            for hr_payslip_id in hr_payslip_ids.filtered(
                    lambda x: x.employee_id.id == hr_payslip_employee_id['employee_id'][0]):
                old_total_hs = annexe_hs_line.get('total_hs')
                annexe_hs_line.update({'total_hs': old_total_hs + self._convert_to_decimal_hour(
                    sum([self._convert_to_second(x.amount) for x in hr_payslip_id.input_line_ids]))})
                if not hr_payslip_id.contract_id in hr_contract_list:
                    hr_contract_list.append(hr_payslip_id.contract_id)
                tuple_ni = [(x.amount if x.amount <= 8 else 8, x.amount - 8 if x.amount > 8 else 0) for x in
                            hr_payslip_id.input_line_ids.filtered(
                                lambda input: input.code in ('HS_SEM1', 'HS_SEM2', 'HS_SEM3', 'HS_SEM4')) or []]
                ni_30_list = [self._convert_to_second(i) for i, j in tuple_ni]
                ni_50_list = [self._convert_to_second(j) for i, j in tuple_ni]
                ni_sum_list = [self._convert_to_second(i) + self._convert_to_second(j) for i, j in tuple_ni]
                irsa_found = False
                # HS Non imposable 30% et 50 %
                ni_30 = 0
                ni_50 = 0
                for index, value in enumerate(ni_sum_list):
                    temp_sum = sum([x for x in ni_sum_list[:index + 1]])
                    if temp_sum >= irsa_20_in_second and not irsa_found:
                        temp_sum -= ni_50_list[index]
                        if temp_sum <= irsa_20_in_second:
                            temp_sum += ni_50_list[index]
                            rest = temp_sum - irsa_20_in_second
                            ni_50 = sum([x for x in ni_50_list[:index + 1]])
                            ni_50 -= rest
                            ni_30 = sum([x for x in ni_30_list[:index + 1]])
                            old_ni_30 = self._convert_to_second(annexe_hs_line.get('hs_30_ni'))
                            old_ni_50 = self._convert_to_second(annexe_hs_line.get('hs_50_ni'))
                            annexe_hs_line.update({'hs_30_ni': self._convert_to_decimal_hour(old_ni_30 + ni_30),
                                                   'hs_50_ni': self._convert_to_decimal_hour(old_ni_50 + ni_50)})
                            irsa_found = True
                        elif temp_sum >= irsa_20_in_second:
                            temp_sum -= ni_30_list[index]
                            if temp_sum <= irsa_20_in_second:
                                temp_sum += ni_30_list[index]
                                rest = temp_sum - irsa_20_in_second
                                ni_30 = sum([x for x in ni_30_list[:index + 1]])
                                ni_30 -= rest
                                ni_50 = sum([x if x else 0 for x in ni_50_list[:index]])
                                old_ni_30 = self._convert_to_second(annexe_hs_line.get('hs_30_ni'))
                                old_ni_50 = self._convert_to_second(annexe_hs_line.get('hs_50_ni'))
                                annexe_hs_line.update({'hs_30_ni': self._convert_to_decimal_hour(old_ni_30 + ni_30),
                                                       'hs_50_ni': self._convert_to_decimal_hour(old_ni_50 + ni_50)})
                                irsa_found = True
                # ####################
                # HS Non imposable 40% et 50%

                # HS Imposable 30% et 50%
                i_30 = sum(ni_30_list) - ni_30
                i_50 = sum(ni_50_list) - ni_50
                old_i_30 = self._convert_to_second(annexe_hs_line.get('hs_30_i'))
                old_i_50 = self._convert_to_second(annexe_hs_line.get('hs_50_i'))
                annexe_hs_line.update({'hs_30_i': self._convert_to_decimal_hour(old_i_30 + i_30),
                                       'hs_50_i': self._convert_to_decimal_hour(old_i_50 + i_50)})
                # HS Imposable 40% et 50%
                old_i_40 = self._convert_to_second(annexe_hs_line.get('hs_40_i'))
                old_i_100 = self._convert_to_second(annexe_hs_line.get('hs_100_i'))
                i_40 = self._convert_to_second(
                    sum([x.amount for x in hr_payslip_id.input_line_ids.filtered(lambda input: input.code == 'MD_40')]))
                i_100 = self._convert_to_second(sum([x.amount for x in hr_payslip_id.input_line_ids.filtered(
                    lambda input: input.code == 'MF_100')]))
                annexe_hs_line.update({'hs_40_i': self._convert_to_decimal_hour(old_i_40 + i_40),
                                       'hs_100_i': self._convert_to_decimal_hour(old_i_100 + i_100)})
                print(hr_payslip_id)
            if hr_contract_list and len(hr_contract_list) == 1:
                hr_contract_id = hr_contract_list[0]
                if hr_contract_id.employee_id == employee_id:
                    if hr_contract_id.wage_type == 'monthly':
                        annexe_hs_line.update({'hourly_wage': self._float_2(hr_contract_id.wage / 173.33)})
                    elif hr_contract_id.wage_type == 'hourly':
                        annexe_hs_line.update({'hourly_wage': self._float_2(hr_contract_id.wage)})

            # ####################
            # Taux
            hourly_wage = annexe_hs_line.get('hourly_wage')
            annexe_hs_line.update({'rate_30_ni': self._float_2(hourly_wage * 1.3),
                                   'rate_40_ni': self._float_2(hourly_wage * 0.4),
                                   'rate_50_ni': self._float_2(hourly_wage * 1.5),
                                   'rate_100_ni': self._float_2(hourly_wage * 2),
                                   'rate_30_i': self._float_2(hourly_wage * 1.3),
                                   'rate_40_i': self._float_2(hourly_wage * 0.4),
                                   'rate_50_i': self._float_2(hourly_wage * 1.5),
                                   'rate_100_i': self._float_2(hourly_wage * 2)})
            # Valeur
            annexe_hs_line.update(
                {'value_30_ni': self._float_2(annexe_hs_line.get('hs_30_ni') * annexe_hs_line.get('rate_30_ni')),
                 'value_40_ni': self._float_2(annexe_hs_line.get('hs_40_ni') * annexe_hs_line.get('rate_40_ni')),
                 'value_50_ni': self._float_2(annexe_hs_line.get('hs_50_ni') * annexe_hs_line.get('rate_50_ni')),
                 'value_100_ni': self._float_2(annexe_hs_line.get('hs_100_ni') * annexe_hs_line.get('rate_100_ni')),
                 'value_30_i': self._float_2(annexe_hs_line.get('hs_30_i') * annexe_hs_line.get('rate_30_i')),
                 'value_40_i': self._float_2(annexe_hs_line.get('hs_40_i') * annexe_hs_line.get('rate_40_i')),
                 'value_50_i': self._float_2(annexe_hs_line.get('hs_50_i') * annexe_hs_line.get('rate_50_i')),
                 'value_100_i': self._float_2(annexe_hs_line.get('hs_100_i') * annexe_hs_line.get('rate_100_i')),
                 })
            # Total hs ,rate,value imposable
            total_hs_i = self._convert_to_decimal_hour(
                self._convert_to_second(annexe_hs_line.get('hs_30_i')) +
                self._convert_to_second(annexe_hs_line.get('hs_40_i')) +
                self._convert_to_second(annexe_hs_line.get('hs_50_i')) +
                self._convert_to_second(annexe_hs_line.get('hs_100_i')))
            total_rate_i = annexe_hs_line.get('rate_30_i') + annexe_hs_line.get('rate_40_i') + annexe_hs_line.get(
                'rate_50_i') + annexe_hs_line.get('rate_100_i')
            total_value_i = annexe_hs_line.get('value_30_i') + annexe_hs_line.get('value_40_i') + annexe_hs_line.get(
                'value_50_i') + annexe_hs_line.get('value_100_i')
            annexe_hs_line.update(
                {'total_hs_i': total_hs_i, 'total_rate_i': total_rate_i, 'total_value_i': total_value_i})
            total_hs_ni = self._convert_to_decimal_hour(
                self._convert_to_second(annexe_hs_line.get('hs_30_ni')) +
                self._convert_to_second(annexe_hs_line.get('hs_40_ni')) +
                self._convert_to_second(annexe_hs_line.get('hs_50_ni')) +
                self._convert_to_second(annexe_hs_line.get('hs_100_ni')))
            total_hs_i_ni = self._convert_to_decimal_hour(
                self._convert_to_second(total_hs_i) + self._convert_to_second(total_hs_ni))
            annexe_hs_line.update({'total_hs_i_ni': total_hs_i_ni})
            annexe_hs_lines.append(annexe_hs_line)
            print(annexe_hs_lines)
        return {
            'doc_ids': docids,
            'doc_model': model,
            'docs': docs,
            'data': data,
            'annexe_hs_lines': annexe_hs_lines
        }

    def _float_2(self, x):
        return float("{:.2f}".format(x))

    def _convert_to_decimal_hour(self, s):
        h = int(s / 3600)
        m = s % 3600
        m = m / 60
        m = int(m) / 100
        return h + m

    def _convert_to_second(self, x):
        h = int(x)
        m = x - h
        m = m * 100
        s = (h * 3600) + (m * 60)
        return s
