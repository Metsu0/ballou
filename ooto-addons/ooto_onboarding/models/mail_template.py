# -*- coding:utf-8 -*-
from odoo import _, api, fields, models, SUPERUSER_ID, tools


def _reopen(self, res_id, model, context=None):
    # save original model in context, because selecting the list of available
    # templates requires a model in context
    context = dict(context or {}, default_model=model)
    return {'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_id': res_id,
            'res_model': self._name,
            'target': 'new',
            'context': context,
            }


class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'

    user_onboarding_id = fields.Many2one("res.users", "Users")

    def save_as_template(self):
        """ hit save as template button: current form value will be a new
            template attached to the current document. """
        for record in self:
            model = self.env['ir.model']._get(record.model or 'mail.message')
            model_name = model.name or ''
            if record.user_onboarding_id:
                template_name = "%s: Invitation" % record.user_onboarding_id.name
            else:
                template_name = "%s: %s" % (model_name, tools.ustr(record.subject))
            values = {
                'name': template_name,
                'subject': record.subject or False,
                'body_html': record.body or False,
                'model_id': model.id or False,
                'user_onboarding_id': record.user_onboarding_id.id if record.user_onboarding_id else False,
                'attachment_ids': [(6, 0, [att.id for att in record.attachment_ids])],
            }
            template = self.env['mail.template'].create(values)
            # generate the saved template
            record.write({'template_id': template.id})
            record.onchange_template_id_wrapper()
            return _reopen(self, record.id, record.model, context=self._context)


class MailTemplate(models.Model):
    _inherit = "mail.template"

    user_onboarding_id = fields.Many2one("res.users", "Users")
    active = fields.Boolean("Active", default=True)
