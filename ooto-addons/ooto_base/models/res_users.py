# coding: utf-8

from odoo import models, fields, _
from odoo.tools.misc import ustr
from ast import literal_eval

from odoo.addons.auth_signup.models.res_partner import SignupError


class ResUsers(models.Model):
    _inherit = 'res.users'

    not_send_mail = fields.Boolean("Invitation mail", )
    no_reset_mail = fields.Boolean("Reset mail")

    def _create_user_from_template(self, values):
        template_user_id = literal_eval(
            self.env['ir.config_parameter'].sudo().get_param('base.template_portal_user_id', 'False'))
        template_user = self.browse(template_user_id)
        if not template_user.exists():
            raise ValueError(_('Signup: invalid template user'))

        if not values.get('login'):
            raise ValueError(_('Signup: no login given for new user'))
        if not values.get('partner_id') and not values.get('name'):
            raise ValueError(_('Signup: no name or partner given for new user'))

        # create a copy of the template user (attached to a specific partner_id if given)
        values['active'] = True
        try:
            with self.env.cr.savepoint():
                if values.get('no_reset_mail', False):
                    return template_user.with_context(no_reset_password=True).copy(values)
                else:
                    return template_user.with_context(no_reset_password=False).copy(values)
        except Exception as e:
            # copy may failed if asked login is not available.
            raise SignupError(ustr(e))
