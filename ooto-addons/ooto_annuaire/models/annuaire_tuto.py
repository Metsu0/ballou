# -*- coding: utf-8 -*-

from odoo import _, fields, models, api, exceptions


class AnnuaireTutoPage(models.Model):
    _name = 'annuaire.tuto.page'
    _description = 'Annuaire tutorial page in website'
    _order = 'page_number'

    name = fields.Html('Title', required=True)
    description = fields.Html('Description')
    support = fields.Binary('Image')
    page_number = fields.Integer(string='Page number')
    tuto_id = fields.Many2one('annuaire.tuto', 'Concerned tutorial')


class AnnuaireTuto(models.Model):
    _name = "annuaire.tuto"
    _description = "Annuaire Tutorial"

    name = fields.Char('Title', required=True)
    page_ids = fields.One2many('annuaire.tuto.page', 'tuto_id', 'Tutorial pages')

    @api.model
    def get_annuaire_tuto_pages(self):
        """
        Get annuaire tutorial pages
        :return: List
        """
        # Variable initialization
        page_list = []
        tuto_id = self.env.ref('ooto_annuaire.default_annuaire_tuto_config')
        page_ids = tuto_id.page_ids.sorted(lambda p: p.page_number)
        for page_id in page_ids:
            page_list.append([page_id.name, page_id.description, page_id.support])
        return page_list