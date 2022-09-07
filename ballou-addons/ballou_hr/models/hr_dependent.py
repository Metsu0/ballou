# coding: utf-8
from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import models, fields, _, api


class HrDependent(models.Model):
    _name = 'hr.dependent'
    _description = 'Employee dependent'

    employee_id = fields.Many2one('hr.employee', 'Employee')
    firstname = fields.Char('Firstname', required=True)
    lastname = fields.Char('Lastname', required=True)
    birthdate = fields.Date('Birthdate', required=True)
    age = fields.Float('Age', compute='_compute_age')
    age_txt = fields.Char('Age', compute='_compute_age')
    is_handicap = fields.Boolean('Handicap', default=False)
    gender = fields.Selection([('male', _('male')), ('female', _('female')), ('other', _('Other'))], default='male')

    @api.depends('birthdate')
    def _compute_age(self):
        """
        Compute children age
        :return:
        """
        for rec in self:
            # Variable init
            today = date.today()
            birthdate = rec.birthdate
            diff = relativedelta(today, birthdate)
            years = _('{} an(s)'.format(diff.years)) if diff.years else ''
            months = _(' {} mois'.format(diff.months)) if diff.months else ''
            days = _(' {} jour(s)'.format(diff.days)) if diff.days else ''
            # Set age

            rec.age = ((today.year - birthdate.year) * 12 + (today.month - birthdate.month)) / 12 if birthdate else 0
            rec.age_txt = '{}{}{}'.format(years, months, days)
