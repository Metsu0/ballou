# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    nif = fields.Char("NIF")
    stat = fields.Char("STAT")
    rcs = fields.Char("RCS")
    
    category_ids = fields.Many2many('res.partner.personalized.category', string="Catégorie")


class ResPartnerPersonalizedCategory(models.Model):
    _name = 'res.partner.personalized.category'

    name = fields.Char()
    color = fields.Integer()
