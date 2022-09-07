# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from lxml import etree
from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare, float_is_zero
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def _fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(AccountMove, self)._fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                        submenu=submenu)
        print(res)
        if view_type == 'tree':
            # self.env['ir.model.fields'].create({
            #     'name': 'x_test_champ2',
            #     'model_id': self.env['ir.model']._get_id('account.move'),
            #     'ttype': 'integer',
            #
            # })
            print(res['arch'])
            eview = etree.fromstring(res['arch'])
            summary = eview.xpath("//field[@name='partner_id']")
            if len(summary):
                summary = summary[0]
                summary.addnext(etree.Element('field', {'name': 'x_test_champ2',
                                                        'string': 'Milay oa',

                                                        }))
            res['arch'] = etree.tostring(eview)
            # res['arch'] = self._fields_view_get_address(res['arch'])
        return res
