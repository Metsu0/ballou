# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _


class Survey(models.Model):
    _inherit = 'survey.survey'

    period = fields.Selection([
        ('before_arrival', _('Before arrival')),
        ('arrival_day', _('Arrival day')),
        ('first_week', _('First week')),
        ('first_month', _('First month')),
        ('after_first_month', _('After first month')),
        ('specific', _('Specific')),
    ], string="Period")

    questions_layout = fields.Selection(default='page_per_section')

    is_filled = fields.Boolean("Is survey filled", default=False)

    task_belong = fields.Boolean("Is survey belong to a task", default=False)
    
    certificate = fields.Boolean('Certificate')

    def _default_state_onboarding(self):
        default = "specific"
        if self.period:
            return self.period
        else:
            return default

    state_onboarding = fields.Selection([
        ('before_arrival', 'Before arrival'),
        ('arrival_day', 'Arrival day'),
        ('first_week', 'First week'),
        ('first_month', 'First month'),
        ('after_first_month', 'After first month'),
        ('specific', 'Specific'),
    ], string="Survey onboarding state", default=_default_state_onboarding, required=True,
        group_expand='_read_group_state_onboarding', compute='compute_state_onboarding', store=True
    )

    with_onboarding = fields.Boolean(string="Survey with onboarding", default=False)

    def _read_group_state_onboarding(self, values, domain, order):
        selection = self.env['survey.survey'].fields_get(allfields=['state_onboarding'])['state_onboarding']['selection']
        return [s[0] for s in selection]

    @api.depends('period')
    def compute_state_onboarding(self):
        for rec in self:
            if rec.period:
                rec.task_belong = True

                if rec.period == 'before_arrival':
                    rec.state_onboarding = rec.period
                elif rec.period == 'arrival_day':
                    rec.state_onboarding = rec.period
                elif rec.period == 'first_week':
                    rec.state_onboarding = rec.period
                elif rec.period == 'first_month':
                    rec.state_onboarding = rec.period
                elif rec.period == 'after_first_month':
                    rec.state_onboarding = rec.period
                elif rec.period == 'specific':
                    rec.state_onboarding = rec.period
                else:
                    # rec.stage_id = self.env.search([], limit=1).id
                    return self.env['survey.survey'].search([], limit=1).id
