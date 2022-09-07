# -*- coding: utf-8 -*-
import calendar

import xlsxwriter

from datetime import date
from odoo import models, fields, _

SELECT_YEAR = [(str(year), year) for year in range(
    fields.Date().today().year - 10, fields.Date().today().year + 10)]

SELECT_MONTH = [
    ('1', _('January')),
    ('2', _('February')),
    ('3', _('March')),
    ('4', _('April')),
    ('5', _('May')),
    ('6', _('June')),
    ('7', _('July')),
    ('8', _('August')),
    ('9', _('September')),
    ('10', _('October')),
    ('11', _('November')),
    ('12', _('December'))
]

QUARTER = [
    ('00', _('First Quarter (Jan. Feb. March.)')),
    ('01', _('Second Quarter (April. May. June.)')),
    ('02', _('Third Quarter (July. Aug. Sept.)')),
    ('03', _('Forth Quarter (Oct. Nov. Dec.)')),
]

MONTHS = [(1, 2, 3), (4, 5, 6), (7, 8, 9), (10, 11, 12)]


class PayslipStateExport(models.TransientModel):
    _name = 'payslip.state.export'
    _description = 'Payslip State Export'

    name = fields.Selection([('cnaps', 'CNAPS'), ('ostie', 'OSTIE'),
                            ('irsa', 'IRSA'), ('annex_irsa', _('Annex IRSA'))])
    year = fields.Selection(SELECT_YEAR, string='Year', default=str(
        fields.Date().today().year), required=True)
    period = fields.Selection(SELECT_MONTH, string='Period')
    quarter = fields.Selection(QUARTER, string='Quarter')
    company_id = fields.Many2one('res.company', string='Company')

    def get_xls_file(self):
        """
        Method to export payslip state such as cnaps, ostie, iri, irsa
        :return: xlsx file
        """
        if self.name == 'cnaps':
            return {
                'type': 'ir.actions.act_url',
                'url': '/web/binary/download_cnaps_xlsx_file?id=%s' % (self[0].id),
            }
        elif self.name == 'ostie':
            return {
                'type': 'ir.actions.act_url',
                'url': '/web/binary/download_ostie_xlsx_file?id=%s' % (self[0].id),
            }
        elif self.name == 'irsa':
            return {
                'type': 'ir.actions.act_url',
                'url': '/web/binary/download_irsa_xlsx_file?id=%s' % (self[0].id),
            }
        elif self.name == 'annex_irsa':
            return {
                'type': 'ir.actions.act_url',
                'url': '/web/binary/download_annex_irsa_xlsx_file?id=%s' % (self[0].id),
            }

    def get_default_format(self, workbook: xlsxwriter.Workbook):
        """
        Set default cell format for the workbook
        :type workbook: xlsxwriter.Workbook
        :param workbook:
        :return: dict
        """
        # set double bottom border
        bold_f9_center_double_bottom_border = workbook.add_format(
            {'bold': True, 'font_size': 9, 'align': 'center'})
        bold_f9_center_double_bottom_border.set_bottom(6)
        # set double border
        numeric_f9_double_border = workbook.add_format({
            'num_format': '_- #,##0.00 _A_r_-;- #,##0.00 A_r_-;_-* "-"?? A_r_-;_-@_-',
            'font_size': 9,
            'border': True
        })
        numeric_f9_double_border.set_border(6)
        # set arial font_name
        f9_center_border_arial = workbook.add_format({
            'font_size': 9,
            'font_name': 'Arial',
            'align': 'center',
            'border': True,
            'text_wrap': 1
        })
        f9_center_border_arial.set_align('vcenter')
        # f9_center_border_arial.set_text_wrap()

        return {
            'center': workbook.add_format({'align': 'center'}),
            'f9': workbook.add_format({'font_size': 9}),
            'f10_arial': workbook.add_format({'font_size': 10, 'font_name': 'Arial'}),
            'f12_bold': workbook.add_format({'font_size': 12, 'bold': True}),
            'f12_bold_center': workbook.add_format({'font_size': 12, 'bold': True, 'align': 'center'}),
            'f12_bold_red': workbook.add_format({'font_size': 12, 'bold': True, 'color': 'red'}),
            'f9_url': workbook.add_format({'font_size': 9, 'font_color': 'blue'}),
            'f9_url_center_border': workbook.add_format({
                'font_size': 9,
                'font_color': 'blue',
                'align': 'center',
                'border': True
            }),
            'f9_right': workbook.add_format({'font_size': 9, 'align': 'right'}),
            'f9_right_border': workbook.add_format({'font_size': 9, 'align': 'right', 'border': True}),
            'f9_center': workbook.add_format({'font_size': 9, 'align': 'center'}),
            'f9_center_border_arial': f9_center_border_arial,
            'f9_italic': workbook.add_format({'font_size': 9, 'italic': True}),
            'f9_border': workbook.add_format({'font_size': 9, 'border': True}),
            'f10_border_arial': workbook.add_format({'font_size': 10, 'font_name': 'Arial', 'border': True}),
            'f10_arial_bottom': workbook.add_format({'font_size': 10, 'font_name': 'Arial', 'bottom': True}),
            'f10_arial_right': workbook.add_format({'font_size': 10, 'font_name': 'Arial', 'right': True}),
            'f9_border_bgyellow': workbook.add_format({'font_size': 9, 'border': True, 'bg_color': 'yellow'}),
            'f9_border_center': workbook.add_format({'font_size': 9, 'border': True, 'align': 'center'}),
            'f10_border_center_arial': workbook.add_format(
                {'font_size': 10, 'font_name': 'Arial', 'border': True, 'align': 'center'}),
            'f11_center_border': workbook.add_format({'font_size': 11, 'align': 'center', 'border': True}),
            'f9_border_date': workbook.add_format({'font_size': 9, 'border': True, 'num_format': 'DD/MM/YY;@'}),
            'f9_border_center_date': workbook.add_format({
                'font_size': 9,
                'border': True,
                'num_format': 'DD/MM/YY;@',
                'align': 'center'
            }),
            'bold_f8': workbook.add_format({
                'bold': True,
                'font_size': 8,
            }),
            'f8_border_date': workbook.add_format({
                'font_size': 8,
                'border': True,
                'num_format': 'DD/MM/YY;@',
            }),
            'f8_border': workbook.add_format({
                'font_size': 8,
                'border': True,
            }),
            'f8_border_center': workbook.add_format({
                'font_size': 8,
                'border': True,
                'align': 'center'
            }),
            'numeric_f8_border': workbook.add_format({
                'num_format': '_-* #,##0.00 _A_r_-;-* #,##0.00 _A_r_-;_-* "-"?? _A_r_-;_-@_-',
                'font_size': 8,
                'border': True
            }),
            'bold_underline_f8': workbook.add_format({
                'bold': True,
                'underline': True,
                'font_size': 8
            }),
            'f9_bold_date': workbook.add_format({'font_size': 9, 'bold': True, 'num_format': 'DD/MM/YY;@'}),
            'f9_left_bggray': workbook.add_format({'font_size': 9, 'bg_color': '#D9D9D9', 'align': 'left'}),
            'f9_center_bggray_border': workbook.add_format(
                {'font_size': 9, 'bg_color': '#D9D9D9', 'align': 'center', 'left': True}),
            'f9_center_bggray': workbook.add_format(
                {'font_size': 9, 'bg_color': '#D9D9D9', 'align': 'center'}),
            'f9_left': workbook.add_format({'font_size': 9, 'align': 'left'}),
            'f9_left_arial': workbook.add_format({'font_size': 9, 'align': 'left', 'font_name': 'Arial'}),
            'bold': workbook.add_format({'bold': True}),
            'bold_center': workbook.add_format({'bold': True, 'align': 'center'}),
            'text_wrap': workbook.add_format({'text_wrap': 1}),
            'bold_f9': workbook.add_format({'bold': True, 'font_size': 9}),
            'bold_f9_center_bggray': workbook.add_format(
                {'bold': True, 'font_size': 9, 'bg_color': '#D9D9D9', 'align': 'center'}),
            'bold_f9_center_border': workbook.add_format({
                'bold': True,
                'font_size': 9,
                'align': 'center',
                'border': True
            }),
            'bold_f10_border_arial': workbook.add_format({
                'bold': True,
                'font_size': 10,
                'font_name': 'Arial',
                'border': True}),
            'bold_f10_arial_center_italic_border': workbook.add_format({
                'bold': True,
                'font_size': 10,
                'font_name': 'Arial',
                'align': 'center',
                'italic': True,
                'border': True
            }),
            'bold_f10_center_border_arial': workbook.add_format({
                'bold': True,
                'font_size': 10,
                'font_name': 'Arial',
                'align': 'center',
                'border': True
            }),
            'bold_f9_center_left': workbook.add_format({
                'bold': True,
                'font_size': 9,
                'align': 'center',
                'left': True
            }),
            'bold_f9_right': workbook.add_format({'bold': True, 'font_size': 9, 'align': 'right'}),
            'bold_f9_center_left_bggray': workbook.add_format({
                'bold': True,
                'font_size': 9,
                'align': 'center',
                'bg_color': '#D9D9D9',
                'left': True
            }),
            'bold_f9_center': workbook.add_format({
                'bold': True,
                'font_size': 9,
                'align': 'center'
            }),
            'bold_f9_center_top': workbook.add_format({
                'bold': True,
                'font_size': 9,
                'align': 'center',
                'top': True
            }),
            'border_left_bottom': workbook.add_format({
                'bottom': True,
                'left': True
            }),
            'border_bottom': workbook.add_format({'bottom': True}),
            'border_right_bottom': workbook.add_format({
                'bottom': True,
                'right': True
            }),
            'bold_f9_center_top_bottom': workbook.add_format({
                'bold': True,
                'font_size': 9,
                'align': 'center',
                'top': True,
                'bottom': True
            }),
            'bold_f9_center_double_bottom_border': bold_f9_center_double_bottom_border,
            'bold_f9_center_top_right': workbook.add_format({
                'bold': True,
                'font_size': 9,
                'align': 'center',
                'top': True,
                'right': True
            }),
            'bold_f9_center_right': workbook.add_format({
                'bold': True,
                'font_size': 9,
                'align': 'center',
                'right': True
            }),
            'bold_f9_right_top': workbook.add_format({
                'bold': True,
                'font_size': 9,
                'align': 'right',
                'top': True
            }),
            'bold_f9_right_top_bggray': workbook.add_format({
                'bold': True,
                'font_size': 9,
                'align': 'right',
                'bg_color': '#D9D9D9',
                'top': True
            }),
            'bold_f9_center_top_left': workbook.add_format({
                'bold': True,
                'font_size': 9,
                'align': 'center',
                'top': True,
                'left': True
            }),
            'bold_f9_center_top_left_bggray': workbook.add_format({
                'bold': True,
                'font_size': 9,
                'align': 'center',
                'bg_color': '#D9D9D9',
                'top': True,
                'left': True
            }),
            'bold_f9_left': workbook.add_format({'bold': True, 'font_size': 9, 'align': 'left'}),
            'bold_f9_left_bggray': workbook.add_format(
                {'bold': True, 'font_size': 9, 'bg_color': '#D9D9D9', 'align': 'left'}),
            'bold_f9_red': workbook.add_format({'bold': True, 'font_size': 9, 'color': 'red'}),
            'bold_f9_red_right': workbook.add_format({'bold': True, 'font_size': 9, 'color': 'red', 'align': 'right'}),
            'bold_underline': workbook.add_format({'bold': True, 'underline': True}),
            'bold_underline_f9': workbook.add_format({'bold': True, 'underline': True, 'font_size': 9}),
            'bold_underline_arial_f9': workbook.add_format(
                {'bold': True, 'underline': True, 'font_size': 9, 'font_name': 'Arial'}),
            'bold_underline_f11_arial': workbook.add_format(
                {'bold': True, 'underline': True, 'font_size': 11, 'font_name': 'Arial'}),
            'bold_underline_f10_arial': workbook.add_format(
                {'bold': True, 'underline': True, 'font_size': 10, 'font_name': 'Arial'}),
            'bold_justify_top_textwrap': workbook.add_format({
                'bold': True,
                'align': 'center',
                'valign': 'top',
                'text_wrap': 1,
            }),
            'numeric': workbook.add_format({
                'num_format': '_-* #,##0.00 _A_r_-;-* #,##0.00 _A_r_-;_-* "-"?? _A_r_-;_-@_-'
            }),
            'numeric_f9': workbook.add_format({
                'num_format': '_-* #,##0.00 _A_r_-;-* #,##0.00 _A_r_-;_-* "-"?? _A_r_-;_-@_-',
                'font_size': 9
            }),
            'numeric_center_arial_f9': workbook.add_format({
                'num_format': '_-* #,##0.00 _A_r_-;-* #,##0.00 _A_r_-;_-* "-"?? _A_r_-;_-@_-',
                'align': 'center',
                'font_name': 'Arial',
                'font_size': 9
            }),
            'numeric_center_bold_underline_arial_f9': workbook.add_format({
                'num_format': '_-* #,##0.00 _A_r_-;-* #,##0.00 _A_r_-;_-* "-"?? _A_r_-;_-@_-',
                'align': 'center',
                'underline': True,
                'bold': True,
                'font_name': 'Arial',
                'font_size': 9
            }),
            'numeric_2_f9_border': workbook.add_format({
                'num_format': '_(* #,##0_);_(* \(#,##0\);_(* "-"??_);_(@_)',
                'font_size': 9,
                'border': True
            }),
            'numeric_f9_border': workbook.add_format({
                'num_format': '_-* #,##0.00 _A_r_-;-* #,##0.00 _A_r_-;_-* "-"?? _A_r_-;_-@_-',
                'font_size': 9,
                'border': True
            }),
            'numeric_f9_border_without_space': workbook.add_format({
                'num_format': '0.00 _A_r_-;-*0.00 _A_r_-;_-* "-"?? _A_r_-;_-@_-',
                'font_size': 9,
                'border': True
            }),
            'numeric_f10_arial_border': workbook.add_format({
                'num_format': '_-* #,##0.00 _A_r_-;-* #,##0.00 _A_r_-;_-* "-"?? _A_r_-;_-@_-',
                'font_size': 10,
                'font_name': 'Arial',
                'border': True
            }),
            'numeric_f11_center_border': workbook.add_format({
                'num_format': '_-* #,##0.00 _A_r_-;-* #,##0.00 _A_r_-;_-* "-"?? _A_r_-;_-@_-',
                'font_size': 11,
                'align': 'center',
                'border': True
            }),
            'numeric_f9_double_border': numeric_f9_double_border,
            'numeric_f9_borderbgyellow': workbook.add_format({
                'num_format': '_-* #,##0.00 _A_r_-;-* #,##0.00 _A_r_-;_-* "-"?? _A_r_-;_-@_-',
                'font_size': 9,
                'border': True,
                'bg_color': 'yellow'
            }),
            'numeric_2_f9': workbook.add_format({
                'num_format': '_(* #,##0_);_(* \(#,##0\);_(* "-"??_);_(@_)',
                'font_size': 9
            }),
            'numeric_2': workbook.add_format({'num_format': '_(* #,##0_);_(* \(#,##0\);_(* "-"??_);_(@_)', }),
            'numeric_2_bold_bottom': workbook.add_format({
                'num_format': '_-* #,##0 _€_-;-* #,##0 _€_-;_-* "-"?? _€_-;_-@_-',
                'bold': True,
                'bottom': True,
            }),
            'numeric_bold': workbook.add_format({
                'num_format': '_-* #,##0.00 _A_r_-;-* #,##0.00 _A_r_-;_-* "-"?? _A_r_-;_-@_-',
                'bold': True,
            }),
            'numeric_bold_f9': workbook.add_format({
                'num_format': '_-* #,##0.00 _A_r_-;-* #,##0.00 _A_r_-;_-* "-"?? _A_r_-;_-@_-',
                'bold': True,
                'font_size': 9
            }),
            'bold_f16_center_calibri': workbook.add_format({
                'bold': True,
                'font_size': 16,
                'align': 'center',
                'font_name': 'Calibri',
            }),
            'bold_left_border': workbook.add_format({
                'bold': True,
                'align': 'left',
                'border': True,
                'bg_color': '#E7E6E6'
            }),
            'bold_center_border': workbook.add_format({
                'bold': True,
                'align': 'center',
                'border': True,
                'bg_color': '#F2F2F2'
            }),
            'bold_center_border_wrap': workbook.add_format({
                'bold': True,
                'align': 'center',
                'valign': 'vcenter',
                'border': True,
                'bg_color': '#F2F2F2',
                'text_wrap': 1
            }),
            'border': workbook.add_format({
                'border': True
            })
        }

    def get_quarter_range(self):
        """
        Get quarter range
        :param quarter:
        :return:
        """
        months = MONTHS[int(self.quarter)]
        year = int(self.year)
        quarter_range = []
        for month in months:
            month_range = calendar.monthrange(year, month)
            quarter_range.append(
                (date(year, month, 1), date(year, month, month_range[1])))
        return quarter_range

    def get_date_range(self):
        """
        Get quarter range date
        :param quarter:
        :return:
        """
        months = MONTHS[int(self.quarter)]
        year = int(self.year)
        lastmonth_range = calendar.monthrange(year, months[2])
        return (date(year, months[0], 1), date(year, months[2], lastmonth_range[1]))

    def get_filename(self):
        """
        Return filename or refererence
        :return: Char
        """
        name = 'OSTIE' if self.name == 'ostie' else 'CNAPS'
        return '%sT%s%s' % (str(int(self.quarter) + 1), self.year, name)

    def get_ostie_filename(self):
        """
        Return filename or refererence
        :return: Char
        """
        return str(self.company_id.ostie_member_code) + ' ' + str(self.company_id.name) + ' %sT%s' % (
            str(int(self.quarter) + 1), self.year)
