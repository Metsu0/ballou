# coding: utf-8
from datetime import timedelta
from odoo import models

MONTHS = [(1, 2, 3), (4, 5, 6), (7, 8, 9), (10, 11, 12)]


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def get_gross_salary_amount(self):
        """
        Method to get gross salary amount.
        :param payslip:
        :return: gross salary
        """
        total_amount = 0
        for rec in self:
            total_amount += sum(
                rec.line_ids.filtered(
                    lambda p: p.salary_rule_id.code == rec.struct_id.gross_salary_id.code
                ).mapped('amount')
            )
        return total_amount

    def get_gross_daily_wage(self):
        """
        Get gross daily wage
        :return:
        """
        total_amount = 0
        for rec in self:
            total_amount += sum(
                rec.line_ids.filtered(
                    lambda p: p.salary_rule_id.code == rec.struct_id.gross_daily_id.code
                ).mapped('amount')
            )
        return total_amount

    def get_fmfp(self):
        """
        Method to get fmfp.
        :return: fmfp
        """
        total_amount = 0
        for rec in self:
            total_amount += sum(
                rec.line_ids.filtered(lambda p: p.salary_rule_id.code == rec.struct_id.fmfp_id.code).mapped('amount')
            )
        return total_amount

    def get_cnaps_employee(self):
        """
        Method to get cnaps employee.
        :return: cnaps employee
        """
        total_amount = 0
        for rec in self:
            total_amount += sum(
                rec.line_ids.filtered(lambda p: p.salary_rule_id.code == rec.struct_id.cnaps_id.code).mapped('amount')
            )
        return total_amount

    def get_cnaps_employer(self):
        """
        Method to get cnaps employer.
        :return: cnaps employer
        """
        total_amount = 0
        for rec in self:
            total_amount += sum(
                rec.line_ids.filtered(
                    lambda p: p.salary_rule_id.code == rec.struct_id.cnaps_employer_id.code
                ).mapped('amount')
            )
        return total_amount

    def get_ostie_employee(self):
        """
        Method to get ostie employee.
        :return: ostie employee
        """
        total_amount = 0
        for rec in self:
            total_amount += sum(
                rec.line_ids.filtered(lambda p: p.salary_rule_id.code == rec.struct_id.ostie_id.code).mapped('amount')
            )
        return total_amount

    def get_ostie_employer(self):
        """
        Method to get ostie employer.
        :return: ostie employer
        """
        return sum(
            self.line_ids.filtered(lambda p: p.salary_rule_id.code == self.struct_id.ostie_employer_id.code).mapped(
                'amount'))

    def get_advantages_sum(self):
        """
        Method to get the sum of an employee advantages.
        :param payslip:
        :return: Advantage
        """
        total_amount = 0
        for rec in self:
            total_amount += sum(
                rec.line_ids.filtered(
                    lambda p: p.salary_rule_id.category_id.code in rec.struct_id.advantage_ids.mapped('code')
                ).mapped('amount')
            )
        return total_amount

    def get_workdays(self):
        """
        Get work days
        :return:
        """
        total_amount = 0
        for rec in self:
            total_amount += sum(
                rec.worked_days_line_ids.filtered(
                    lambda w: w.code == rec.struct_id.workday_code
                ).mapped('number_of_days')
            )
        return total_amount

    def get_wages_by_month(self, state_id):
        """
        Get wages (brut) by month
        :param state_id:
        :return:
        """
        months = MONTHS[int(state_id.quarter)]
        wages = {0: 0, 1: 0, 2: 0}
        for key, month in enumerate(months):
            payslip_ids = self.filtered(lambda p: int(p.date_to.month) == month)
            wages[key] = payslip_ids.get_gross_salary_amount()
        return wages

    def get_effectif_per_month(self, state_id):
        """
        Get payslip effectif in month
        :param state_id:
        :return:
        """
        months = MONTHS[int(state_id.quarter)]
        effectifs = {0: 0, 1: 0, 2: 0}
        for key, month in enumerate(months):
            payslip_ids = self.filtered(lambda p: int(p.date_to.month) == month)
            effectifs[key] = len(payslip_ids.mapped('employee_id'))
        return effectifs

    def get_base_salary(self):
        """
        Method to get base salary
        :return: base salary employer
        """
        total_amount = 0
        for rec in self:
            total_amount += sum(
                rec.line_ids.filtered(
                    lambda p: p.salary_rule_id.code == "BASIC"
                ).mapped('amount')
            )
        return total_amount

    def get_taxable_allowance(self):
        """
        Method to get taxable allowance
        :return: total taxable allowance
        """
        total_amount = 0
        for rec in self:
            total_amount += sum(
                rec.line_ids.filtered(
                    lambda p: p.salary_rule_id.code in rec.struct_id.taxable_allowance_ids.mapped('code')
                ).mapped('amount')
            )
        return total_amount

    def get_non_taxable_allowance(self):
        """
        Method to get non taxable allowance
        :return: total non taxable allowance
        """
        total_amount = 0
        for rec in self:
            total_amount += sum(
                rec.line_ids.filtered(
                    lambda p: p.salary_rule_id.code in rec.struct_id.non_taxable_allowance_ids.mapped('code')
                ).mapped('amount')
            )
        return total_amount

    def get_taxable_benefit_in_kind(self):
        """
        Method to get non taxable allowance
        :return: total non taxable allowance
        """
        total_amount = 0
        for rec in self:
            total_amount += sum(
                rec.line_ids.filtered(
                    lambda p: p.salary_rule_id.code in rec.struct_id.taxable_benefit_in_kind_ids.mapped('code')
                ).mapped('amount')
            )
        return total_amount

    def get_exempt_benefits_in_kind(self):
        """
        Method to get non taxable allowance
        :return: total non taxable allowance
        """
        total_amount = 0
        for rec in self:
            total_amount += sum(
                rec.line_ids.filtered(
                    lambda p: p.salary_rule_id.code in rec.struct_id.exempt_benefits_in_kind_ids.mapped('code')
                ).mapped('amount')
            )
        return total_amount

    def get_additional_hour(self):
        """
        Method to get non taxable allowance
        :return: total non taxable allowance
        """
        total_amount = 0
        for rec in self:
            total_amount += sum(
                rec.line_ids.filtered(
                    lambda p: p.salary_rule_id.category_id.code == rec.struct_id.additional_hour_id.code
                ).mapped('amount')
            )
        return total_amount

    def get_bonus_and_gratuity(self):
        """
        Method to get bonus and gratuity
        :return: bonus and gratuity
        """
        total_amount = 0
        for rec in self:
            total_amount += sum(
                rec.line_ids.filtered(
                    lambda p: p.salary_rule_id.code in rec.struct_id.bonus_and_gratuity_ids.mapped('code')
                ).mapped('amount')
            )
        return total_amount

    def get_others(self):
        """
        Method others rules (if non_taxable_additional_hour checked + HS 30/50)
        :return: others rules amount
        """
        total_amount = 0
        for rec in self:
            total_amount += sum(
                rec.line_ids.filtered(
                    lambda p: p.salary_rule_id.code in rec.struct_id.others_ids.mapped('code')
                ).mapped('amount')
            )

            if rec.struct_id.non_taxable_additional_hour:
                hourly_rate = sum(
                    rec.line_ids.filtered(
                        lambda p: p.salary_rule_id.code == "TH"
                    ).mapped('amount')
                )

                hs_30, hs_50 = rec._get_non_taxable_additional_hour_30_50()

                non_taxable_30_amount = hs_30 * 1.3 * hourly_rate
                non_taxable_50_amount = hs_50 * 1.5 * hourly_rate
                total_amount += (non_taxable_30_amount + non_taxable_50_amount)

        return total_amount

    def get_net_salary(self):
        """
        Method to get net salary
        :return: net salary amount
        """
        total_amount = 0
        for rec in self:
            total_amount += sum(
                rec.line_ids.filtered(
                    lambda p: p.salary_rule_id.code == rec.struct_id.net_salary_id.code
                ).mapped('amount')
            )
        return total_amount
    
    def get_other_deduction(self):
        """
        Method to get bonus and gratuity
        :return: bonus and gratuity
        """
        total_amount = 0
        for rec in self:
            total_amount += sum(
                rec.line_ids.filtered(
                    lambda p: p.salary_rule_id.code in rec.struct_id.other_deduction_ids.mapped('code')
                ).mapped('amount')
            )
        return total_amount

    def get_taxable_amount(self):
        """
        Method to get corresponding tax
        :return: corresponding Tax
        """
        total_amount = 0
        for rec in self:
            total_amount += sum(
                rec.line_ids.filtered(
                    lambda p: p.salary_rule_id.code == rec.struct_id.taxable_amount_id.code
                ).mapped('amount')
            )
        return total_amount

    def get_corresponding_tax(self):
        """
        Method to get corresponding tax
        :return: corresponding Tax
        """
        total_amount = 0
        for rec in self:
            total_amount += sum(
                rec.line_ids.filtered(
                    lambda p: p.salary_rule_id.code == "IRSA_BRUT"
                ).mapped('amount')
            )
        return total_amount

    def get_reduction_for_dependents(self):
        """
        Method to get Reduction for dependents
        :return: reduction for dependents
        """
        total_amount = 0
        for rec in self:
            total_amount += sum(
                rec.line_ids.filtered(
                    lambda p: p.salary_rule_id.code == "DED_ENFANT"
                ).mapped('amount')
            )
        return total_amount
    
    def get_tax_due(self):
        """
        Method to get Tax Due
        :return: reduction for tax due
        """
        total_amount = 0
        for rec in self:
            total_amount += sum(
                rec.line_ids.filtered(
                    lambda p: p.salary_rule_id.code == rec.struct_id.irsa_id.code
                ).mapped('amount')
            )
        return total_amount

    def _get_non_taxable_additional_hour_30_50(self):
        """
        Method to get non Taxable Additional Hour (HS: heure sup)
        :return: tuple of value of (hs30, hs50)
        """

        hs_input_line_ids = self.env["hr.payslip.input"].search([("payslip_id", "=", self.id), ("code", "in", ("HS_SEM1", "HS_SEM2", "HS_SEM3", "HS_SEM4", "HS_SEM5"))])
        print("======>", hs_input_line_ids)

        tuple_hs = [(
            x.amount if x.amount <= 8 else 8,
            x.amount - 8 if x.amount > 8 else 0) for x in hs_input_line_ids or []]
        hs_30_list = [self._convert_to_second(i) for i, j in tuple_hs]
        hs_50_list = [self._convert_to_second(j) for i, j in tuple_hs]
        hs_sum_list = [self._convert_to_second(i) + self._convert_to_second(j) for i, j in tuple_hs]
        # Non imposable 30% et 50 %
        hs_30 = 0
        hs_50 = 0
        hour_20 = 60 * 60 * 20
        found = True

        for index in range(len(hs_sum_list)):
            temp_sum = sum([x for x in hs_sum_list[:index + 1]])
            if temp_sum >= hour_20 and not found:
                temp_sum -= hs_50_list[index]
                if temp_sum <= hour_20:
                    temp_sum += hs_50_list[index]
                    rest = temp_sum - hour_20
                    hs_50 = sum([x for x in hs_50_list[:index + 1]])
                    hs_50 -= rest
                    hs_30 = sum([x for x in hs_30_list[:index + 1]])
                    found = True

                elif temp_sum >= hour_20:
                    temp_sum -= hs_30_list[index]
                    if temp_sum <= hour_20:
                        temp_sum += hs_30_list[index]
                        rest = temp_sum - hour_20
                        hs_30 = sum([x for x in hs_30_list[:index + 1]])
                        hs_30 -= rest
                        hs_50 = sum([x for x in hs_50_list[:index] ])
                        found = True

        return (hs_30, hs_50)


    def _convert_to_second(self, hour_float):
        print(self.employee_id.name)
        print(hour_float)
        hour_float = str(float(hour_float)).split(".")
        return timedelta(hours=int(hour_float[0]), minutes=int(hour_float[1])).total_seconds()
