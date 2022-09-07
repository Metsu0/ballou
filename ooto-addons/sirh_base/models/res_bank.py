# -*- coding: utf-8 -*-

from odoo import fields, models


class ResBank(models.Model):
    _inherit = 'res.bank'

    rib_key = fields.Char(string='RIB Key')
    bank_code = fields.Char(string='Bank Code')


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    rib_key = fields.Char(string='RIB Key')
    bank_code = fields.Char(string='Bank Code')
    agency_code = fields.Char(string='Agency Code')
