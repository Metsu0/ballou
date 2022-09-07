from odoo import api, models
import datetime


class ParticularReport(models.AbstractModel):
    _name = 'report.generic_hr.print_employee_history'

    def _get_report_values(self, docids, data=None):
        # get the report action back as we will need its data
        # report = self.env['ir.actions.report']._get_report_from_name('module.report_name')
        # get the records selected for this rendering of the report
        obj = self.env['hr.employee'].browse(docids)

        # return a custom rendering context
        premium_monthly = 0
        if obj.contract_id:
            hr_payroll_variable_ids = obj.contract_id.payroll_variable_ids.filtered(lambda x: x.print == True)
            premium_monthly = sum([x.amount for x in hr_payroll_variable_ids if hr_payroll_variable_ids])
        more_info_list = []
        for contract_id in obj.contract_ids:
            more_info_line = {
                'ref': datetime.date(contract_id.create_date.year, contract_id.create_date.month,
                                     contract_id.create_date.day),
                'classification': contract_id.category_id.name,
                'wage': contract_id.wage if contract_id.wage_type == 'monthly' else contract_id.wage * 173.33,
                'premium': sum([x.amount for x in
                                contract_id.payroll_variable_ids.filtered(lambda
                                                                              x: x.print == True)])}
            more_info_list.append(more_info_line)
        hr_sanction_ids = self.env['hr.sanction'].search([('employee_id', '=', obj.id)])

        for hr_sanction in hr_sanction_ids.filtered(lambda x: x.type_id.type != False):
            more_info_line = {}
            more_info_line.update({'ref': hr_sanction.delivery_date, 'wage': 0, 'premium': 0})
            if hr_sanction.type_id.type == 'caution':
                delta = hr_sanction.end_date - hr_sanction.delivery_date
                more_info_line.update({'caution': str(delta.days) + " Jours"})
            elif hr_sanction.type_id.type == 'layoff':
                delta = hr_sanction.end_date - hr_sanction.delivery_date
                more_info_line.update({'layoff': str(delta.days) + " Jours"})
            more_info_list.append(more_info_line)

        more_info_list.sort(key=lambda x: x['ref'])
        skills_str = ""
        for skill_id in obj.employee_skill_ids:
            skills_str += skill_id.display_name + ", "
        for more_info_list_dict in more_info_list:
            more_info_list_dict.update(
                {'ref': obj.registration_number + " " + str(more_info_list_dict.get('ref').strftime('%d/%m/%Y')),
                 'wage': str(more_info_list_dict.get(
                     'wage', 0.0)) + " " + obj.company_id.currency_id.symbol, 'premium': str(
                    more_info_list_dict.get('premium', 0.0)) + " " + obj.company_id.currency_id.symbol,
                 'distinction': skills_str})

        return {
            'docs': obj,
            'premium_monthly': premium_monthly,
            'more_infos': more_info_list,
            # 'lines': docids.get_lines()
        }
