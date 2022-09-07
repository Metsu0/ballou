# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from lxml import etree


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    sale_type = fields.Selection([
        ('occasional', 'Occasional'),
        ('reference', 'Reference')
    ])


class AccountMove(models.Model):
    _inherit = 'account.move'

    note2 = fields.Text('Deuxième note')

    @api.onchange('partner_id')
    def _compute_journal_id(self):
        partner_type = self.partner_id.company_type
        journal_occasional = self.env['account.journal'].search([('company_id','=',self.company_id.id),('sale_type', '=', 'occasional')])
        journal_reference = self.env['account.journal'].search([('company_id','=',self.company_id.id),('sale_type', '=', 'reference')])

        if self.move_type in ('out_invoice','out_refund'):
            if partner_type == 'person':
                self.journal_id = journal_occasional
            else:
                self.journal_id = journal_reference

    @api.model
    def create(self, values):
        journal_occasional = self.env['account.journal'].search([('company_id','=',values.get('company_id')),('sale_type', '=', 'occasional')])
        journal_reference = self.env['account.journal'].search([('company_id','=',values.get('company_id')),('sale_type', '=', 'reference')])
        partner = self.env['res.partner'].search([('id', '=', values.get('partner_id'))])

        if 'move_type' in values:
            if values['move_type'] in ('out_invoice','out_refund'):
                if partner[0].company_type == 'person':
                    values['journal_id'] = journal_occasional.id
                else:
                    values['journal_id'] = journal_reference.id

        return super(AccountMove, self).create(values)


    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(AccountMove, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                       submenu=submenu)

        # hide create button on the form, tree and kanban view of account.move model for group_account_move users group
        if view_type in ['form', 'tree', 'kanban'] and self.env.user.has_group('ballou_sales.group_account_move'):
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//{}".format(view_type)):
                node.set('create', '0')
            res['arch'] = etree.tostring(doc, encoding='unicode')

        return res
