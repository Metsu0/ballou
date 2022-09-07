from odoo import api, _, fields, models, exceptions
from dateutil.relativedelta import relativedelta
from datetime import datetime

all_months = {
    '1': 'January',
    '2': 'February',
    '3': 'March',
    '4': 'April',
    '5': 'May',
    '6': 'June',
    '7': 'July',
    '8': 'August',
    '9': 'September',
    '10': 'October',
    '11': 'November',
    '12': 'December',
}


def get_human_time(diff, date):
    if diff.years:
        return {'type': 'date',
                'value': _('ago ') + str(abs(diff.years)) + (_(' years ') if abs(diff.years) > 1 else _(' year '))}
    elif abs(diff.months):
        return {'type': 'date', 'value': _('ago ') + str(abs(diff.months)) + (_(' months ') if abs(diff.months) > 1 else _(' month '))}
    elif abs(diff.days):
        if abs(diff.days) > 30:
            return {'type': 'date',
                    'value': _('ago ') + str(diff.months) + (_(' months ') if abs(diff.months) > 1 else _(' month '))}
        else:
            return {
                'type': 'days',
                'value': _('ago ') + str(abs(diff.days)) + (_(' days ') if abs(diff.days) > 1 else _(' day ')),
                'days_value': abs(diff.days)
            }
    elif abs(diff.hours):
        return {'type': 'hours', 'value': _('ago ') + str(abs(diff.hours)) + (_(' hours ') if abs(diff.hours) > 1 else _(' hour '))}
    elif abs(diff.minutes):
        return {'type': 'minutes',
                'value': _('ago ') + str(abs(diff.minutes)) + (_(' minutes ') if abs(diff.minutes) > 1 else _(' minute '))}
    else:
        return {'type': 'seconds', 'value': _('Now')}


class Message(models.Model):
    _inherit = 'mail.message'

    date_format = fields.Char('Delay', compute='_compute_date_format')
    active = fields.Boolean("Active", default=True)
    onboarding_id = fields.Many2one("hr.onboarding", string="Onboarding")
    state_task = fields.Text()

    @api.model
    def archive_mail_10_days_ago(self):
        for mail in self.sudo().search([('model', '=', 'hr.onboarding.task'), ('active', '=', True)]):
            date = datetime.strptime(str(mail.date), '%Y-%m-%d %H:%M:%S')
            diff = relativedelta(datetime.now(), date)
            if get_human_time(diff, date).get('days_value', 0) > 10 or get_human_time(diff, date).get('type') == 'date':
                mail.write({'active': False})

    def _compute_date_format(self):
        for record in self:
            date_to_calc = str(record.date)
            date = datetime.strptime(date_to_calc, '%Y-%m-%d %H:%M:%S')
            diff = relativedelta(datetime.now(), date)
            record.date_format = get_human_time(diff, record.date).get('value')


class MassMailing(models.Model):
    _inherit = 'mailing.mailing'

    @api.onchange('mailing_model_id', 'contact_list_ids')
    def _onchange_model_and_list(self):
        super(MassMailing, self)._onchange_model_and_list()
        default_mailing_domain = self._context.get('default_mailing_domain')
        if self.mailing_model_name == 'res.partner' and default_mailing_domain:
            self.mailing_domain = default_mailing_domain
