# -*- encoding: utf-8 -*-

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2019 eTech (<https://www.etechconsulting-mg.com/>). All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

import ast
import copy
from operator import itemgetter

from odoo import models, fields, exceptions, api, _
from odoo.tools import ustr
from odoo.tools.misc import formatLang
from odoo.tools.safe_eval import safe_eval
from dateutil.relativedelta import relativedelta


class AccountFinancialReportInherit(models.Model):
    _inherit = 'account.financial.html.report'

    type_financial_report_mg = fields.Selection(string="Type de rapport financier",
                                                selection=[('balance_sheet', "Bilan actif"),
                                                           ('balance_cp_p', "Bilan des capitaux propres et passifs"),
                                                           ('income_statement', "Compte de résultat"),
                                                           ('ftt_d', "Flux de trésorerie direct"),
                                                           ('ftt_i', "Flux de tresorerie indirect"),
                                                           ('cr_n', "Compte de résultat par nature"),
                                                           ('cr_f', "Compte de résultat par fonction"),
                                                           ('passif', "Passif")])
    monetary_unit_mg = fields.Boolean(string="Unité monétaire", default=False)
    note_mg = fields.Boolean(string="Note", default=False)
    n_gross_mg = fields.Boolean(string="N Brut", default=False)
    n_amort_prov_mg = fields.Boolean(string="N Amort/prov", default=False)
    last_year_mg = fields.Boolean(string="N-1", default=False)

    #     def _get_columns_name(self, options):
    #         columns = [{'name': ''}]
    #
    #         # Modified part of native code
    #         if self.note_mg:
    #             columns += [{'name': 'Note'}]
    #
    #         if self.debit_credit and not options.get('comparison', {}).get('periods', False):
    #             columns += [{'name': _('Debit'), 'class': 'number'}, {'name': _('Credit'), 'class': 'number'}]
    #         if not self.filter_date:
    #             if self.date_range:
    #                 self.filter_date = {'mode': 'range', 'filter': 'this_year'}
    #             else:
    #                 self.filter_date = {'mode': 'single', 'filter': 'today'}
    #
    #         # Modified part of native code
    #         if self.type_financial_report_mg:
    #             if self.n_gross_mg:
    #                 columns += [{'name': '%s Brut' % self.format_date(options), 'class': 'number'}]
    #             if self.n_amort_prov_mg:
    #                 columns += [{'name': '%s Amort/prov' % self.format_date(options), 'class': 'number'}]
    #             columns += [{'name': '%s Net' % self.format_date(options), 'class': 'number'}]
    #         else:
    #             columns += [{'name': self.format_date(options), 'class': 'number'}]
    #
    #         # Modified part of native code
    #         if options.get('comparison') and options['comparison'].get('periods'):
    #             for period in options['comparison']['periods']:
    #                 col_name = period.get('string')
    #                 col_name += " Net" if self.type_financial_report_mg == 'balance_sheet' else ""
    #                 columns += [{'name': col_name, 'class': 'number'}]
    #             balance_sheet = self.type_financial_report_mg == 'balance_sheet' and not self.n_gross_mg and not self.n_amort_prov_mg and self.last_year_mg
    #             if self.type_financial_report_mg != 'balance_sheet' and options['comparison'].get('number_period') == 1 and not options.get('groups') or balance_sheet:
    #                 columns += [{'name': '%', 'class': 'number'}]
    #
    #         if options.get('groups', {}).get('ids'):
    #             columns_for_groups = []
    #             for column in columns[1:]:
    #                 for ids in options['groups'].get('ids'):
    #                     group_column_name = ''
    #                     for index, id in enumerate(ids):
    #                         column_name = self._get_column_name(id, options['groups']['fields'][index])
    #                         group_column_name += ' ' + column_name
    #                     columns_for_groups.append({'name': column.get('name') + group_column_name, 'class': 'number'})
    #             columns = columns[:1] + columns_for_groups
    #
    #         return columns

    # HRN ADD
    def _get_filter_info(self, options):
        if not options.get('ir_filters'):
            return False, False

        selected_ir_filter = [f for f in options['ir_filters'] if f.get('selected')]
        if selected_ir_filter:
            selected_ir_filter = selected_ir_filter[0]
        else:
            return False, False

        return selected_ir_filter['domain'], selected_ir_filter['groupby']

    #     def _get_lines(self, options, line_id=None):
    #         line_obj = self.line_ids
    #         if line_id:
    #             line_obj = self.env['account.financial.html.report.line'].search([('id', '=', line_id)])
    #         if options.get('comparison') and options.get('comparison').get('periods'):
    #             line_obj = line_obj.with_context(periods=options['comparison']['periods'])
    #         if options.get('ir_filters'):
    #             line_obj = line_obj.with_context(periods=options.get('ir_filters'))
    #
    #         currency_table = self.env['res.currency']._get_query_currency_table(options)
    #         domain, group_by = self._get_filter_info(options)
    #         pprint(options)
    #
    #         if group_by:
    #             options['groups'] = {}
    #             options['groups']['fields'] = group_by
    #             options['groups']['ids'] = self._get_groups(domain, group_by)
    #
    #         amount_of_periods = len((options.get('comparison') or {}).get('periods') or []) + 1
    #
    #         # Modified part of native code
    #         if self.type_financial_report_mg == 'balance_sheet':
    #             amount_of_periods *= 2
    #
    #         amount_of_group_ids = len(options.get('groups', {}).get('ids') or []) or 1
    #         linesDicts = [[{} for _ in range(0, amount_of_group_ids)] for _ in range(0, amount_of_periods)]
    #
    #         res = line_obj.with_context(
    #             filter_domain=domain,
    #         )._get_lines(self, currency_table, options, linesDicts)
    #
    #         # Modified part of native code
    #         if self.type_financial_report_mg == 'balance_sheet':
    #             # Get list of columns to remove
    #             columns_to_remove = [col for col in range(len(res[0]['columns'])) if col % 3 != 2]
    #             if self.type_financial_report_mg == 'balance_sheet' and not self.n_gross_mg and not self.n_amort_prov_mg and self.last_year_mg:
    #                 columns_to_remove.pop(-1)
    #             if self.n_amort_prov_mg:
    #                 columns_to_remove.pop(1)
    #             if self.n_gross_mg:
    #                 columns_to_remove.pop(0)
    #             # Remove columns
    #             columns_to_remove = sorted(columns_to_remove, reverse=True)
    #             [res[i]['columns'].pop(col) for i in range(len(res)) for col in columns_to_remove]
    #         # Insert one blank column in the beginning of result if note is checked
    #         if self.note_mg:
    #             [res[i]['columns'].insert(0, {'name': ""}) for i in range(len(res))]
    #
    #         return res

    def get_report_informations(self, options):
        if self.type_financial_report_mg == 'balance_sheet' and self.last_year_mg and not self.filter_comparison:
            self.filter_comparison = {'date_from': '', 'date_to': '', 'filter': 'no_comparison', 'number_period': 1}

        return super(AccountFinancialReportInherit, self).get_report_informations(options)

    @api.model
    def _format_cell_value(self, financial_line, amount, currency=False, blank_if_zero=False):
        # don't print -0.0 in reports
        # instead put negative numbers between brackets
        if (self.type_financial_report_mg == 'cr_n' or self.type_financial_report_mg == 'cr_f') and financial_line.figure_type == 'float' and amount < 0.0:
            return "({})".format(super().format_value(abs(amount),
                                                        currency=currency,
                                                        blank_if_zero=blank_if_zero))
        return super(AccountFinancialReportInherit, self)._format_cell_value(financial_line, amount,
                                                                             currency=currency,
                                                                             blank_if_zero=blank_if_zero)

    @api.model
    def _get_financial_line_report_line(self, options, financial_line, solver, groupby_keys):
        ''' Create the report line for an account.financial.html.report.line record.
        :param options:             The report options.
        :param financial_line:      An account.financial.html.report.line record.
        :param solver_results:      An instance of the FormulaSolver class.
        :param groupby_keys:        The sorted encountered keys in the solver.
        :return:                    The dictionary corresponding to a line to be rendered.
        '''
        results = solver.get_results(financial_line)['formula']

        is_leaf = solver.is_leaf(financial_line)
        has_lines = solver.has_move_lines(financial_line)
        has_something_to_unfold = is_leaf and has_lines and bool(financial_line.groupby)

        # Compute if the line is unfoldable or not.
        is_unfoldable = has_something_to_unfold and financial_line.show_domain == 'foldable'

        # Compute if the line is unfolded or not.
        # /!\ Take care about the case when the line is unfolded but not unfoldable with show_domain == 'always'.
        if not has_something_to_unfold or financial_line.show_domain == 'never':
            is_unfolded = False
        elif financial_line.show_domain == 'always':
            is_unfolded = True
        elif financial_line.show_domain == 'foldable' and financial_line.id in options['unfolded_lines']:
            is_unfolded = True
        else:
            is_unfolded = False

        # Standard columns.
        columns = []
        for key in groupby_keys:
            amount = results.get(key, 0.0)
            columns.append(
                {'name': self._format_cell_value(financial_line, amount), 'no_format': amount, 'class': 'number'})

        # Growth comparison column.
        if self._display_growth_comparison(options):
            columns.append(self._compute_growth_comparison_column(options,
                                                                  columns[0]['no_format'],
                                                                  columns[1]['no_format'],
                                                                  green_on_positive=financial_line.green_on_positive
                                                                  ))

        # Debug info columns.
        if self._display_debug_info(options):
            columns.append(self._compute_debug_info_column(options, solver, financial_line))

        financial_report_line = {
            'id': financial_line.id,
            'name': financial_line.name,
            'level': financial_line.level,
            'class': 'o_account_reports_totals_below_sections' if self.env.company.totals_below_sections else '',
            'columns': columns,
            'unfoldable': is_unfoldable,
            'unfolded': is_unfolded,
            'page_break': financial_line.print_on_new_page,
            'action_id': financial_line.action_id.id,
            'is_hidden': financial_line.is_hidden,
        }

        # Custom caret_options for tax report.
        if self.tax_report and financial_line.domain and not financial_line.action_id:
            financial_report_line['caret_options'] = 'tax.report.line'

        return financial_report_line


class AccountFinancialReportLineInherit(models.Model):
    _inherit = 'account.financial.html.report.line'

    is_hidden = fields.Boolean("Hide line in report", default=False)

    #     def _get_lines(self, financial_report, currency_table, options, linesDicts):
    #         # If not MG financial report
    #         if not financial_report.type_financial_report_mg:
    #             return super(AccountFinancialReportLineInherit, self)._get_lines(financial_report, currency_table, options, linesDicts)
    #
    #         final_result_table = []
    #         comparison_table = [options.get('date')]
    #         comparison_table += options.get('comparison') and options['comparison'].get('periods', []) or []
    #
    #         # Modified part of native code
    #         if financial_report.type_financial_report_mg == 'balance_sheet':
    #             comparison_table_temp = []
    #             for period in comparison_table:
    #                 comparison_table_temp.append(copy.copy(period))
    #                 comparison_table_temp.append(copy.copy(period))
    #             comparison_table = comparison_table_temp
    #
    #         currency_precision = self.env.company.currency_id.rounding
    #
    #         # build comparison table
    #         for line in self:
    #             res = []
    #
    #             # Modified part of native code
    #             if financial_report.type_financial_report_mg == 'balance_sheet':
    #                 debit_credit = False
    #
    #                 formulas = line._get_formulas_expressions(line.formulas) if line.formulas else ["", ""]
    #                 domains = line._get_domains_expressions(line.domain) if line.domain else ["", ""]
    #
    #                 if len(formulas) == 1:
    #                     formulas.insert(1, "balance = 0") if "brut" in line.formulas else formulas.insert(0, "balance = 0")
    #                 if len(domains) == 1:
    #                     domains.insert(1, "[('id', '<', 0)]") if "brut" in line.domain else domains.insert(0, "[('id', '<', 0)]")
    #
    #                 for i in range(len(comparison_table)):
    #                     comparison_table[i]['formula'] = formulas[i % 2]
    #                     comparison_table[i]['domain'] = domains[i % 2]
    #             else:
    #                 debit_credit = len(comparison_table) == 1
    #
    #             domain_ids = {'line'}
    #             k = 0
    #
    #             for period in comparison_table:
    #                 date_from = period.get('date_from', False)
    #                 date_to = period.get('date_to', False) or period.get('date', False)
    #                 date_from, date_to, strict_range = line.with_context(date_from=date_from, date_to=date_to)._compute_date_range()
    #
    #                 # Modified part of native code
    #                 if financial_report.type_financial_report_mg == 'balance_sheet':
    #                     r = line.with_context(date_from=date_from,
    #                                           date_to=date_to,
    #                                           strict_range=strict_range)._eval_formula(financial_report,
    #                                                                                    debit_credit,
    #                                                                                    currency_table,
    #                                                                                    linesDicts[k],
    #                                                                                    groups=options.get('groups'),
    #                                                                                    formula_o=period['formula'],
    #                                                                                    domain_o=period['domain'])
    #                 else:
    #                     r = line.with_context(date_from=date_from,
    #                                           date_to=date_to,
    #                                           strict_range=strict_range)._eval_formula(financial_report,
    #                                                                                    debit_credit,
    #                                                                                    currency_table,
    #                                                                                    linesDicts[k],
    #                                                                                    groups=options.get('groups'))
    #                 debit_credit = False
    #                 res.extend(r)
    #                 for column in r:
    #                     domain_ids.update(column)
    #                 k += 1
    #
    #             # Modified part of native code
    #             if financial_report.type_financial_report_mg == 'balance_sheet':
    #                 res = self._compute_net_value(copy.deepcopy(res))
    #
    #             res = line._put_columns_together(res, domain_ids)
    #
    #             if line.hide_if_zero and all([float_is_zero(k, precision_rounding=currency_precision) for k in res['line']]):
    #                 continue
    #
    #             #add by Lanja: to hide hidden line on report
    #             if line.is_hidden:
    #                 continue
    #
    #             # Post-processing ; creating line dictionnary, building comparison, computing total for extended, formatting
    #             vals = {
    #                 'id': line.id,
    #                 'name': line.name,
    #                 'level': line.level,
    #                 'class': 'o_account_reports_totals_below_sections' if self.env.company.totals_below_sections else '',
    #                 'columns': [{'name': l} for l in res['line']],
    #                 'unfoldable': len(domain_ids) > 1 and line.show_domain != 'always',
    #                 'unfolded': line.id in options.get('unfolded_lines', []) or line.show_domain == 'always',
    #                 'page_break': line.print_on_new_page,
    #             }
    #
    #             if financial_report.tax_report and line.domain and not line.action_id:
    #                 vals['caret_options'] = 'tax.report.line'
    #
    #             if line.action_id:
    #                 vals['action_id'] = line.action_id.id
    #             domain_ids.remove('line')
    #             lines = [vals]
    #             groupby = line.groupby or 'aml'
    #             if line.id in options.get('unfolded_lines', []) or line.show_domain == 'always':
    #                 if line.groupby:
    #                     domain_ids = sorted(list(domain_ids), key=lambda k: line._get_gb_name(k))
    #                 for domain_id in domain_ids:
    #                     name = line._get_gb_name(domain_id)
    #                     if not self.env.context.get('print_mode') or not self.env.context.get('no_format'):
    #                         name = name[:40] + '...' if name and len(name) >= 45 else name
    #                     vals = {
    #                         'id': domain_id,
    #                         'name': name,
    #                         'level': line.level,
    #                         'parent_id': line.id,
    #                         'columns': [{'name': l} for l in res[domain_id]],
    #                         'caret_options': groupby == 'account_id' and 'account.account' or groupby,
    #                         'financial_group_line_id': line.id,
    #                     }
    #                     if line.financial_report_id.name == 'Aged Receivable':
    #                         vals['trust'] = self.env['res.partner'].browse([domain_id]).trust
    #                     lines.append(vals)
    #                 if domain_ids and self.env.company.totals_below_sections:
    #                     lines.append({
    #                         'id': 'total_' + str(line.id),
    #                         'name': _('Total') + ' ' + line.name,
    #                         'level': line.level,
    #                         'class': 'o_account_reports_domain_total',
    #                         'parent_id': line.id,
    #                         'columns': copy.deepcopy(lines[0]['columns']),
    #                     })
    #
    #             for vals in lines:
    #                 # Modified part of native code
    #                 balance_sheet = financial_report.type_financial_report_mg == 'balance_sheet' and not financial_report.n_gross_mg and not financial_report.n_amort_prov_mg and financial_report.last_year_mg
    #                 if balance_sheet and len(comparison_table) == 4 and not options.get('groups'):
    #                     vals['columns'].append(line._build_cmp(vals['columns'][2]['name'], vals['columns'][5]['name']))
    #                     for i in [2, 5]:
    #                         vals['columns'][i] = line._format(vals['columns'][i])
    #                 elif financial_report.type_financial_report_mg != 'balance_sheet' and len(comparison_table) == 2 and not options.get('groups'):
    #                     # vals['columns'].append(line._build_cmp(vals['columns'][0]['name'], vals['columns'][1]['name']))
    #                     for i in [0, 1]:
    #                         vals['columns'][i] = line._format(vals['columns'][i])
    #
    #                 else:
    #                     vals['columns'] = [line._format(v) for v in vals['columns']]
    #                 if not line.formulas:
    #                     vals['columns'] = [{'name': ''} for k in vals['columns']]
    #
    #             if len(lines) == 1:
    #                 new_lines = line.children_ids._get_lines(financial_report, currency_table, options, linesDicts)
    #                 if new_lines and line.formulas:
    #                     if self.env.company.totals_below_sections:
    #                         divided_lines = self._divide_line(lines[0])
    #                         result = [divided_lines[0]] + new_lines + [divided_lines[-1]]
    #                     else:
    #                         # Modified part of native code
    #                         if financial_report.type_financial_report_mg == 'income_statement':
    #                             # Inverting the order of the lines relative to the native
    #                             result = new_lines + [lines[0]]
    #                         else:
    #                             result = [lines[0]] + new_lines
    #                 else:
    #                     if not new_lines and not lines[0]['unfoldable'] and line.hide_if_empty:
    #                         lines = []
    #                     result = lines + new_lines
    #             else:
    #                 result = lines
    #             final_result_table += result
    #
    #         return final_result_table
    def _get_formulas_expressions(self, global_expression):
        if global_expression.split(";")[0].split("=")[0].strip() not in ['brut', 'amort']:
            if len(global_expression.split(";")) == 1:
                return [global_expression, global_expression]
            elif len(global_expression.split(";")) == 2 and not global_expression.split(";")[1].strip():
                return [global_expression.split(";")[0].strip(), global_expression.split(";")[0].strip()]

        category_dict = {
            'brut': 0,
            'amort': 1,
        }
        expressions = []
        try:
            for expression in global_expression.split(";"):
                if 'sum' in expression.split("=", 1)[1].strip().split(".")[0]:
                    expressions.insert(category_dict[expression.split("=")[0].strip()],
                                       expression.strip().replace(expression.split("=", 1)[0].strip(), "balance"))
                else:
                    # If formula contain a CODE
                    expressions.insert(category_dict[expression.split("=")[0].strip()], expression.strip())
        except KeyError:
            keys = [key for key in category_dict.keys()]
            exceptions.ValidationError(_("Please, check your formulas. Make sure that your keys are in: %s") % keys)

        return expressions

    def _get_domains_expressions(self, global_expression):
        category_dict = {
            'brut': 0,
            'amort': 1,
        }
        expressions = []
        try:
            for expression in global_expression.split(";"):
                expressions.insert(category_dict[expression.split("=")[0].strip()], expression.split("=", 1)[1].strip())
        except KeyError:
            keys = [key for key in category_dict.keys()]
            exceptions.ValidationError(_("Please, check your domains. Make sure that your keys are in: %s") % keys)

        return expressions

    @api.model
    def _eval_formula(self, financial_report, debit_credit, currency_table, linesdict_per_group, groups=False,
                      formula_o="", domain_o=""):
        if financial_report.type_financial_report_mg != 'balance_sheet':
            return super(AccountFinancialReportLineInherit, self)._eval_formula(financial_report, debit_credit,
                                                                                currency_table, linesdict_per_group,
                                                                                groups)
        groups = groups or {'fields': [], 'ids': [()]}
        debit_credit = debit_credit and financial_report.debit_credit
        formulas = self._split_formulas(formula_o)
        currency = self.env.company.currency_id

        line_res_per_group = []

        if not groups['ids']:
            return [{'line': {'balance': 0.0}}]

        # this computes the results of the line itself
        for group_index, group in enumerate(groups['ids']):
            self_for_group = self.with_context(group_domain=self._get_group_domain(group, groups))
            linesdict = linesdict_per_group[group_index]
            line = False

            if self.code and self.code in linesdict:
                line = linesdict[self.code]
            elif formulas and formulas[next(iter(formulas))].strip() == 'count_rows' and self.groupby:
                # We don't need to change the dictionary key
                line_res_per_group.append({'line': {'balance': self_for_group._get_rows_count()}})
            elif formulas and formulas[next(iter(formulas))].strip() == 'from_context':
                # We don't need to change the dictionary key
                line_res_per_group.append({'line': {'balance': self_for_group._get_value_from_context()}})
            else:
                line = FormulaLine(self_for_group, currency_table, financial_report, linesdict=linesdict,
                                   formula_o=formula_o, domain_o=domain_o)

            if line:
                res = {}
                res['balance'] = currency.round(line.balance)
                if debit_credit:
                    res['debit'] = currency.round(line.debit)
                line_res_per_group.append(res)

        # don't need any groupby lines for count_rows and from_context formulas
        if all('line' in val for val in line_res_per_group):
            return line_res_per_group

        columns = []
        # this computes children lines in case the groupby field is set
        if self.domain and self.groupby and self.show_domain != 'never':
            if self.groupby not in self.env['account.move.line']:
                raise ValueError(_('Groupby should be a field from account.move.line'))

            groupby = [self.groupby or 'id']
            if groups:
                groupby = groups['fields'] + groupby
            groupby = ', '.join(['"account_move_line".%s' % field for field in groupby])

            aml_obj = self.env['account.move.line']
            tables, where_clause, where_params = aml_obj._query_get(domain=self._get_aml_domain(domain_o))
            if financial_report.tax_report:
                where_clause += ''' AND "account_move_line".tax_exigible = 't' '''

            select, params = self._query_get_select_sum(currency_table)
            sql = "SELECT " + groupby + ", " + select + " FROM " + tables + " WHERE " + where_clause + " GROUP BY " + groupby + " ORDER BY " + groupby

            params += where_params
            self.env.cr.execute(sql, params)
            results = self.env.cr.fetchall()
            for group_index, group in enumerate(groups['ids']):
                linesdict = linesdict_per_group[group_index]
                results_for_group = [result for result in results if group == result[:len(group)]]
                if results_for_group:
                    results_for_group = [r[len(group):] for r in results_for_group]
                    results_for_group = dict(
                        [(k[0], {'balance': k[1], 'amount_residual': k[2], 'debit': k[3], 'credit': k[4]}) for k in
                         results_for_group])
                    c = FormulaContext(self.env['account.financial.html.report.line'].with_context(
                        group_domain=self._get_group_domain(group, groups)),
                        linesdict, currency_table, financial_report, only_sum=True, formula_o=formula_o,
                        domain_o=domain_o)
                    if formulas:
                        for key in results_for_group:
                            c['sum'] = FormulaLine(results_for_group[key], currency_table, financial_report,
                                                   type='not_computed', formula_o=formula_o, domain_o=domain_o)
                            c['sum_if_pos'] = FormulaLine(
                                results_for_group[key]['balance'] >= 0.0 and results_for_group[key] or {'balance': 0.0},
                                currency_table, financial_report, type='not_computed', formula_o=formula_o,
                                domain_o=domain_o)
                            c['sum_if_neg'] = FormulaLine(
                                results_for_group[key]['balance'] <= 0.0 and results_for_group[key] or {'balance': 0.0},
                                currency_table, financial_report, type='not_computed', formula_o=formula_o,
                                domain_o=domain_o)
                            for col, formula in formulas.items():
                                if col in results_for_group[key]:
                                    results_for_group[key][col] = safe_eval(formula, c, nocopy=True)
                    to_del = []
                    for key in results_for_group:
                        if self.env.company.currency_id.is_zero(results_for_group[key]['balance']):
                            to_del.append(key)
                    for key in to_del:
                        del results_for_group[key]
                    results_for_group.update({'line': line_res_per_group[group_index]})
                    columns.append(results_for_group)
                else:
                    res_vals = {'balance': 0.0}
                    if debit_credit:
                        res_vals.update({'debit': 0.0, 'credit': 0.0})
                    columns.append({'line': res_vals})

        return columns or [{'line': res} for res in line_res_per_group]

    def _split_formulas(self, formula_o=""):
        temp = self
        while temp.parent_id:
            temp = temp.parent_id
        if temp.financial_report_id.type_financial_report_mg != 'balance_sheet':
            return super(AccountFinancialReportLineInherit, self)._split_formulas()

        result = {}
        if formula_o:
            for f in formula_o.split(';'):
                [column, formula] = f.split('=')
                column = column.strip()
                result.update({column: formula})
        return result

    def _get_balance(self, linesdict, currency_table, financial_report, field_names=None, formula_o="", domain_o=""):
        if financial_report.type_financial_report_mg != 'balance_sheet':
            return super(AccountFinancialReportLineInherit, self)._get_balance(linesdict, currency_table,
                                                                               financial_report, field_names)

        results = []

        if not field_names:
            field_names = ['debit', 'credit', 'balance']

        for rec in self:
            res = dict((fn, 0.0) for fn in field_names)
            c = FormulaContext(self.env['account.financial.html.report.line'],
                               linesdict, currency_table, financial_report, rec, formula_o=formula_o, domain_o=domain_o)
            if rec.formulas:
                # Get corresponding formula
                try:
                    current_formula = formula_o.split("=")[0].strip()
                    if current_formula == 'balance':
                        current_formula = formula_o
                    elif current_formula in rec.formulas:
                        for formula in rec.formulas.split(";"):
                            if current_formula in formula:
                                current_formula = formula.strip().replace(current_formula, 'balance')
                                break
                    else:
                        current_formula = "=;="
                except:
                    current_formula = "=;="

                for f in current_formula.split(';'):
                    [field, formula] = f.split('=')
                    field = field.strip()
                    if field in field_names:
                        try:
                            res[field] = safe_eval(formula, c, nocopy=True)
                        except ValueError as err:
                            if 'division by zero' in err.args[0]:
                                res[field] = 0
                            else:
                                raise err
            results.append(res)
        return results

    def _get_sum(self, currency_table, financial_report, field_names=None, formula_o="", domain_o=""):
        ''' Returns the sum of the amls in the domain '''

        if financial_report.type_financial_report_mg != 'balance_sheet':
            return super(AccountFinancialReportLineInherit, self)._get_sum(currency_table, financial_report,
                                                                           field_names)

        if not field_names:
            field_names = ['debit', 'credit', 'balance', 'amount_residual']
        res = dict((fn, 0.0) for fn in field_names)
        if self.domain:
            # Get corresponding domain
            try:
                current_domain = domain_o.split("=")[0].strip() if domain_o else formula_o.split("=")[0].strip()
                if current_domain == 'balance' and domain_o:
                    current_domain = domain_o
                elif current_domain in self.domain:
                    for domain in self.domain.split(";"):
                        if current_domain in domain:
                            current_domain = domain.split("=", 1)[1].strip()
                            break
                else:
                    current_domain = "=;="
            except:
                current_domain = "=;="

            date_from, date_to, strict_range = \
                self._compute_date_range()
            res = self.with_context(strict_range=strict_range, date_from=date_from, date_to=date_to,
                                    active_test=False)._compute_line(currency_table, financial_report,
                                                                     group_by=self.groupby,
                                                                     domain=self._get_aml_domain(current_domain))
        return res

    def _get_aml_domain(self, domain_o=""):
        temp = self
        while temp.parent_id:
            temp = temp.parent_id
        if temp.financial_report_id.type_financial_report_mg != 'balance_sheet':
            domain_o = self.domain

        if domain_o and 'similar to' in domain_o.split(",")[1]:
            field, operator, values = domain_o[2:-2].replace("'\\", "").replace(" ", "").replace("'", "").split(",", 2)
            operator = '=like'
            values = values[1:-1].split(",")
            domain = "["
            for i in range(len(values) - 1):
                domain += "'|',"
            for value in values:
                domain += "('%s', '%s', '%s')," % (field, operator, value)
            domain = domain[:-1] + "]"
            return (safe_eval(domain) or []) + (self._context.get('filter_domain') or []) + (
                    self._context.get('group_domain') or [])
        elif domain_o:
            return (safe_eval(domain_o) or []) + (self._context.get('filter_domain') or []) + (
                    self._context.get('group_domain') or [])
        else:
            return [] + (self._context.get('filter_domain') or []) + (self._context.get('group_domain') or [])

    def _compute_line(self, currency_table, financial_report, group_by=None, domain=[]):
        """ Computes the sum that appeas on report lines when they aren't unfolded. It is using _query_get() function
            of account.move.line which is based on the context, and an additional domain (the field domain on the report
            line) to build the query that will be used.

            @param currency_table: dictionary containing the foreign currencies (key) and their factor (value)
                compared to the current user's company currency
            @param financial_report: browse_record of the financial report we are willing to compute the lines for
            @param group_by: used in case of conditionnal sums on the report line
            @param domain: domain on the report line to consider in the query_get() call

            @returns : a dictionnary that has for each aml in the domain a dictionnary of the values of the fields
        """

        if financial_report.type_financial_report_mg != 'balance_sheet':
            return super(AccountFinancialReportLineInherit, self)._compute_line(currency_table, financial_report,
                                                                                group_by, domain)

        domain = domain and ast.literal_eval(ustr(domain))
        for index, condition in enumerate(domain):
            if condition[0].startswith('tax_ids.'):
                new_condition = (condition[0].partition('.')[2], condition[1], condition[2])
                taxes = self.env['account.tax'].with_context(active_test=False).search([new_condition])
                domain[index] = ('tax_ids', 'in', taxes.ids)
        aml_obj = self.env['account.move.line']
        tables, where_clause, where_params = aml_obj._query_get(domain=self._get_aml_domain(ustr(domain)))
        if financial_report.tax_report:
            where_clause += ''' AND "account_move_line".tax_exigible = 't' '''

        line = self
        financial_report = False

        while not financial_report:
            financial_report = line.financial_report_id
            if not line.parent_id:
                break
            line = line.parent_id

        select, select_params = self._query_get_select_sum(currency_table)
        where_params = select_params + where_params

        if (self.env.context.get('sum_if_pos') or self.env.context.get('sum_if_neg')) and group_by:
            sql = "SELECT account_move_line." + group_by + " as " + group_by + "," + select + " FROM " + tables + " WHERE " + where_clause + " GROUP BY account_move_line." + group_by
            self.env.cr.execute(sql, where_params)
            res = {'balance': 0, 'debit': 0, 'credit': 0, 'amount_residual': 0}
            for row in self.env.cr.dictfetchall():
                if (row['balance'] > 0 and self.env.context.get('sum_if_pos')) or (
                        row['balance'] < 0 and self.env.context.get('sum_if_neg')):
                    for field in ['debit', 'credit', 'balance', 'amount_residual']:
                        res[field] += row[field]
            res['currency_id'] = self.env.company.currency_id.id
            return res

        sql = "SELECT " + select + " FROM " + tables + " WHERE " + where_clause
        self.env.cr.execute(sql, where_params)
        results = self.env.cr.dictfetchall()[0]
        results['currency_id'] = self.env.company.currency_id.id
        return results

    def _compute_net_value(self, res):
        i = 0
        while i < len(res):
            brut = copy.deepcopy(res[i])
            brut.pop('line')
            res.insert(i + 2, copy.deepcopy(brut))

            amort = copy.deepcopy(res[i + 1])
            amort.pop('line')

            keys_1 = set(brut.keys()) | set(amort.keys())
            if brut:
                keys_2 = list(brut[next(iter(brut))].keys())
            elif amort:
                keys_2 = list(amort[next(iter(amort))].keys())
            else :
                keys_2 = False
            if keys_2:
                for key_1 in keys_1:
                    res[i + 2].update({key_1: {}})
                    for key_2 in keys_2:
                        res[i + 2][key_1].update(
                            {key_2: brut.get(key_1, {}).get(key_2, 0.0) - amort.get(key_1, {}).get(key_2, 0.0)})
                res[i + 2]['line'] = {'balance': sum(list(map(itemgetter('balance'), res[i + 2].values())))}
            else:
                res[i + 2]['line'] = {'balance': res[i]['line']['balance'] - res[i + 1]['line']['balance']}

            i += 3

        return res

    def _format(self, value):
        if self.env.context.get('no_format'):
            return value
        value['no_format_name'] = value['name']
        if self.figure_type == 'float':
            currency_id = self.env.company.currency_id
            if currency_id.is_zero(value['name']):
                # don't print -0.0 in reports
                value['name'] = abs(value['name'])
                value['class'] = 'number text-muted'

            # Modified part of native code
            temp = self
            while temp.parent_id:
                temp = temp.parent_id
            if temp.financial_report_id.monetary_unit_mg:
                value['name'] = formatLang(self.env, value['name'], currency_obj=currency_id)
            else:
                value['name'] = formatLang(self.env, value['name'])

            return value
        if self.figure_type == 'percents':
            value['name'] = str(round(value['name'] * 100, 1)) + '%'
            return value
        value['name'] = round(value['name'], 1)
        return value

    # HRN ADDD
    def _compute_date_range(self):
        '''Compute the current report line date range according to the dates passed through the context
        and its specified special_date_changer.

        :return: The date_from, date_to, strict_range values to consider for the report line.
        '''
        date_from = self._context.get('date_from', False)
        date_to = self._context.get('date_to', False)

        strict_range = self.special_date_changer == 'strict_range'
        if self.special_date_changer == 'from_beginning':
            date_from = False
        if self.special_date_changer == 'to_beginning_of_period' and date_from:
            date_tmp = fields.Date.from_string(self._context['date_from']) - relativedelta(days=1)
            date_to = date_tmp.strftime('%Y-%m-%d')
            date_from = False
        if self.special_date_changer == 'from_fiscalyear' and date_to:
            date_tmp = fields.Date.from_string(date_to)
            date_tmp = self.env.company.compute_fiscalyear_dates(date_tmp)['date_from']
            date_from = date_tmp.strftime('%Y-%m-%d')
            strict_range = True
        return date_from, date_to, strict_range


class FormulaLine(object):
    def __init__(self, obj, currency_table, financial_report, type='balance', linesdict=None, formula_o="",
                 domain_o=""):
        if linesdict is None:
            linesdict = {}
        fields = dict((fn, 0.0) for fn in ['debit', 'credit', 'balance'])
        if type == 'balance':
            fields = \
                obj._get_balance(linesdict, currency_table, financial_report, formula_o=formula_o, domain_o=domain_o)[0]
            linesdict[obj.code] = self
        elif type in ['sum', 'sum_if_pos', 'sum_if_neg']:
            if type == 'sum_if_neg':
                obj = obj.with_context(sum_if_neg=True)
            if type == 'sum_if_pos':
                obj = obj.with_context(sum_if_pos=True)
            if obj._name == 'account.financial.html.report.line':
                fields = obj._get_sum(currency_table, financial_report, formula_o=formula_o, domain_o=domain_o)
                self.amount_residual = fields['amount_residual']
            elif obj._name == 'account.move.line':
                self.amount_residual = 0.0
                field_names = ['debit', 'credit', 'balance', 'amount_residual']
                res = obj.env['account.financial.html.report.line']._compute_line(currency_table, financial_report)
                for field in field_names:
                    fields[field] = res[field]
                self.amount_residual = fields['amount_residual']
        elif type == 'not_computed':
            for field in fields:
                fields[field] = obj.get(field, 0)
            self.amount_residual = obj.get('amount_residual', 0)
        elif type == 'null':
            self.amount_residual = 0.0
        self.balance = fields['balance']
        self.credit = fields['credit']
        self.debit = fields['debit']


class FormulaContext(dict):
    def __init__(self, reportlineobj, linesdict, currency_table, financial_report, curobj=None, only_sum=False,
                 formula_o="", domain_o="", *data):
        self.reportlineobj = reportlineobj
        self.curobj = curobj
        self.linesdict = linesdict
        self.currency_table = currency_table
        self.only_sum = only_sum
        self.financial_report = financial_report
        self.formula_o = formula_o
        self.domain_o = domain_o
        return super(FormulaContext, self).__init__(data)

    def __getitem__(self, item):
        formula_items = ['sum', 'sum_if_pos', 'sum_if_neg']
        if item in set(__builtins__.keys()) - set(formula_items):
            return super(FormulaContext, self).__getitem__(item)

        if self.only_sum and item not in formula_items:
            return FormulaLine(self.curobj, self.currency_table, self.financial_report, type='null',
                               formula_o=self.formula_o, domain_o=self.domain_o)
        if self.get(item):
            return super(FormulaContext, self).__getitem__(item)
        if self.linesdict.get(item):
            return self.linesdict[item]
        if item == 'sum':
            res = FormulaLine(self.curobj, self.currency_table, self.financial_report, type='sum',
                              formula_o=self.formula_o, domain_o=self.domain_o)
            self['sum'] = res
            return res
        if item == 'sum_if_pos':
            res = FormulaLine(self.curobj, self.currency_table, self.financial_report, type='sum_if_pos',
                              formula_o=self.formula_o, domain_o=self.domain_o)
            self['sum_if_pos'] = res
            return res
        if item == 'sum_if_neg':
            res = FormulaLine(self.curobj, self.currency_table, self.financial_report, type='sum_if_neg',
                              formula_o=self.formula_o, domain_o=self.domain_o)
            self['sum_if_neg'] = res
            return res
        if item == 'NDays':
            d1 = fields.Date.from_string(self.curobj.env.context['date_from'])
            d2 = fields.Date.from_string(self.curobj.env.context['date_to'])
            res = (d2 - d1).days
            self['NDays'] = res
            return res
        if item == 'count_rows':
            return self.curobj._get_rows_count()
        if item == 'from_context':
            return self.curobj._get_value_from_context()
        line_id = self.reportlineobj.search([('code', '=', item)], limit=1)
        if line_id:
            date_from, date_to, strict_range = line_id._compute_date_range()
            res = FormulaLine(line_id.with_context(strict_range=strict_range, date_from=date_from, date_to=date_to),
                              self.currency_table, self.financial_report, linesdict=self.linesdict,
                              formula_o=self.formula_o, domain_o=self.domain_o)
            self.linesdict[item] = res
            return res
        return super(FormulaContext, self).__getitem__(item)
