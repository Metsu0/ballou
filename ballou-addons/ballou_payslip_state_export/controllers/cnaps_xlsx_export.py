# coding: utf-8
import io

import xlsxwriter

from odoo import http, _
from odoo.http import request, content_disposition

MONTHS = [
    (_('JANVIER'), _('FEVRIER'), _('MARS')),
    (_('AVRIL'), _('MAI'), _('JUIN')),
    (_('JUILLET'), _('AOUT'), _('SEPTEMBRE')),
    (_('OCTOBRE'), _('NOVEMBRE'), _('DECEMBRE')),
]


class CnapsXlsxExport(http.Controller):

    @http.route('/web/binary/download_cnaps_xlsx_file', type='http', auth="public")
    def download_cnaps_xls_file(self, id, **args):
        """
        Function to export CNaPs state
        :param id:
        :param args:
        :return: xls
        """
        # Variable initialisation
        state_id = request.env['payslip.state.export'].browse(int(id))
        months = MONTHS[int(state_id.quarter)]
        xls_file = io.BytesIO()
        year_month = '%s0%s' % (state_id.year, str(int(state_id.quarter) + 1))
        period_year = '0%s T-%s' % (str(int(state_id.quarter) + 1), state_id.year)
        filename = state_id.get_filename()
        company_id = state_id.company_id
        quarter_range = state_id.get_quarter_range()
        responsible_id = company_id.responsible_id
        effective, capped_resume, employer_contribution_resume, employee_contribution_resume = [], [], [], []
        fmfp_resume = []

        # Get salary rule value sme/cnaps contribution
        smig_id = request.env['hr.salary.rule'].search([('code', '=', 'SMIG')])
        cnaps_employer_threshold_id = request.env['hr.salary.rule'].search([('code', '=', 'TAUX_CNAPS_PAT')])
        cnaps_threshold_id = request.env['hr.salary.rule'].search([('code', '=', 'TAUX_CNAPS')])

        sme = smig_id[0].amount_fix if smig_id else 0
        cnaps_employer_contribution = cnaps_threshold_id[0].amount_fix if cnaps_employer_threshold_id else 0
        cnaps_employee_contribution = cnaps_threshold_id.amount_fix if cnaps_threshold_id else 0

        # Create workbook
        workbook = xlsxwriter.Workbook(xls_file)
        # Set default font size
        workbook.formats[0].set_font_size(8)
        # Set style
        style = state_id.get_default_format(workbook)
        # Create worksheet
        sheet_1 = workbook.add_worksheet(_('EMPLOYER'))
        monthly_sheet = [
            workbook.add_worksheet(months[0].upper()),
            workbook.add_worksheet(months[1].upper()),
            workbook.add_worksheet(months[2].upper())
        ]
        # Write monthly sheet
        for key, quarter in enumerate(quarter_range):
            current_sheet = monthly_sheet[key]
            sum_wage, sum_advantage, sum_workday, sum_uncapped, sum_capped = 0, 0, 0, 0, 0
            sum_employer_contribution, sum_employee_contribution, sum_total_contribution, sum_fmfp = 0, 0, 0, 0
            last_row = 0
            # Write sheet title
            self.write_sheet_title(current_sheet, style)
            # Get payslips
            domain = [
                ('state', '=', 'done'),
                ('date_to', '>=', quarter[0]),
                ('date_to', '<=', quarter[1]),
                ('company_id.id', '=', state_id.company_id.id)
            ]
            all_payslip_ids = request.env['hr.payslip'].search(domain)

            # Group payslips by employee
            employee_ids = all_payslip_ids.mapped('employee_id')
            grouped_payslip_list = []
            for employee_id in employee_ids:
                current_payslip_ids = all_payslip_ids.filtered(lambda p: p.employee_id == employee_id)
                grouped_payslip_list.append(current_payslip_ids)
                all_payslip_ids -= current_payslip_ids
            effective.append(len(grouped_payslip_list))
            for index, payslip_ids in enumerate(grouped_payslip_list):
                # Current payslip variable init
                row = index + 2
                last_row = row
                current_employee_id = payslip_ids[0].employee_id
                c_id = company_id
                wage = payslip_ids.get_gross_daily_wage()
                advantage = payslip_ids.get_advantages_sum()
                gross_salary = payslip_ids.get_gross_salary_amount()
                workdays = payslip_ids.get_workdays()
                cnaps_ceiling = sme * 8
                uncapped = gross_salary
                capped = cnaps_ceiling if uncapped > cnaps_ceiling else uncapped
                employer_contribution = payslip_ids.get_cnaps_employer()
                employee_contribution = payslip_ids.get_cnaps_employee()
                total_contribution = employee_contribution + employer_contribution
                fmfp = payslip_ids.get_fmfp()

                first_contract_id = current_employee_id.contract_ids[0]
                last_contract_id = current_employee_id.contract_ids[-1]
                if last_contract_id:
                    contract_date_end = ''
                    if not last_contract_id.date_end:
                        contract_date_end = last_contract_id.date_end
                    elif last_contract_id.date_end.month == quarter[0].month:
                        contract_date_end = last_contract_id.date_end

                # Set sum values
                sum_workday += workdays
                sum_advantage += advantage
                sum_wage += wage
                sum_uncapped += uncapped
                sum_capped += capped
                sum_employer_contribution += employer_contribution
                sum_employee_contribution += employee_contribution
                sum_total_contribution += total_contribution
                sum_fmfp += fmfp
                # Write sheet row
                current_sheet.write(row, 0, year_month, style.get('f8_border'))
                current_sheet.write(row, 1, current_employee_id.cnaps_number or '', style.get('f8_border'))
                current_sheet.write(row, 2, current_employee_id.lastname, style.get('f8_border'))
                current_sheet.write(row, 3, current_employee_id.firstname, style.get('f8_border'))
                current_sheet.write(row, 4, c_id.company_registry, style.get('f8_border'))
                current_sheet.write(row, 5, first_contract_id.first_contract_date if first_contract_id else '',
                                    style.get('f8_border_date'))
                current_sheet.write(row, 6, contract_date_end or '',
                                    style.get('f8_border_date'))
                current_sheet.write(row, 7, wage or '-', style.get('numeric_f8_border'))
                current_sheet.write(row, 8, advantage or '-', style.get('numeric_f8_border'))
                current_sheet.write(row, 9, workdays or '-', style.get('numeric_f8_border'))
                current_sheet.write(row, 10, uncapped or '-', style.get('numeric_f8_border'))
                current_sheet.write(row, 11, capped or '-', style.get('numeric_f8_border'))
                current_sheet.write(row, 12, employer_contribution or '-', style.get('numeric_f8_border'))
                current_sheet.write(row, 13, employee_contribution or '-', style.get('numeric_f8_border'))
                current_sheet.write(row, 14, total_contribution or '-', style.get('numeric_f8_border'))
                current_sheet.write(row, 15, fmfp or '-', style.get('numeric_f8_border'))
                current_sheet.write(row, 16,
                                    current_employee_id.identification_id if current_employee_id.identification_id else current_employee_id.passport_id or '',
                                    style.get('f8_border'))
            # write column sum
            current_sheet.write(last_row + 1, 7, sum_wage, style.get('numeric_f8_border'))
            current_sheet.write(last_row + 1, 8, sum_advantage, style.get('numeric_f8_border'))
            current_sheet.write(last_row + 1, 8, sum_advantage, style.get('numeric_f8_border'))
            current_sheet.write(last_row + 1, 9, sum_workday, style.get('numeric_f8_border'))
            current_sheet.write(last_row + 1, 10, sum_uncapped, style.get('numeric_f8_border'))
            current_sheet.write(last_row + 1, 11, sum_capped, style.get('numeric_f8_border'))
            current_sheet.write(last_row + 1, 12, sum_employer_contribution, style.get('numeric_f8_border'))
            current_sheet.write(last_row + 1, 13, sum_employee_contribution, style.get('numeric_f8_border'))
            current_sheet.write(last_row + 1, 14, sum_total_contribution, style.get('numeric_f8_border'))
            current_sheet.write(last_row + 1, 15, sum_fmfp, style.get('numeric_f8_border'))
            # Set resume values
            capped_resume.append(sum_capped)
            employer_contribution_resume.append(sum_employer_contribution)
            employee_contribution_resume.append(sum_employee_contribution)
            fmfp_resume.append(sum_fmfp)
            current_sheet.set_column(0, 0, 10)
            current_sheet.set_column(1, 1, 20)
            current_sheet.set_column(2, 3, 40)
            current_sheet.set_column(4, 16, 20)
            current_sheet.freeze_panes(2, 0)
        # Write sheet 1
        sheet_1.write(0, 0, year_month)
        sheet_1.write(1, 0, 'RENSEIGNEMENTS SUR L\'EMPLOYEUR', style.get('bold_underline_f8'))
        sheet_1.write(3, 1, 'N° MATRICULE')
        sheet_1.write(3, 2, company_id.company_registry)
        sheet_1.write(4, 1, 'RAISON SOCIALE')
        sheet_1.write(4, 2, company_id.name)
        sheet_1.write(5, 1, 'N° NIF')
        sheet_1.write(5, 2, company_id.nif)
        sheet_1.write(6, 1, 'N° STAT')
        sheet_1.write(6, 2, company_id.stat)
        sheet_1.write(7, 1, 'ADRESSE')
        sheet_1.write(7, 2, company_id.street)
        sheet_1.write(7, 2, company_id.street)
        sheet_1.write(7, 4, '%s %s' % (company_id.city, company_id.zip))
        sheet_1.write(8, 1, 'E-mail')
        sheet_1.write_url(8, 2, responsible_id.work_email if responsible_id else '', style.get('f8'))
        sheet_1.write(10, 0, 'COTISATIONS', style.get('bold_underline_f8'))
        sheet_1.write(11, 1, 'Période et Année')
        sheet_1.write(11, 2, period_year, style.get('f8_border'))
        sheet_1.write(12, 1, 'Référence paiement VIREMENT')
        sheet_1.write(12, 2, filename, style.get('f8_border'))
        sheet_1.write(14, 1, 'Taux Employeur')
        sheet_1.write(14, 2, "%s" % str(cnaps_employer_contribution) + ' %', style.get('f8_border'))
        sheet_1.write(15, 1, 'Taux Travailleur')
        sheet_1.write(15, 2, "%s" % str(cnaps_employee_contribution) + ' %', style.get('f8_border'))
        sheet_1.write(17, 0, 'MOIS CONCERNE', style.get('bold_underline_f8'))
        sheet_1.write(17, 2, months[0].upper(), style.get('f8_border_center'))
        sheet_1.write(17, 3, months[1].upper(), style.get('f8_border_center'))
        sheet_1.write(17, 4, months[2].upper(), style.get('f8_border_center'))
        sheet_1.write(19, 0, 'RECAPITULATION', style.get('bold_underline_f8'))
        sheet_1.write(20, 5, 'TOTAUX', style.get('bold_f8'))
        sheet_1.write(21, 1, 'Effectif mensuel (OBLIGATOIRE)', style.get('f8_border'))
        sheet_1.write(21, 2, effective[0], style.get('numeric_f8_border'))
        sheet_1.write(21, 3, effective[1], style.get('numeric_f8_border'))
        sheet_1.write(21, 4, effective[2], style.get('numeric_f8_border'))
        sheet_1.write(21, 5, '', style.get('numeric_f8_border'))
        sheet_1.write(22, 1, 'Totaux Salaires plafonnés', style.get('f8_border'))
        sheet_1.write(22, 2, capped_resume[0], style.get('numeric_f8_border'))
        sheet_1.write(22, 3, capped_resume[1], style.get('numeric_f8_border'))
        sheet_1.write(22, 4, capped_resume[2], style.get('numeric_f8_border'))
        sheet_1.write(22, 5, sum(capped_resume), style.get('numeric_f8_border'))
        sheet_1.write(23, 1, 'Cotisations Employeur', style.get('f8_border'))
        sheet_1.write(23, 2, employer_contribution_resume[0], style.get('numeric_f8_border'))
        sheet_1.write(23, 3, employer_contribution_resume[1], style.get('numeric_f8_border'))
        sheet_1.write(23, 4, employer_contribution_resume[2], style.get('numeric_f8_border'))
        sheet_1.write(23, 5, sum(employer_contribution_resume), style.get('numeric_f8_border'))
        sheet_1.write(24, 1, 'Cotisations travailleurs', style.get('f8_border'))
        sheet_1.write(24, 2, employee_contribution_resume[0], style.get('numeric_f8_border'))
        sheet_1.write(24, 3, employee_contribution_resume[1], style.get('numeric_f8_border'))
        sheet_1.write(24, 4, employee_contribution_resume[2], style.get('numeric_f8_border'))
        sheet_1.write(24, 5, sum(employee_contribution_resume), style.get('numeric_f8_border'))
        sheet_1.write(25, 5, sum(employer_contribution_resume) + sum(employee_contribution_resume) + sum(capped_resume),
                      style.get('numeric_f8_border'))
        sheet_1.write(28, 1, '** Reporter ci-dessus les totaux obtenus dans les onglets Mois 1, 2 et 3.',
                      style.get('f8_italic'))
        sheet_1.write(31, 2, 'FMFP', style.get('f8_border'))
        sheet_1.write(31, 3, 'FMFP', style.get('f8_border'))
        sheet_1.write(31, 4, 'FMFP', style.get('f8_border'))
        sheet_1.write(31, 5, '', style.get('numeric_f8_border'))
        sheet_1.write(32, 2, fmfp_resume[0], style.get('numeric_f8_border'))
        sheet_1.write(32, 3, fmfp_resume[1], style.get('numeric_f8_border'))
        sheet_1.write(32, 4, fmfp_resume[2], style.get('numeric_f8_border'))
        sheet_1.write(32, 5, sum(fmfp_resume), style.get('numeric_f8_border'))

        # Set cell width
        sheet_1.set_column(1, 5, 30)
        # Close workbook
        workbook.close()
        # Export xlsx file
        response = request.make_response(
            xls_file.getvalue(),
            [
                ('Content-Type', 'application/octet-stream'),
                ('Content-Disposition', content_disposition('%s.xlsx' % filename.replace('/', '_')))
            ]
        )
        return response

    def write_sheet_title(self, sheet, style):
        """
        Write title for sheet
        :param sheet: sheet to write
        :return:
        """
        sheet.write(0, 0, 'ANNEE-MOIS', style.get('f8_border'))
        sheet.write(0, 1, 'N° CNaPS', style.get('f8_border'))
        sheet.write(0, 2, 'TRAVAILLEURS', style.get('f8_border'))
        sheet.write(0, 4, 'Réf. Employeur', style.get('f8_border'))
        sheet.write(0, 5, 'DATE', style.get('f8_border'))
        sheet.write(0, 7, 'SALAIRE', style.get('f8_border'))
        sheet.write(0, 9, 'TP', style.get('f8_border'))
        sheet.write(0, 10, 'TOTAL', style.get('f8_border'))
        sheet.write(0, 12, ' COTISATIONS', style.get('f8_border'))
        sheet.write(0, 15, ' COT. FORMATION', style.get('f8_border'))
        sheet.write(0, 16, 'N° CIN', style.get('f8_border'))
        sheet.write(1, 0, '', style.get('f8_border_center'))
        sheet.write(1, 1, '', style.get('f8_border_center'))
        sheet.write(1, 2, 'NOM', style.get('f8_border_center'))
        sheet.write(1, 3, 'PRENOMS', style.get('f8_border_center'))
        sheet.write(1, 4, '', style.get('f8_border_center'))
        sheet.write(1, 5, 'ENTREE', style.get('f8_border_center'))
        sheet.write(1, 6, 'DEPART', style.get('f8_border_center'))
        sheet.write(1, 7, 'DU MOIS', style.get('f8_border_center'))
        sheet.write(1, 8, 'AVANTAGE', style.get('f8_border_center'))
        sheet.write(1, 9, '', style.get('f8_border_center'))
        sheet.write(1, 10, 'NON PLAFONNE', style.get('f8_border_center'))
        sheet.write(1, 11, 'PLAFONNE', style.get('f8_border_center'))
        sheet.write(1, 12, 'EMPLOYEUR', style.get('f8_border_center'))
        sheet.write(1, 13, 'TRAVAILLEUR', style.get('f8_border_center'))
        sheet.write(1, 14, 'TOTAL', style.get('f8_border_center'))
        sheet.write(1, 15, 'EMPLOYEUR', style.get('f8_border_center'))
        sheet.write(1, 16, '', style.get('f8_border_center'))
