# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.depends('list_price', 'taxes_id')
    def _compute_ati_price(self):
        for product in self:
            if len(product.taxes_id) != 0:
                product.ati_price = product.list_price + (product.list_price * product.taxes_id[0].amount)/100
            else:
                product.ati_price = product.list_price
        return product.ati_price

    ati_price = fields.Float('Prix TTC', compute=_compute_ati_price, store=True)
