# -*- coding: utf-8 -*-

from odoo import models, fields, _, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    responsible_id = fields.Many2one('hr.employee', string='responsible')
    nif = fields.Char("NIF")
    stat = fields.Char("STAT")
    ostie_member_code = fields.Char('OSTIE member code')
    cnaps_member_code = fields.Char('CNAPS member code')
    ostie_folio = fields.Char('OSTIE Folio')
    company_activity = fields.Char('Activity of company')
