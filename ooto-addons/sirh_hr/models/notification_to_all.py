# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
class SendNotification(models.TransientModel):
    _name = 'front.notification.all'
    _description = 'Sending notification for all modification made by user'


    def _get_default_base_url(self):
        return self.env['ir.config_parameter'].sudo().get_param('web.base.url')

    @api.model
    def _set_default_email_to(self):
        return self.env['res.partner'].search([('email', 'in', ['all@etechconsulting-mg.com','all@arkeup.com','all@lcas-agency.com'])]).ids

    newsletter = fields.Boolean("Newsletter")
    good_to_know = fields.Boolean("Good to know")
    we_hire = fields.Boolean("We hire")
    know_how = fields.Boolean("Know How")
    base_url = fields.Text("Base Url",default=_get_default_base_url)
    subject = fields.Char("Subject")
    email_to_ids = fields.Many2many('res.partner', string='To', default=_set_default_email_to,domain=lambda self: [("email", "<>", '')])


    def send_notification(self):
        self.ensure_one()
        template = self.env.ref('sirh_hr.mail_template_notify_all',raise_if_not_found=False)
        list_email_to = ""
        if self.email_to_ids:
            for receipt in self.email_to_ids:
                list_email_to = list_email_to + receipt.email + ","
        if self.newsletter or self.good_to_know or self.we_hire or self.know_how:
            template.sudo().send_mail(self.id,
                                email_values={'subject':self.subject,
                                              'email_to':list_email_to[:len(list_email_to)-1],
                                              'email_from': self.env.user.email or '' }, force_send=True)
        else:
            return