# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta

from odoo import api, _, fields, models


class RenewTrialContractWizard(models.TransientModel):
    _name = 'hr.ooto.contract.wizard'

    name = fields.Char('Contract Reference', required=True)
    date_end = fields.Date('End Date', help="End date of the contract (if it's a fixed-term contract).")
    trial_date_end = fields.Date('End of Trial Period', help="End date of the trial period (if there is one).")

    duration = fields.Char(string='Duration', track_visibility='onchange')
    duration_years = fields.Integer(string='Year(s)')
    duration_months = fields.Integer(string='Month(s)')
    duration_days = fields.Integer(string='Day(s)')

    def _default_contract(self):
        sirh_hr_state = self.env['ir.module.module'].search([('name', '=', 'sirh_hr')]).state
        if sirh_hr_state == 'installed':
            if self.env['hr.contract'].search([('id', '=', self._context.get('active_id'))]).contract_type == 'cdi':
                return True
            else:
                return False
        else:
            return False

    is_cdi = fields.Boolean('Contract CDI', default=_default_contract)

    def _default_duration(self):
        sirh_hr_state = self.env['ir.module.module'].search([('name', '=', 'sirh_hr')]).state
        if sirh_hr_state == 'installed':
            if 'duration' in self.env['hr.contract']._fields:
                return True
            else:
                return False
        else:
            return False

    is_duration = fields.Boolean('Contract CDI', default=_default_duration)

    def save(self):
        contract_id = self.env['hr.contract'].search([('id', '=', self._context.get('active_id'))])

        om_hr_payroll_state = self.env['ir.module.module'].search([('name', '=', 'om_hr_payroll')]).state
        sirh_hr_state = self.env['ir.module.module'].search([('name', '=', 'sirh_hr')]).state
        madajob_hr_state = self.env['ir.module.module'].search([('name', '=', 'madajob_hr')]).state

        if self.is_duration:
            self.date_end = contract_id.date_start + relativedelta(years=self.duration_years, months=self.duration_months,
                                                                   days=self.duration_days)
            self.duration = str(self.duration_years) + _(' year(s) ') + str(self.duration_months) + _(
                ' month(s) ') + str(self.duration_days) + _(' day(s)')

        values = {
            'name': self.name,
            'employee_id': contract_id.employee_id.id,
            'department_id': contract_id.department_id.id,
            'company_id': contract_id.company_id.id,
            'job_id': contract_id.job_id.id,
            'date_start': contract_id.date_start,
            'date_end': self.date_end,
            'trial_date_end': self.trial_date_end,
            'resource_calendar_id': contract_id.resource_calendar_id.id,
            'hr_responsible_id': contract_id.hr_responsible_id.id,
            'wage': contract_id.wage
        }

        if om_hr_payroll_state == 'installed':
            values.update({
                'payslip_payment_mode_id': contract_id.payslip_payment_mode_id.id,
                'struct_id': contract_id.struct_id.id,
            })

        if sirh_hr_state == 'installed':
            values.update({
                'contract_type': contract_id.contract_type,
                'coach_id': contract_id.coach_id.id,
                'duration': self.duration,
                'duration_years': self.duration_years,
                'duration_months': self.duration_months,
                'duration_days': self.duration_days,
            })

        if madajob_hr_state == 'installed':
            values.update({
                'reference': contract_id.reference,
                'commission': contract_id.commission,
                'housing_indemnity': contract_id.housing_indemnity,
                'transport_allowance': contract_id.transport_allowance,
                'precariousness_allowance': contract_id.precariousness_allowance,
                'other_advantages': contract_id.other_advantages,
            })

        self.env['hr.contract'].create(values)
