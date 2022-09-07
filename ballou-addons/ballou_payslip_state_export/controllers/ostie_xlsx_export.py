# coding: utf-8
import io

import xlsxwriter

from odoo import http, _
from odoo.http import request, content_disposition

GENDER = {'male': 'M', 'female': 'F', 'other': 'O'}

MONTHS = [
    (_('JANVIER'), _('FEVRIER'), _('MARS')),
    (_('AVRIL'), _('MAI'), _('JUIN')),
    (_('JUILLET'), _('AOUT'), _('SEPTEMBRE')),
    (_('OCTOBRE'), _('NOVEMBRE'), _('DECEMBRE')),
]


class OstieXlsxExport(http.Controller):

    @http.route('/web/binary/download_ostie_xlsx_file', type='http', auth="public")
    def download_ostie_xls_file(self, id, **args):
        """
                Function to export OSTIE state
                :param id:
                :param args:
                :return:
                """
        # Variable initialisation
        state_id = request.env['payslip.state.export'].browse(int(id))
        xls_file = io.BytesIO()
        company_id = state_id.company_id
        ostie_responsible_id = company_id.responsible_id
        date_range = state_id.get_date_range()
        domain = [
            ('state', '=', 'done'),
            ('date_to', '>=', date_range[0]),
            ('date_to', '<=', date_range[1]),
            ('company_id.id', '=', state_id.company_id.id)
        ]
        payslip_ids = request.env['hr.payslip'].search(domain)
        list_payslip_ids = []

        # Only take payslip line ostie amount superior to 0 and have line ostie
        for payslip_id in payslip_ids:
            for line_id in payslip_id.line_ids:
                if line_id.code == 'OSTIE' and line_id.amount > 0:
                    list_payslip_ids.append(payslip_id.id)

        all_payslip_ids = request.env['hr.payslip'].search([('id', 'in', list_payslip_ids)])

        employee_ids = all_payslip_ids.mapped('employee_id')
        sum_wages, total_crapped, total_employer_contribution, total_employee_contribution = [0, 0, 0], 0, 0, 0

        # Get salary rule value sme/ostie contribution
        smig_id = request.env['hr.salary.rule'].search([('code', '=', 'SMIG')])
        ostie_employer_threshold_id = request.env['hr.salary.rule'].search([('code', '=', 'TAUX_OSTIE_PAT')])
        ostie_threshold_id = request.env['hr.salary.rule'].search([('code', '=', 'TAUX_OSTIE')])

        sme = smig_id[0].amount_fix if smig_id else 0
        cnaps_ceiling = sme * 8
        employer_contribution = ostie_employer_threshold_id[0].amount_fix if ostie_employer_threshold_id else 0
        employee_contribution = ostie_threshold_id.amount_fix if ostie_threshold_id else 0

        filename = state_id.get_ostie_filename()
        months = MONTHS[int(state_id.quarter)]
        effectifs = all_payslip_ids.get_effectif_per_month(state_id)
        # Create workbook
        workbook = xlsxwriter.Workbook(xls_file)
        # Set default font size
        workbook.formats[0].set_font_size(8)
        # Set style
        style = state_id.get_default_format(workbook)
        # Create worksheet
        sheet_1 = workbook.add_worksheet('DNS')
        sheet_2 = workbook.add_worksheet('RECAP COTISATION')
        # Write sheet 1
        sheet_1.merge_range('A1:E1', 'ORGANISATION SANITAIRE TANANARIVIENNE INTER-ENTREPRISES',
                            style.get('bold_f9_center'))
        sheet_1.merge_range('G1:N1', 'DECLARATION NOMINATIVE DES SALAIRES VERSES AU TITRE DU ',
                            style.get('bold_f9_right'))
        sheet_1.write(0, 14, '%sE' % (str(int(state_id.quarter) + 1)) if state_id.quarter == '00' else '%sEME' % (
            str(int(state_id.quarter) + 1)), style.get('bold_f9_center_double_bottom_border'))
        sheet_1.write(0, 15, 'TRIMESTRE', style.get('bold_f9_center'))
        sheet_1.write(0, 16, '%s' % (state_id.year), style.get('bold_f9_center_double_bottom_border'))
        sheet_1.merge_range('A2:E2', 'O.S.T.I.E.', style.get('bold_f9_center'))
        sheet_1.merge_range('A3:E3', 'Rue Dr Zamenhof Behoririka 101 ANTANANARIVO', style.get('f9_center'))
        sheet_1.merge_range('A4:E4', 'Tél.: 22 265 78 / 22 274 76 / 22 251 42  FAX : 22 265 66',
                            style.get('f9_center'))
        sheet_1.merge_range('A5:E5', 'BP : 165 Antananarivo ', style.get('f9_center'))
        sheet_1.merge_range('A6:E6', 'e-mail : sadhostie@moov.mg      site web : www.ostie.mg',
                            style.get('f9_center'))
        sheet_1.merge_range('G3:H3', 'CODE ADHERENT :', style.get('bold_f9_center_top_left_bggray'))
        sheet_1.write(2, 8, company_id.ostie_member_code or '', style.get('bold_f9_center_top_bottom'))
        sheet_1.write(2, 9, '', style.get('bold_f9_center_top'))
        sheet_1.write(2, 10, '', style.get('bold_f9_center_top'))
        sheet_1.write(2, 11, '', style.get('bold_f9_center_top'))
        sheet_1.write(2, 12, 'FOLIO :', style.get('bold_f9_right_top_bggray'))
        sheet_1.write(2, 13, company_id.ostie_folio or '', style.get('bold_f9_center_top_right'))
        sheet_1.merge_range('O3:P3', 'Plafond par travailleur et par mois :', style.get('f9_left_bggray'))
        sheet_1.write(2, 16, cnaps_ceiling, style.get('numeric_f9'))
        sheet_1.merge_range('G4:H4', 'Raison Sociale :', style.get('bold_f9_center_left_bggray'))
        sheet_1.write(3, 8, company_id.name or '', style.get('bold_f9_left'))
        sheet_1.write(3, 13, '', style.get('bold_f9_center_right'))
        sheet_1.merge_range('O4:P4', 'Salaire Minimum d\'Embauche :', style.get('f9_left_bggray'))
        sheet_1.write(3, 16, sme, style.get('numeric_f9'))
        sheet_1.merge_range('G5:H5', 'Adresse :', style.get('bold_f9_center_left_bggray'))
        sheet_1.write(4, 8, company_id.street or '', style.get('f9_left'))
        sheet_1.write(4, 13, '', style.get('bold_f9_center_right'))
        sheet_1.merge_range('G6:H6', 'Tél :', style.get('bold_f9_center_left_bggray'))
        sheet_1.write(5, 8, company_id.phone or '', style.get('f9_left'))
        sheet_1.write(5, 9, 'eMail :', style.get('bold_f9_center_bggray'))
        sheet_1.write_url(5, 10, ostie_responsible_id.work_email if ostie_responsible_id else '', style.get('f9'))
        sheet_1.write(5, 13, '', style.get('bold_f9_center_right'))
        sheet_1.write(6, 6, 'STAT :', style.get('bold_f9_center_left_bggray'))
        sheet_1.merge_range('H7:I7', company_id.stat or '', style.get('f9_left'))
        sheet_1.write(6, 9, 'NIF : ', style.get('bold_f9_center_bggray'))
        sheet_1.write(6, 10, company_id.nif or '', style.get('bold_f9_center_bggray'))
        sheet_1.write(6, 13, '', style.get('bold_f9_center_right'))
        sheet_1.write(7, 6, 'ACTIVITÉ :', style.get('bold_f9_center_left_bggray'))
        sheet_1.merge_range('H8:I8', company_id.company_activity or '', style.get('f9_left'))
        sheet_1.write(7, 11, 'REGIME : ', style.get('bold_f9_center_bggray'))
        sheet_1.write(7, 12, 'GENERAL', style.get('bold_f9_center'))
        sheet_1.write(7, 13, '', style.get('bold_f9_center_right'))
        sheet_1.merge_range('G9:H9', 'Taux Employeur :', style.get('f9_center_bggray_border'))
        sheet_1.write(8, 8, str(employer_contribution) + '%', style.get('f9_center'))
        sheet_1.write(8, 9, 'Travailleur : ', style.get('f9_center_bggray'))
        sheet_1.write(8, 10, '', style.get('f9_center_bggray'))
        sheet_1.write(8, 11, str(employee_contribution) + '%', style.get('f9_center'))
        sheet_1.write(8, 13, '', style.get('bold_f9_center_right'))
        sheet_1.merge_range('G10:H10', 'N° Cnaps Employeur :', style.get('f9_center_bggray_border'))
        sheet_1.write(9, 8, company_id.cnaps_member_code or '', style.get('f9_center'))
        sheet_1.write(9, 13, '', style.get('bold_f9_center_right'))
        sheet_1.write(10, 6, '', style.get('border_left_bottom'))
        sheet_1.write(10, 7, '', style.get('border_bottom'))
        sheet_1.write(10, 8, '', style.get('border_bottom'))
        sheet_1.write(10, 9, '', style.get('border_bottom'))
        sheet_1.write(10, 10, '', style.get('border_bottom'))
        sheet_1.write(10, 11, '', style.get('border_bottom'))
        sheet_1.write(10, 12, '', style.get('border_bottom'))
        sheet_1.write(10, 13, '', style.get('border_right_bottom'))
        sheet_1.write(6, 0, 'BOA Andravoahangy   00009 05600 10762050010 23', style.get('f9_left'))
        sheet_1.write(7, 0, 'BNI-CL Analakely  00005 00001 01232020200 71', style.get('f9_left'))
        sheet_1.write(8, 0, 'BFV-SG  Antaninarenina  00008 00005 21000155438 43', style.get('f9_left'))
        sheet_1.write(9, 0, 'BMOI Analamahitsy 00004 00003 01500800184 32', style.get('f9_left'))
        sheet_1.write(10, 0, 'ACCES BANQUE Antaninandro  00011 00003 24100035111 77', style.get('f9_left'))
        sheet_1.write(11, 0, 'ORANGE MONEY  032 24 704 67  - MVOLA 034 31 564 90', style.get('f9_left'))
        sheet_1.write(13, 0, 'N°', style.get('f9_center_border_arial'))
        sheet_1.write(13, 1, 'MATRICULE', style.get('f9_center_border_arial'))
        sheet_1.write(13, 2, 'NOM DU TRAVAILLEUR', style.get('f9_center_border_arial'))
        sheet_1.write(13, 3, 'PRENOMS DU TRAVAILLEUR', style.get('f9_center_border_arial'))
        sheet_1.write(13, 4, 'SEXE', style.get('f9_center_border_arial'))
        sheet_1.write(13, 5, 'DATE DE\nNAISSANCE', style.get('f9_center_border_arial'))
        sheet_1.write(13, 6, 'DATE D\'EMBAUCHE', style.get('f9_center_border_arial'))
        sheet_1.write(13, 7, 'DATE DE\nDEBAUCHE', style.get('f9_center_border_arial'))
        sheet_1.write(13, 8, 'FONCTION', style.get('f9_center_border_arial'))
        sheet_1.write(13, 9, 'N°CNAPS', style.get('f9_center_border_arial'))
        sheet_1.write(13, 10, 'N°CIN', style.get('f9_center_border_arial'))
        sheet_1.write(13, 11, 'SALAIRE 1er MOIS', style.get('f9_center_border_arial'))
        sheet_1.write(13, 12, 'SALAIRE 2ème MOIS', style.get('f9_center_border_arial'))
        sheet_1.write(13, 13, 'SALAIRE 3ème MOIS', style.get('f9_center_border_arial'))
        sheet_1.write(13, 14, 'TOTAUX SALAIRES\nNON PLAFONNES', style.get('f9_center_border_arial'))
        sheet_1.write(13, 15, 'TOTAUX SALAIRES\nPLAFONNES', style.get('f9_center_border_arial'))
        sheet_1.write(13, 16, 'PART\nEMPLOYEUR 5%', style.get('f9_center_border_arial'))
        sheet_1.write(13, 17, 'PART\nTRAVAILLEUR 1%', style.get('f9_center_border_arial'))
        # Write sheet 1 lines
        first_line, last_row = 14, 0
        for key, employee_id in enumerate(employee_ids):
            # current employee variable
            row = first_line + key
            last_row = row
            payslip_ids = all_payslip_ids.filtered(lambda p: p.employee_id.id == employee_id.id)
            wages = payslip_ids.get_wages_by_month(state_id)
            sum_wages[0] += wages[0]
            sum_wages[1] += wages[1]
            sum_wages[2] += wages[2]
            crapped = (cnaps_ceiling if wages[0] > cnaps_ceiling else wages[0]) + (
                cnaps_ceiling if wages[1] > cnaps_ceiling else wages[1]) + (
                          cnaps_ceiling if wages[2] > cnaps_ceiling else wages[2])
            total_crapped += crapped
            job_id = employee_id.job_id
            first_contract_id = employee_id.contract_ids[0]
            last_contract_id = employee_id.contract_ids[-1]

            if last_contract_id:
                contract_date_end = ''
                if not last_contract_id.date_end:
                    contract_date_end = last_contract_id.date_end
                elif last_contract_id.date_end.month >= date_range[0].month and last_contract_id.date_end.month <= \
                        date_range[1].month:
                    contract_date_end = last_contract_id.date_end

            total_employer_contribution += round((crapped * employer_contribution / 100), 2)
            total_employee_contribution += round((crapped * employee_contribution / 100), 2)
            # Write lines
            sheet_1.write(row, 0, key + 1, style.get('f9_border'))
            sheet_1.write(row, 1, employee_id.registration_number or '', style.get('f9_border'))
            sheet_1.write(row, 2, employee_id.lastname.upper() if employee_id.firstname else '', style.get('f9_border'))
            sheet_1.write(row, 3, employee_id.firstname.upper() if employee_id.firstname else '',
                          style.get('f9_border'))
            sheet_1.write(row, 4, GENDER.get(employee_id.gender), style.get('f9_border_center_date'))
            sheet_1.write(row, 5, employee_id.birthday, style.get('f9_border_center_date'))
            sheet_1.write(row, 6, first_contract_id.first_contract_date if first_contract_id else '',
                          style.get('f9_border_center_date'))
            sheet_1.write(row, 7, contract_date_end or '', style.get('f9_border_center_date'))
            sheet_1.write(row, 8, employee_id.job_id.name.upper() if job_id else '', style.get('f9_border_center'))
            sheet_1.write(row, 9, employee_id.cnaps_number or '-', style.get('f9_border_center'))
            sheet_1.write(row, 10,
                          employee_id.identification_id if employee_id.identification_id else employee_id.passport_id or '-',
                          style.get('f9_border_center'))
            sheet_1.write(row, 11, wages[0] or '-', style.get('numeric_f9_border_without_space'))
            sheet_1.write(row, 12, wages[1] or '-', style.get('numeric_f9_border_without_space'))
            sheet_1.write(row, 13, wages[2] or '-', style.get('numeric_f9_border_without_space'))
            sheet_1.write(row, 14, (wages[0] + wages[1] + wages[2]) or '-',
                          style.get('numeric_f9_border_without_space'))
            sheet_1.write(row, 15, crapped or '-', style.get('numeric_f9_border_without_space'))
            sheet_1.write(row, 16, (crapped * employer_contribution / 100) or '-', style.get('numeric_f9_border'))
            sheet_1.write(row, 17, (crapped * employee_contribution / 100) or '-', style.get('numeric_f9_border'))
        # Write sum line
        row = last_row + 1
        total_uncrapped = sum_wages[0] + sum_wages[1] + sum_wages[2]
        sheet_1.merge_range('J%s:K%s' % (row + 1, row + 1), 'TOTAUX', style.get('bold_f9_center_border'))
        sheet_1.write(row, 11, sum_wages[0] or '-', style.get('numeric_f9_double_border'))
        sheet_1.write(row, 12, sum_wages[1] or '-', style.get('numeric_f9_double_border'))
        sheet_1.write(row, 13, sum_wages[2] or '-', style.get('numeric_f9_double_border'))
        sheet_1.write(row, 14, total_uncrapped or '-', style.get('numeric_f9_double_border'))
        sheet_1.write(row, 15, total_crapped or '-', style.get('numeric_f9_double_border'))
        sheet_1.write(row, 16, total_employer_contribution or '-', style.get('numeric_f9_double_border'))
        sheet_1.write(row, 17, total_employee_contribution or '-', style.get('numeric_f9_double_border'))
        # Write sheet 2
        sheet_2.write(0, 0, 'ETAT RECAPITULATIF DES DECLARATIONS NOMINATIVES DE SALAIRES:',
                      style.get('bold_underline_f11_arial'))
        sheet_2.write(2, 1, 'CODE ADHERENT', style.get('f10_arial'))
        sheet_2.merge_range('C3:F3', company_id.ostie_member_code or '', style.get('f10_border_center_arial'))
        sheet_2.write(3, 1, 'RAISON SOCIALE', style.get('f10_arial'))
        sheet_2.merge_range('C4:F4', company_id.name or '', style.get('f10_border_center_arial'))
        sheet_2.write(4, 1, 'N° Téléphone', style.get('f10_arial'))
        sheet_2.merge_range('C5:F5', company_id.phone or '', style.get('f10_border_center_arial'))
        sheet_2.write(5, 1, 'ADRESSE', style.get('f10_arial'))
        sheet_2.merge_range('C6:F6', company_id.street or '', style.get('f10_border_center_arial'))
        sheet_2.write(6, 1, 'Adresse Email', style.get('f10_arial'))
        sheet_2.merge_range('C7:F7', ostie_responsible_id.work_email if ostie_responsible_id else '',
                            style.get('f10_border_center_arial'))
        sheet_2.write(8, 0, 'COTISATIONS :', style.get('bold_underline_f10_arial'))
        sheet_2.write(9, 1, 'TRIMESTRE', style.get('f10_arial'))
        sheet_2.write(9, 2, '%se' % (str(int(state_id.quarter) + 1)) if state_id.quarter == '00' else '%sème' % (
            str(int(state_id.quarter) + 1)), style.get('f11_center_border'))
        sheet_2.write(10, 1, 'ANNEE', style.get('f10_arial'))
        sheet_2.write(10, 2, str(int(state_id.year)), style.get('f11_center_border'))
        sheet_2.write(11, 1, 'MODE DE PAIEMENT', style.get('f10_arial'))
        sheet_2.write(11, 2, '', style.get('f11_center_border'))
        sheet_2.write(12, 1, 'REFERENCE', style.get('f10_arial'))
        sheet_2.write(12, 2, filename, style.get('f11_center_border'))
        sheet_2.write(13, 1, 'Taux Employeur', style.get('f10_arial'))
        sheet_2.write(13, 2, str(employer_contribution) + '%', style.get('f11_center_border'))
        sheet_2.write(14, 1, 'Taux Travailleur', style.get('f10_arial'))
        sheet_2.write(14, 2, str(employee_contribution) + '%', style.get('f11_center_border'))
        sheet_2.write(15, 1, 'Montant Plafonnement', style.get('f10_arial'))
        sheet_2.write(15, 2, cnaps_ceiling, style.get('numeric_f11_center_border'))
        # sheet_2.write(15, 3, company_id.declaration_date, style.get('f9_bold_date'))
        sheet_2.write(16, 1, 'Montant SME', style.get('f10_arial'))
        sheet_2.write(16, 2, sme, style.get('numeric_f11_center_border'))
        # sheet_2.write(16, 3, company_id.declaration_date, style.get('f9_bold_date'))
        sheet_2.write(18, 0, 'MOIS CONCERNES :', style.get('bold_underline_f10_arial'))
        sheet_2.write(18, 2, months[0], style.get('f10_border_center_arial'))
        sheet_2.write(18, 3, months[1], style.get('f10_border_center_arial'))
        sheet_2.write(18, 4, months[2], style.get('f10_border_center_arial'))
        sheet_2.write(21, 0, 'RECAPITULATION :', style.get('bold_underline_f10_arial'))
        sheet_2.write(21, 1, '', style.get('f10_arial_bottom'))
        sheet_2.write(21, 2, 'Mois 1', style.get('bold_f10_center_border_arial'))
        sheet_2.write(21, 3, 'Mois 2', style.get('bold_f10_center_border_arial'))
        sheet_2.write(21, 4, 'Mois 3', style.get('bold_f10_center_border_arial'))
        sheet_2.write_rich_string('B23',
                                  style.get('f10_border_arial'), 'Effectif mensuel',
                                  style.get('bold_f10_border_arial'), ' (OBLIGATOIRE)')
        sheet_2.write(22, 0, '', style.get('f10_arial_right'))
        sheet_2.write(22, 2, effectifs[0], style.get('numeric_f10_arial_border'))
        sheet_2.write(22, 3, effectifs[1], style.get('numeric_f10_arial_border'))
        sheet_2.write(22, 4, effectifs[2], style.get('numeric_f10_arial_border'))
        sheet_2.write(22, 5, 'TOTAUX', style.get('bold_f10_center_border_arial'))
        sheet_2.write(23, 1, u'Totaux Salaires non plafonnés', style.get('f10_border_arial'))
        sheet_2.write(23, 2, sum_wages[0], style.get('numeric_f10_arial_border'))
        sheet_2.write(23, 3, sum_wages[1], style.get('numeric_f10_arial_border'))
        sheet_2.write(23, 4, sum_wages[2], style.get('numeric_f10_arial_border'))
        sheet_2.write(23, 5, total_uncrapped, style.get('numeric_f10_arial_border'))
        sheet_2.write(24, 1, u'Totaux Salaires plafonnés', style.get('f10_border_arial'))
        sheet_2.write(24, 2, '', style.get('numeric_f10_arial_border'))
        sheet_2.write(24, 3, '', style.get('numeric_f10_arial_border'))
        sheet_2.write(24, 4, '', style.get('numeric_f10_arial_border'))
        sheet_2.write(24, 5, total_crapped, style.get('numeric_f10_arial_border'))
        sheet_2.write(25, 1, u'Cotisations Employeur EMPLOYEUR (A)', style.get('f10_border_arial'))
        sheet_2.write(25, 2, '', style.get('numeric_f10_arial_border'))
        sheet_2.write(25, 3, '', style.get('numeric_f10_arial_border'))
        sheet_2.write(25, 4, '', style.get('numeric_f10_arial_border'))
        sheet_2.write(25, 5, total_employer_contribution, style.get('numeric_f10_arial_border'))
        sheet_2.write(26, 1, u'Cotisations Travailleurs (B)', style.get('f10_border_arial'))
        sheet_2.write(26, 2, '', style.get('numeric_f10_arial_border'))
        sheet_2.write(26, 3, '', style.get('numeric_f10_arial_border'))
        sheet_2.write(26, 4, '', style.get('numeric_f10_arial_border'))
        sheet_2.write(26, 5, total_employee_contribution, style.get('numeric_f10_arial_border'))
        sheet_2.merge_range('B28:E28', 'Total cotisations A+B', style.get('f10_border_center_arial'))
        sheet_2.write(27, 5, total_employee_contribution + total_employer_contribution,
                      style.get('numeric_f10_arial_border'))
        sheet_2.merge_range('B29:E29', u'Majoration de retard 10%', style.get('f10_border_center_arial'))
        sheet_2.write(28, 5, '', style.get('numeric_f10_arial_border'))
        sheet_2.merge_range('B30:E30', u'Trop perçu antérieur à déduire', style.get('f10_border_center_arial'))
        sheet_2.write(29, 5, '', style.get('numeric_f10_arial_border'))
        sheet_2.merge_range('B31:E31', u'COTISATIONS NET A PAYER', style.get('bold_f10_arial_center_italic_border'))
        sheet_2.write(30, 5, total_employee_contribution + total_employer_contribution,
                      style.get('numeric_f10_arial_border'))

        # Set cell width
        sheet_1.set_column(2, 3, 30)
        sheet_1.set_column(5, 17, 20)
        sheet_1.set_row(13, 30)
        sheet_1.set_column('A:A', 7)
        sheet_1.set_column('B:B', 15)
        sheet_1.set_column('D:D', 35)
        sheet_1.set_column('G:G', 22)
        sheet_1.set_column('M:M', 22)
        sheet_1.set_column('N:N', 22)
        sheet_1.set_column('O:O', 22)
        sheet_1.set_column('P:P', 22)
        sheet_1.set_column('Q:Q', 19)
        sheet_1.set_column('R:R', 19)
        sheet_2.set_column('A:A', 25)
        sheet_2.set_column('B:B', 45)
        sheet_2.set_column('C:C', 25)
        sheet_2.set_column('D:D', 25)
        sheet_2.set_column('E:E', 25)
        sheet_2.set_column('F:F', 25)

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
