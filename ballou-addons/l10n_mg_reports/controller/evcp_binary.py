# -*- coding: utf-8 -*-
'''
Created on 16 avr. 2018

@author: m.raharijaona
'''

import calendar

from io import BytesIO
import datetime

import xlsxwriter

from odoo import api, models
from odoo import http, _
from odoo.http import content_disposition, request
from dateutil.relativedelta import relativedelta
from datetime import datetime, date


class EvcpController(http.Controller):

    def compute_years(self, date):
        nbr = []
        for year in range(2):
            new = int(date) - year
            nbr.append(new)
        return sorted(nbr)

    @http.route('/web/evcp_binary/download_evcp', type="http", auth="user")
    def download_evcp(self, p_start_date, p_end_date, p_period, p_is_custom, p_date_start, **kwargs):

        """ Function to import product order state as xls """
        filename = "EVCP.xlsx"
        xls_file = BytesIO()
        workbook = xlsxwriter.Workbook(xls_file)
        date_start = int(p_date_start) if p_date_start else datetime.today().year
        p_start_date = p_start_date.split('__')
        p_end_date = p_end_date.split('__')
        p_start_date = date(int(p_start_date[0]), int(p_start_date[1]), int(p_start_date[2]))
        p_end_date = date(int(p_end_date[0]), int(p_end_date[1]), int(p_end_date[2]))

        # Text formating
        title_format = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': 'white'
        })
        text_format = workbook.add_format({
            'border': 1,
            'align': 'right',
            'valign': 'vcenter',
            'fg_color': 'white'
        })
        bolding = workbook.add_format()
        bolding.set_bold(True)

        # Create sheet
        worksheet = workbook.add_worksheet('EVCP')

        # Adjust column
        worksheet.set_column('A:A', 40)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 20)
        worksheet.set_column('E:E', 20)
        worksheet.set_column('F:F', 20)

        # Get search domain
        is_custom = p_is_custom
        res = dict()
        if is_custom == 'True':
            list_years = self.compute_years(date_start)
        else:
            period = p_period.split('_')
            code, t_code = period[0], period[1]
            today = date.today()
            if code == '3':
                years = today.year if t_code == '1' else today.year - 1
                list_years = self.compute_years(years)
        for year in list_years:
            date_first = date(year, 1, 1)
            date_end = date(year, 12, 31)
            domain = [('date_maturity', '>=', date_first), ('date_maturity', '<=', date_end)]
            domain_prec = [('date_maturity', '>=', date_first - relativedelta(years=1)),
                           ('date_maturity', '<=', date_end - relativedelta(years=1))]
            # Complete data
            account_moves = request.env['account.move.line'].search(domain)
            account_moves_prec = request.env['account.move.line'].search(domain_prec)
            result = {
                'result_prec_cap': 0, 'result_prec_prime': 0, 'result_prec_ecart': 0, 'result_prec_result': 0,
                'result_prec_t': 0,
                'change_meth_cap': 0, 'change_meth_prime': 0, 'change_meth_ecart': 0, 'change_meth_result': 0,
                'change_meth_t': 0,
                'correct_cap': 0, 'correct_prime': 0, 'correct_ecart': 0, 'correct_result': 0, 'correct_t': 0,
                'prod_charge_cap': 0, 'prod_charge_prime': 0, 'prod_charge_ecart': 0, 'prod_charge_result': 0,
                'prod_charge_t': 0,
                'affect_cap': 0, 'affect_prime': 0, 'affect_ecart': 0, 'affect_result': 0, 'affect_t': 0,
                'operation_cap': 0, 'operation_prime': 0, 'operation_ecart': 0, 'operation_result': 0, 'operation_t': 0,
                'resultat_cap': 0, 'resultat_prime': 0, 'resultat_ecart': 0, 'resultat_result': 0, 'resultat_t': 0,
                'result_cap': 0, 'result_prime': 0, 'result_ecart': 0, 'result_result': 0, 'result_t': 0,
            }
            for account_prec in account_moves_prec:
                current_code_prec = account_prec.account_id.code

                if current_code_prec == '1010000':
                    result['result_prec_cap'] -= account_prec.balance if account_prec.balance < 0 else 0
                if current_code_prec[:3] == '106':
                    result['result_prec_prime'] -= account_prec.balance if account_prec.balance < 0 else 0
                if current_code_prec[:3] == '110' or current_code_prec[:3] == '120':
                    result['result_prec_result'] -= account_prec.balance if account_prec.balance < 0 else 0
                if current_code_prec[:3] == '129':
                    result['result_prec_result'] -= account_prec.balance if account_prec.balance > 0 else 0

            for account in account_moves:
                current_code = account.account_id.code
                # RESULTAT
                if current_code[:2] in ['60', '61', '62', '63', '64', '65', '66', '68', '69']:
                    result['resultat_result'] -= account.balance
                if current_code[:2] in ['70', '71', '72', '75', '76', '78']:
                    result['resultat_result'] -= account.balance
                # RESULTAT

                result['result_prec_t'] = result['result_prec_cap'] + result['result_prec_prime'] + result[
                    'result_prec_ecart'] + result['result_prec_result']
                result['change_meth_t'] = result['change_meth_cap'] + result['change_meth_prime'] + result[
                    'change_meth_ecart'] + result['change_meth_result']
                result['correct_t'] = result['correct_cap'] + result['correct_prime'] + result['correct_ecart'] + \
                                      result['correct_result']
                result['prod_charge_t'] = result['prod_charge_cap'] + result['prod_charge_prime'] + result[
                    'prod_charge_ecart'] + result['prod_charge_result']
                result['affect_t'] = result['affect_cap'] + result['affect_prime'] + result['affect_ecart'] + result[
                    'affect_result']
                result['operation_t'] = result['operation_cap'] + result['operation_prime'] + result[
                    'operation_ecart'] + result['operation_result']
                result['resultat_t'] = result['resultat_cap'] + result['resultat_prime'] + result['resultat_ecart'] + \
                                       result['resultat_result']
                result['result_cap'] = result['result_prec_cap'] + result['change_meth_cap'] + result['correct_cap'] + \
                                       result['prod_charge_cap'] + result['affect_cap'] + result['operation_cap'] + \
                                       result['resultat_cap']
                result['result_prime'] = result['result_prec_prime'] + result['change_meth_prime'] + result[
                    'correct_prime'] + result['prod_charge_prime'] + result['affect_prime'] + result[
                                             'operation_prime'] + result['resultat_prime']
                result['result_ecart'] = result['result_prec_ecart'] + result['change_meth_ecart'] + result[
                    'correct_ecart'] + result['prod_charge_ecart'] + result['affect_ecart'] + result[
                                             'operation_ecart'] + result['resultat_ecart']
                result['result_result'] = result['result_prec_result'] + result['change_meth_result'] + result[
                    'correct_result'] + result['prod_charge_result'] + result['affect_result'] + result[
                                              'operation_result'] + result['resultat_result']
                result['result_t'] = result['result_cap'] + result['result_prime'] + result['result_ecart'] + result[
                    'result_result']

            res.update({str(year): result})

        # Complete file

        year_prec = list_years[0] - 1
        worksheet.write(0, 0, 'ETAT DE VARIATION DES CAPITAUX PROPRES', bolding)
        worksheet.write(0, 1, 'CAPITAL SOCIAL', title_format)
        worksheet.write(0, 2, 'PRIMES ET RESERVES', title_format)
        worksheet.write(0, 3, 'ECART D\'EVALUATION', title_format)
        worksheet.write(0, 4, 'RESULTAT ET REPORT A NOUVEAU', title_format)
        worksheet.write(0, 5, 'TOTAL', title_format)
        worksheet.write(1, 0, 'Solde precedent {}'.format(year_prec), bolding)
        # DEBUT

        year_0 = res.get(str(list_years[0]))
        worksheet.write(1, 1, '{:10,.2f}'.format(float(year_0['result_prec_cap'])).replace(',', ' ').replace('.', ','),
                        bolding)
        worksheet.write(1, 2,
                        '{:10,.2f}'.format(float(year_0['result_prec_prime'])).replace(',', ' ').replace('.', ','),
                        bolding)
        worksheet.write(1, 3,
                        '{:10,.2f}'.format(float(year_0['result_prec_ecart'])).replace(',', ' ').replace('.', ','),
                        bolding)
        worksheet.write(1, 4,
                        '{:10,.2f}'.format(float(year_0['result_prec_result'])).replace(',', ' ').replace('.', ','),
                        bolding)
        worksheet.write(1, 5, '{:10,.2f}'.format(float(year_0['result_prec_t'])).replace(',', ' ').replace('.', ','),
                        bolding)
        worksheet.write(2, 0, 'Changement de methode comptable', text_format)
        worksheet.write(2, 1, '{:10,.2f}'.format(float(year_0['change_meth_cap'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(2, 2,
                        '{:10,.2f}'.format(float(year_0['change_meth_prime'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(2, 3,
                        '{:10,.2f}'.format(float(year_0['change_meth_ecart'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(2, 4,
                        '{:10,.2f}'.format(float(year_0['change_meth_result'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(2, 5, '{:10,.2f}'.format(float(year_0['change_meth_t'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(3, 0, 'Correction d\'erreurs', text_format)
        worksheet.write(3, 1, '{:10,.2f}'.format(float(year_0['correct_cap'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(3, 2, '{:10,.2f}'.format(float(year_0['correct_prime'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(3, 3, '{:10,.2f}'.format(float(year_0['correct_ecart'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(3, 4, '{:10,.2f}'.format(float(year_0['correct_result'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(3, 5, '{:10,.2f}'.format(float(year_0['correct_t'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(4, 0, 'Autres produits et charges', text_format)
        worksheet.write(4, 1, '{:10,.2f}'.format(float(year_0['prod_charge_cap'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(4, 2,
                        '{:10,.2f}'.format(float(year_0['prod_charge_prime'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(4, 3,
                        '{:10,.2f}'.format(float(year_0['prod_charge_ecart'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(4, 4,
                        '{:10,.2f}'.format(float(year_0['prod_charge_result'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(4, 5, '{:10,.2f}'.format(float(year_0['prod_charge_t'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(5, 0, 'Affectation du resultat precedent', text_format)
        worksheet.write(5, 1, '{:10,.2f}'.format(float(year_0['affect_cap'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(5, 2, '{:10,.2f}'.format(float(year_0['affect_prime'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(5, 3, '{:10,.2f}'.format(float(year_0['affect_ecart'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(5, 4, '{:10,.2f}'.format(float(year_0['affect_result'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(5, 5, '{:10,.2f}'.format(float(year_0['affect_t'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(6, 0, 'Operations en capital', text_format)
        worksheet.write(6, 1, '{:10,.2f}'.format(float(year_0['operation_cap'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(6, 2, '{:10,.2f}'.format(float(year_0['operation_prime'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(6, 3, '{:10,.2f}'.format(float(year_0['operation_ecart'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(6, 4, '{:10,.2f}'.format(float(year_0['operation_result'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(6, 5, '{:10,.2f}'.format(float(year_0['operation_t'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(7, 0, 'Resultat net', text_format)
        worksheet.write(7, 1, '{:10,.2f}'.format(float(year_0['resultat_cap'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(7, 2, '{:10,.2f}'.format(float(year_0['resultat_prime'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(7, 3, '{:10,.2f}'.format(float(year_0['resultat_ecart'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(7, 4, '{:10,.2f}'.format(float(year_0['resultat_result'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(7, 5, '{:10,.2f}'.format(float(year_0['resultat_t'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(8, 0, 'Solde de l\'annee {}'.format(list_years[0]), bolding)
        worksheet.write(8, 1, '{:10,.2f}'.format(float(year_0['result_cap'])).replace(',', ' ').replace('.', ','),
                        bolding)
        worksheet.write(8, 2, '{:10,.2f}'.format(float(year_0['result_prime'])).replace(',', ' ').replace('.', ','),
                        bolding)
        worksheet.write(8, 3, '{:10,.2f}'.format(float(year_0['result_ecart'])).replace(',', ' ').replace('.', ','),
                        bolding)
        worksheet.write(8, 4, '{:10,.2f}'.format(float(year_0['result_result'])).replace(',', ' ').replace('.', ','),
                        bolding)
        worksheet.write(8, 5, '{:10,.2f}'.format(float(year_0['result_t'])).replace(',', ' ').replace('.', ','),
                        bolding)

        year_1 = res.get(str(list_years[1]))
        worksheet.write(9, 0, 'Changement de methode comptable', text_format)
        worksheet.write(9, 1, '{:10,.2f}'.format(float(year_1['change_meth_cap'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(9, 2,
                        '{:10,.2f}'.format(float(year_1['change_meth_prime'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(9, 3,
                        '{:10,.2f}'.format(float(year_1['change_meth_ecart'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(9, 4,
                        '{:10,.2f}'.format(float(year_1['change_meth_result'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(9, 5, '{:10,.2f}'.format(float(year_1['change_meth_t'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(10, 0, 'Correction d\'erreurs', text_format)
        worksheet.write(10, 1, '{:10,.2f}'.format(float(year_1['correct_cap'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(10, 2, '{:10,.2f}'.format(float(year_1['correct_prime'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(10, 3, '{:10,.2f}'.format(float(year_1['correct_ecart'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(10, 4, '{:10,.2f}'.format(float(year_1['correct_result'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(10, 5, '{:10,.2f}'.format(float(year_1['correct_t'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(11, 0, 'Autres produits et charges', text_format)
        worksheet.write(11, 1, '{:10,.2f}'.format(float(year_1['prod_charge_cap'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(11, 2,
                        '{:10,.2f}'.format(float(year_1['prod_charge_prime'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(11, 3,
                        '{:10,.2f}'.format(float(year_1['prod_charge_ecart'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(11, 4,
                        '{:10,.2f}'.format(float(year_1['prod_charge_result'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(11, 5, '{:10,.2f}'.format(float(year_1['prod_charge_t'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(12, 0, 'Affectation du resultat precedent', text_format)
        worksheet.write(12, 1, '{:10,.2f}'.format(float(year_1['affect_cap'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(12, 2, '{:10,.2f}'.format(float(year_1['affect_prime'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(12, 3, '{:10,.2f}'.format(float(year_1['affect_ecart'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(12, 4, '{:10,.2f}'.format(float(year_1['affect_result'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(12, 5, '{:10,.2f}'.format(float(year_1['affect_t'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(13, 0, 'Operations en capital', text_format)
        worksheet.write(13, 1, '{:10,.2f}'.format(float(year_1['operation_cap'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(13, 2, '{:10,.2f}'.format(float(year_1['operation_prime'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(13, 3, '{:10,.2f}'.format(float(year_1['operation_ecart'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(13, 4,
                        '{:10,.2f}'.format(float(year_1['operation_result'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(13, 5, '{:10,.2f}'.format(float(year_1['operation_t'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(14, 0, 'Resultat net', text_format)
        worksheet.write(14, 1, '{:10,.2f}'.format(float(year_1['resultat_cap'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(14, 2, '{:10,.2f}'.format(float(year_1['resultat_prime'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(14, 3, '{:10,.2f}'.format(float(year_1['resultat_ecart'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(14, 4, '{:10,.2f}'.format(float(year_1['resultat_result'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(14, 5, '{:10,.2f}'.format(float(year_1['resultat_t'])).replace(',', ' ').replace('.', ','),
                        text_format)
        worksheet.write(15, 0, 'Solde de l\'annee {}'.format(list_years[1]), bolding)
        worksheet.write(15, 1, '{:10,.2f}'.format(float(year_1['result_cap'])).replace(',', ' ').replace('.', ','),
                        bolding)
        worksheet.write(15, 2, '{:10,.2f}'.format(float(year_1['result_prime'])).replace(',', ' ').replace('.', ','),
                        bolding)
        worksheet.write(15, 3, '{:10,.2f}'.format(float(year_1['result_ecart'])).replace(',', ' ').replace('.', ','),
                        bolding)
        worksheet.write(15, 4, '{:10,.2f}'.format(float(year_1['result_result'])).replace(',', ' ').replace('.', ','),
                        bolding)
        worksheet.write(15, 5, '{:10,.2f}'.format(float(year_1['result_t'])).replace(',', ' ').replace('.', ','),
                        bolding)

        # Return XLS files
        workbook.close()
        response = request.make_response(xls_file.getvalue(),
                                         [('Content-Type', 'application/octet-stream'),
                                          ('Content-Disposition', content_disposition(filename))])
        return response
