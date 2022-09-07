# coding: utf-8
import datetime
import calendar
import io

import xlsxwriter

from odoo import http, _
from odoo.http import request
from odoo.addons.web.controllers.main import content_disposition

MONTHS = [
    _('January'),
    _('February'),
    _('March'),
    _('April'),
    _('May'),
    _('June'),
    _('July'),
    _('August'),
    _('September'),
    _('October'),
    _('November'),
    _('December')
]


class AnnexIrsaXlsxExport(http.Controller):

    @http.route('/web/binary/download_annex_irsa_xlsx_file', type='http', auth="public")
    def download_annex_irsa_xlsx_file(self, id, **args):
        """
        Function to export Annex IRSA state
        :param id:
        :param args:
        :return: xlsx file
        """
        # Variable initialization
        report = request.env['payslip.state.export'].browse(int(id))
        report_period = calendar.monthrange(
            int(report.year), int(report.period))
        report_period_from = datetime.date(
            int(report.year), int(report.period), int(1))
        report_period_to = datetime.date(
            int(report.year), int(report.period), int(report_period[1]))
        file_xlsx = io.BytesIO()

        tax_code = "IRSA"
        tax_wording = _("Tax on salaries and assimilated incomes")
        nif = report.company_id.nif
        year = report.year
        month = MONTHS[int(report.period) - 1]

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
            current_payslip_ids = all_payslip_ids.filtered(
                lambda p: p.employee_id == employee_id)
            grouped_payslip_list.append(current_payslip_ids)
        

        # Workbook and sheet creation
        workbook = xlsxwriter.Workbook(file_xlsx)
        worksheet = workbook.add_worksheet()

        # Set format
        style = report.get_default_format(workbook)
        workbook.formats[0].set_font_size(11)

        # Version + Title
        worksheet.write('B1', "Version:")
        worksheet.merge_range(
            'B3:W3', "Form for generating XML files of detailed Annex IRSA", style.get("bold_f16_center_calibri"))

        # Annexe IRSA information
        worksheet.write('B5', _("Tax code:"))
        worksheet.merge_range(
            'C5:D5', tax_code, style.get("bold_left_border"))

        worksheet.write('B7', _("Tax Wording:"))
        worksheet.merge_range(
            'C7:I7', tax_wording, style.get("bold_left_border"))

        worksheet.write('B9', _("NIF:"))
        worksheet.merge_range(
            'C9:D9', nif, style.get("bold_left_border"))

        worksheet.write('B11', _("Year:"))
        worksheet.merge_range(
            'C11:D11', year, style.get("bold_left_border"))

        worksheet.write('B13', _("Month:"))
        worksheet.merge_range(
            'C13:D13', month, style.get("bold_left_border"))

        # Button to generate xml
        worksheet.insert_button('G9', {
            'caption': _("Generate XML in folder /Documents"),
            'width': 150,
            'height': 60,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#C55A11'
        })

        worksheet.write('B15', _("All fields are mandatory"))

        worksheet.merge_range(
            'J15:K15', _("Allowance"), style.get("bold_center_border"))
        worksheet.merge_range(
            'L15:M15', _("Benefits in kind"), style.get("bold_center_border"))

        worksheet.write('B16', _("Registration N°"), style.get("bold_center_border_wrap"))
        worksheet.write('C16', _("CNAPS N°"), style.get("bold_center_border_wrap"))
        worksheet.write('D16', _("Fullname"), style.get("bold_center_border_wrap"))
        worksheet.write('E16', _("CIN/Resident Card"), style.get("bold_center_border_wrap"))
        worksheet.write('F16', _("Hiring date"), style.get("bold_center_border_wrap"))
        worksheet.write('G16', _("Dismissal date"), style.get("bold_center_border_wrap"))
        worksheet.write('H16', _("Job"), style.get("bold_center_border_wrap"))
        worksheet.write('I16', _("Base Salary"), style.get("bold_center_border_wrap"))
        worksheet.write('J16', _("Taxable"), style.get("bold_center_border_wrap"))
        worksheet.write('K16', _("Non Taxable"), style.get("bold_center_border_wrap"))
        worksheet.write('L16', _("Taxable"), style.get("bold_center_border_wrap"))
        worksheet.write('M16', _("Exempt"), style.get("bold_center_border_wrap"))
        worksheet.write('N16', _("Overtime"), style.get("bold_center_border_wrap"))
        worksheet.write('O16', _("Bonus and gratuity"), style.get("bold_center_border_wrap"))
        worksheet.write('P16', _("Others"), style.get("bold_center_border_wrap"))
        worksheet.write('Q16', _("Gross Salary"), style.get("bold_center_border_wrap"))
        worksheet.write('R16', _("CNAPS"), style.get("bold_center_border_wrap"))
        worksheet.write('S16', _("OSTIE or assimiated"), style.get("bold_center_border_wrap"))
        worksheet.write('T16', _("Net Salary"), style.get("bold_center_border_wrap"))
        worksheet.write('U16', _("Other deduction"), style.get("bold_center_border_wrap"))
        worksheet.write('V16', _("Taxable amount"), style.get("bold_center_border_wrap"))
        worksheet.write('W16', _("Corresponding tax"), style.get("bold_center_border_wrap"))
        worksheet.write('X16', _("Reduction for dependents"), style.get("bold_center_border_wrap"))
        worksheet.write('Y16', _("Tax due"), style.get("bold_center_border_wrap"))

        row = 16

        # Editing sheet content
        for payslip_ids in grouped_payslip_list:
            current_employee_id = payslip_ids[0].employee_id

            first_contract_date = current_employee_id.first_contract_date.strftime("%d/%m/%Y") if current_employee_id.first_contract_date else ""
            last_contract_date = ""

            employee_contracts = report.env["hr.contract"].search([('employee_id', '=', current_employee_id.id), ("state", "in", ["open", "cancel"])], order='date_end')
            if employee_contracts:
                last_contract = employee_contracts[-1]
                last_contract_date = last_contract.date_end.strftime("%d/%m/%Y") if last_contract.date_end else ""

            worksheet.write(row, 1, current_employee_id.registration_number or '', style.get("border"))
            worksheet.write(row, 2, current_employee_id.cnaps_number or '', style.get("border"))
            worksheet.write(row, 3, current_employee_id.name or '', style.get("border"))
            worksheet.write(row, 4, current_employee_id.identification_id or current_employee_id.passport_id or '', style.get("border"))
            worksheet.write(row, 5, first_contract_date, style.get("border"))
            worksheet.write(row, 6, last_contract_date, style.get("border"))
            worksheet.write(row, 7, current_employee_id.job_id.name or '', style.get("border"))
            worksheet.write(row, 8, payslip_ids.get_base_salary() or 0, style.get("border"))
            worksheet.write(row, 9, payslip_ids.get_taxable_allowance() or 0, style.get("border"))
            worksheet.write(row, 10, payslip_ids.get_non_taxable_allowance() or 0, style.get("border"))
            worksheet.write(row, 11, payslip_ids.get_taxable_benefit_in_kind() or 0, style.get("border"))
            worksheet.write(row, 12, payslip_ids.get_exempt_benefits_in_kind() or 0, style.get("border"))
            worksheet.write(row, 13, payslip_ids.get_additional_hour(), style.get("border"))
            worksheet.write(row, 14, payslip_ids.get_bonus_and_gratuity() or 0, style.get("border"))
            worksheet.write(row, 15, payslip_ids.get_others() or 0, style.get("border"))
            worksheet.write(row, 16, payslip_ids.get_gross_salary_amount() or 0, style.get("border"))
            worksheet.write(row, 17, payslip_ids.get_cnaps_employee() or 0, style.get("border"))
            worksheet.write(row, 18, payslip_ids.get_ostie_employee() or 0, style.get("border"))
            worksheet.write(row, 19, payslip_ids.get_net_salary() or 0, style.get("border"))
            worksheet.write(row, 20, payslip_ids.get_other_deduction() or 0, style.get("border"))
            worksheet.write(row, 21, payslip_ids.get_taxable_amount() or 0, style.get("border"))
            worksheet.write(row, 22, payslip_ids.get_corresponding_tax() or 0, style.get("border"))
            worksheet.write(row, 23, payslip_ids.get_reduction_for_dependents() or 0, style.get("border"))
            worksheet.write(row, 24, payslip_ids.get_tax_due() or 0, style.get("border"))
            row += 1

        workbook.close()

        # Export xlsx file
        month = calendar.month_name[report_period_from.month].capitalize()
        filename = '%s Annex IRSA %s_%s.xlsx' % (nif, month, str(report.year))
        return request.make_response(file_xlsx.getvalue(),
                                     [('Content-Type', 'application/octet-stream'),
                                      ('Content-Disposition', content_disposition(filename))])
