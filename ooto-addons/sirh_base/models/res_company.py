# -*- coding: utf-8 -*-

from odoo import models, fields, _, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    owner_id = fields.Many2one('res.users', string='Owner')
    rh_responsible_id = fields.Many2one('res.users', string='RH responsible')
    owner_title = fields.Selection([('mr', _('Mr.')), ('mrs', _('Mrs.')), ('miss', _('Miss'))], string='Title',
                                   default='mr')
    post_office_box = fields.Char(string='BP')
    fax = fields.Char(string='Fax')
    fmfp_threshold = fields.Float('FMFP threshold', compute='_compute_thresholds')
    fmfp_employer_contribution = fields.Float('FMFP employer contribution (%)')
    irsa_threshold = fields.Float("IRSA threshold")
    irsa_rate = fields.Float("IRSA rate (%)")
    irsa_allowance = fields.Float("IRSA allowance")
    cnaps_ostie_threshold = fields.Float("CNAPS and OSTIE threshold", compute='_compute_thresholds')
    cnaps_employer_contribution = fields.Float("CNAPS Employer Contribution (%)")
    cnaps_employee_contribution = fields.Float("CNAPS Employee contribution (%)")
    employer_health_contribution = fields.Float("Employer Health Contribution (%)")
    employee_health_contribution = fields.Float("Employee Health Contribution (%)")
    meal_amount = fields.Float("Meal amount")
    child_deduction_amount = fields.Float("Child deduction amount")
    number_day_off_monthly = fields.Float("Number of day off monthly")
    nif = fields.Char("NIF")
    stat = fields.Char("STAT")
    rcs = fields.Char("RCS")
    iri_rate = fields.Float("IRI rate (%)")
    ostie_member_code = fields.Char('OSTIE member code')
    cnaps_member_code = fields.Char('CNAPS member code')
    ostie_folio = fields.Char('OSTIE Folio')
    minimum_hiring_salary = fields.Float(string='Minimum hiring salary', default=0)
    declaration_date = fields.Date('Declaration date')
    cnaps_threshold_employer = fields.Float(string='CNAPS threshold employer', compute='_compute_thresholds')
    cnaps_threshold_employee = fields.Float(string='CNAPS threshold employee', compute='_compute_thresholds')
    ostie_threshold_employer = fields.Float(string='OSTIE threshold employer', compute='_compute_thresholds')
    ostie_threshold_employee = fields.Float(string='OSTIE threshold employee', compute='_compute_thresholds')
    company_activity = fields.Char('Activity of company')

    @api.depends('minimum_hiring_salary', 'employer_health_contribution', 'employee_health_contribution',
                 'cnaps_employer_contribution', 'cnaps_employee_contribution')
    def _compute_thresholds(self):
        """
        Compute default thesholds : CNAPS, OSTIE, FMFP
        :return:
        """
        self.cnaps_ostie_threshold = self.minimum_hiring_salary * 8
        self.ostie_threshold_employer = self.cnaps_ostie_threshold * (self.employer_health_contribution / 100)
        self.ostie_threshold_employee = self.cnaps_ostie_threshold * (self.employee_health_contribution / 100)
        self.cnaps_threshold_employee = self.cnaps_ostie_threshold * (self.cnaps_employee_contribution / 100)
        self.cnaps_threshold_employer = self.cnaps_ostie_threshold * (self.cnaps_employer_contribution / 100)
        self.fmfp_threshold = self.cnaps_ostie_threshold * (self.fmfp_employer_contribution / 100)

    def write(self, values):
        if values.get('resource_calendar_id', False):
            self.update_employee_resource_calendar_id(values.get('resource_calendar_id'))
        return super(ResCompany, self).write(values)

    @api.model
    def update_employee_resource_calendar_id(self, resource_calendar_id):
        """
        Method to update employee resource_calendar_id to be related to company resource_calendar_id
        :return: True
        """
        for rec in self:
            employee_ids = self.env['hr.employee'].search([('company_id', '=', rec.id)])
            for employee_id in employee_ids:
                employee_id.write({
                    'resource_calendar_id': resource_calendar_id,
                })
                employee_id.contract_id.resource_calendar_id = resource_calendar_id
        return True
