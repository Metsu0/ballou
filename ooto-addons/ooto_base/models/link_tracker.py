# -*- coding:utf-8 -*-
#HRN not used on Odoo v14
# import re
# 
# from odoo import models, api
# from odoo.addons.link_tracker.models.link_tracker import URL_REGEX
# from werkzeug import utils



# class link_tracker(models.Model):
#     _inherit = "link.tracker"
# 
#     @api.model
#     def convert_links(self, html, vals, blacklist=None):
#         for match in re.findall(URL_REGEX, html):
#             short_schema = self.env['ir.config_parameter'].sudo().get_param('web.base.url') + '/r/'
#             href = match[0]
#             long_url = match[1]
#             vals['url'] = utils.unescape(long_url)
#             if 'reset_password' not in long_url:
#                 if not blacklist or not [s for s in blacklist if s in long_url] and not long_url.startswith(
#                         short_schema):
#                     link = self.create(vals)
#                     shorten_url = self.browse(link.id)[0].short_url
#                     if shorten_url:
#                         new_href = href.replace(long_url, shorten_url)
#                         html = html.replace(href, new_href)
#         return html
