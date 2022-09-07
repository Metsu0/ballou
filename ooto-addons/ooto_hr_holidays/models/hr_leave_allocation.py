# coding: utf-8

from odoo import models, fields, api


class HrLeaveAllocation(models.Model):
    _inherit = 'hr.leave.allocation'

    accrual_leaves_count = fields.Float('Accrual leaves count', compute='_compute_accrual_leaves_count')
    balance_accrual_leaves_count = fields.Float(
        'Balance accrual leaves count',
        compute='_compute_balance_accrual_leaves_count'
    )
    confirmation_date = fields.Datetime('Confirmation date', default=False)

    def action_validate(self):
        """
        Set confirmation date when validate leave allocation
        :return:
        """
        res = super(HrLeaveAllocation, self).action_validate()
        self.write({'confirmation_date': fields.Datetime.now()})
        return res

    @api.depends('nextcall', 'number_of_days')
    def _compute_accrual_leaves_count(self):
        """
        Compute gotten accrual leaves count in specific date
        If there is no date specified, the function will take the accrual leaves count in the current date
        :return:
        """
        # Variable initialization
        date_from = self.env.context.get('date_from', False)
        date_to = self.env.context.get('date_to', False)
        for rec in self:
            tracking_value_ids = rec.message_ids.mapped('tracking_value_ids')
            if date_to and date_from:
                filtered_tracking_ids = tracking_value_ids.filtered(lambda t: date_from <= t.create_date <= date_to)
                rec.accrual_leaves_count = max(filtered_tracking_ids.mapped('new_value_float'))
            else:
                rec.accrual_leaves_count = max(tracking_value_ids.mapped('new_value_float'))

    def get_balance_accrual_leaves_count(self, date_from=False, date_to=False):
        """
        Get balance of gotten accrual leaves count in specific date
        If there is no date specified, the function will take the balance for the last allocation accrual
        :return: Float
        """
        # Variable initialization
        sum_balance = 0
        for rec in self:
            tracking_value_ids = rec.message_ids.mapped('tracking_value_ids')
            if date_to and date_from:
                filtered_tracking_ids = tracking_value_ids.sudo().filtered(
                    lambda t: date_from <= t.create_date <= date_to)
                sum_balance += sum(filtered_tracking_ids.sudo().mapped('new_value_float')) - \
                               sum(filtered_tracking_ids.sudo().mapped('old_value_float'))
            elif date_to and not date_from:
                tracking_value_id = max(tracking_value_ids.sudo().filtered(lambda t: t.create_date <= date_to))
                sum_balance += tracking_value_id.new_value_float
            else:
                tracking_value_id = max(tracking_value_ids)
                sum_balance += tracking_value_id.new_value_float - tracking_value_id.old_value_float
        return sum_balance

    @api.model
    def _set_allocation_confirmation_date(self):
        """
        Set confirmation date for approved leave allocation
        :return:
        """
        allocation_ids = self.sudo().search([('state', '=', 'validate'), ('confirmation_date', '=', False)])
        for allocation_id in allocation_ids:
            mail_tracking_value_ids = self.env['mail.tracking.value'].sudo().search([
                ('field', '=', 'state'),
                ('mail_message_id', 'in', allocation_id.message_ids.ids)
            ])
            confirmation_date = mail_tracking_value_ids[-1].create_date if len(mail_tracking_value_ids) else False
            allocation_id.confirmation_date = confirmation_date
