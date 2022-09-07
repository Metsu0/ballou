# coding: utf-8
import datetime
import calendar
import io

import xlsxwriter

from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import content_disposition


class IrsaXlsxExport(http.Controller):

    @http.route('/web/binary/download_irsa_xlsx_file', type='http', auth="public")
    def download_irsa_xlsx_file(self, id, **args):
        """
        Function to export IRSA state
        :param id:
        :param args:
        :return: xlsx file
        """
        # Variable initialization
        report = request.env['payslip.state.export'].browse(int(id))
        report_period = calendar.monthrange(int(report.year), int(report.period))
        report_period_from = datetime.date(int(report.year), int(report.period), int(1))
        report_period_to = datetime.date(int(report.year), int(report.period), int(report_period[1]))
        file_xlsx = io.BytesIO()
        row = 1
        sum_gross_daily_wage = 0
        sum_gross_wages = 0
        sum_advantage = 0
        sum_cnaps_employee = 0
        sum_ostie_employee = 0
        sum_net_taxable_income = 0
        sum_net_tax_withheld = 0

        # Get all pay to report
        domain = [
            ('state', '=', 'done'),
            ('date_to', '>=', report_period_from),
            ('date_to', '<=', report_period_to),
        ]
        if report.company_id:
            domain.append(('company_id', '=', report.company_id.id))
        all_payslip_ids = request.env['hr.payslip'].search(domain)
        # Group payslips by employee
        employee_ids = all_payslip_ids.mapped('employee_id')
        grouped_payslip_list = []
        for employee_id in employee_ids:
            current_payslip_ids = all_payslip_ids.filtered(lambda p: p.employee_id == employee_id)
            grouped_payslip_list.append(current_payslip_ids)
            all_payslip_ids -= current_payslip_ids
        # Workbook and sheet creation
        workbook = xlsxwriter.Workbook(file_xlsx)
        worksheet = workbook.add_worksheet()

        # Set format
        style = report.get_default_format(workbook)
        worksheet.set_row(0, 80)
        worksheet.set_column(1, 15, 30)

        # Editing sheet title
        worksheet.write(0, 1, "NOM ET PRÉNOM DU TRAVAILLEUR  (ANARANA SY FANAMPIN'ANARAN'NY MPIASA",
                        style.get('bold_justify_top_textwrap'))
        worksheet.write(0, 2, "FONCTION (ASANY)", style.get('bold_justify_top_textwrap'))
        worksheet.write(0, 3,
                        "NUMÉRO CARTE D'IDENTITÉ NATIONALE OU DE RÉSIDENT  (LAHARAN'NY KARAPANONDROM-PIRENENA NA KARA-BAHINY)",
                        style.get('bold_justify_top_textwrap'))
        worksheet.write(0, 4, "NUMÉRO D'IDENTIFICATION À LA CNAPS  (LAHARAM-PAMANTARANA CNAPS)",
                        style.get('bold_justify_top_textwrap'))
        worksheet.write(0, 5, "RÉMUNÉRATION BRUTE EN NUMÉRAIRE  (KARAMA TSY AFA-KARATSAKA RAISINA LELAVOLA) ( B )",
                        style.get('bold_justify_top_textwrap'))
        worksheet.write(0, 6,
                        "VALEUR DES AVANTAGES EN NATURE IMPOSABLES  (SANDAN'NY TOMBOTSOA TSY ARA-BOLA IHARAN'NY HETRA) ( C )",
                        style.get('bold_justify_top_textwrap'))
        worksheet.write(0, 7, "SALAIRE BRUT", style.get('bold_justify_top_textwrap'))
        worksheet.write(0, 8,
                        "RETENUE ET VERSEMENT EN VUE DE LA CONSTITUTION DE PENSION OU DE RETRAITE  (LATSAKEMBOKA ESORINA HO AN'NY FISOTROAN-DRONONO) ( D )",
                        style.get('bold_justify_top_textwrap'))
        worksheet.write(0, 9,
                        "RETENUE AU TITRE DE COTISATION OUVRIÈRE DUE À UNE ORGANISATION SANITAIRE  (LATSAKEMBOKA HO AN'NY FAHASALAMAN'NY MPIASA) ( E )",
                        style.get('bold_justify_top_textwrap'))
        worksheet.write(0, 10,
                        "REVENUS NETS IMPOSABLES (KARAMA SY NY TOA AZY AFA-KARATSAKA AMERANA NY HETRA)  ( F = B + C - D - E )",
                        style.get('bold_justify_top_textwrap'))
        worksheet.write(0, 11, "IMPÔT BRUT CORRESPONDANT  (HETRA TANDRIFIN'IZANY) ( G )",
                        style.get('bold_justify_top_textwrap'))
        worksheet.write(0, 12, "NOMBRE DE PERSONNES À CHARGE  (ISAN'OLONA IADIDIANA)",
                        style.get('bold_justify_top_textwrap'))
        worksheet.write(0, 13, "RÉDUCTION POUR PERSONNES À CHARGE  (FAMPIHENAN-KETRA NOHO NY OLONA IADIDIANA) ( H )",
                        style.get('bold_justify_top_textwrap'))
        worksheet.write(0, 14, "IMPÔT NET RETENU  (HETRA ALOA AFA-KARATSAKA) ( I = G - H )",
                        style.get('bold_justify_top_textwrap'))

        # Editing sheet content
        for payslip_ids in grouped_payslip_list:
            current_employee_id = payslip_ids[0].employee_id
            gross_daily_wage = payslip_ids.get_gross_daily_wage()
            gross_wages = payslip_ids.get_gross_salary_amount()
            advantage = payslip_ids.get_advantages_sum()
            cnaps_employee = payslip_ids.get_cnaps_employee()
            ostie_employee = payslip_ids.get_ostie_employee()
            net_taxable_income = gross_daily_wage + advantage - cnaps_employee - ostie_employee
            irsa = payslip_ids.get_amount_by_code('IRSA')
            irsa_threshold = request.env['hr.salary.rule'].search([('code', '=', 'SI')])[0].amount_fix or 0
            reduction_for_dependents = payslip_ids.get_amount_by_code('DED_ENFANT')
            net_tax_withheld = payslip_ids.get_amount_by_code('IRSA_BRUT')

            sum_gross_daily_wage += gross_daily_wage
            sum_gross_wages += gross_wages
            sum_advantage += advantage
            sum_cnaps_employee += cnaps_employee
            sum_ostie_employee += ostie_employee
            sum_net_taxable_income += sum_net_taxable_income
            sum_net_tax_withheld += net_tax_withheld

            worksheet.write(row, 0, row)
            worksheet.write(row, 1, current_employee_id.name, style.get('text_wrap'))
            worksheet.write(row, 2, current_employee_id.job_id.name, style.get('text_wrap')) or ''
            worksheet.write(row, 3,
                            current_employee_id.identification_id if current_employee_id.identification_id else current_employee_id.passport_id or '',
                            style.get('text_wrap')) or ''
            worksheet.write(row, 4, current_employee_id.cnaps_number, style.get('text_wrap')) or ''
            worksheet.write(row, 5, gross_daily_wage, style.get('numeric')) or ''
            worksheet.write(row, 6, advantage, style.get('numeric')) or ''
            worksheet.write(row, 7, gross_wages, style.get('numeric')) or ''
            worksheet.write(row, 8, cnaps_employee, style.get('numeric')) or ''
            worksheet.write(row, 9, ostie_employee, style.get('numeric')) or ''
            worksheet.write(row, 10, net_taxable_income, style.get('numeric')) or ''
            worksheet.write(row, 11, net_tax_withheld or irsa, style.get('numeric')) or ''
            worksheet.write(row, 12, reduction_for_dependents / irsa_threshold) or ''
            worksheet.write(row, 13, reduction_for_dependents, style.get('numeric')) or ''
            worksheet.write(row, 14, irsa, style.get('numeric')) or ''

            row += 1

        # Setting sum
        worksheet.write(row, 5, sum_gross_daily_wage, style.get('numeric_bold'))
        worksheet.write(row, 6, sum_advantage, style.get('numeric_bold'))
        worksheet.write(row, 7, sum_gross_wages, style.get('numeric_bold'))
        worksheet.write(row, 8, sum_cnaps_employee, style.get('numeric_bold'))
        worksheet.write(row, 9, sum_ostie_employee, style.get('numeric_bold'))
        worksheet.write(row, 10, sum_net_taxable_income, style.get('numeric_bold'))
        worksheet.write(row, 11, sum_net_tax_withheld, style.get('numeric_bold'))

        workbook.close()

        # Export xlsx file
        month = calendar.month_name[report_period_from.month].capitalize()
        filename = 'IRSA %s_%s.xlsx' % (month, str(report.year))
        return request.make_response(file_xlsx.getvalue(),
                                     [('Content-Type', 'application/octet-stream'),
                                      ('Content-Disposition', content_disposition(filename))])
