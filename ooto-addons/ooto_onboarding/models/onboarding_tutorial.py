# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, exceptions


class OnboardingTutorial(models.Model):
    _name = "onboarding.tutorial"
    _description = "Onboarding tutorial"

    title = fields.Char('Title', required=True)
    page_number = fields.Integer('Page number', readonly=True, compute="_check_page_number", store=True)
    page_id = fields.One2many(comodel_name='onboarding.tutorial.page', inverse_name='tutorial', string='Pages')
    count_page = fields.Integer()

    @api.depends('page_id')
    def _check_page_number(self):
        """
        Method to count page number.
        :return: None
        """
        self.page_number = len(self.page_id)

    def write(self, vals):
        """
        Inheriting def write of tutorial
        :param vals: tutorial fields values
        :return: result
        """
        res = super(OnboardingTutorial, self).write(vals)
        page_id = vals.get('page_id')
        pages = self.page_id
        if page_id:
            n = []
            all_pages = []
            for page in page_id:
                if page[2] and page[0] != 0:
                    for key in page[2]:
                        if 'number' in key:
                            if page[2]['number'] in n:
                                raise exceptions.ValidationError(_(
                                    "The value of page number must be unique. Please choose another number or change the other pages "))
                            elif page[2]['number'] == 0:
                                raise exceptions.ValidationError(
                                    _("The value of page number must be positive ."))
                            else:
                                n.append(page[2]['number'])
                                all_pages.append(page[1])
                            unchanged_pages = pages.filtered(lambda self: self.id not in all_pages)
                            for p in unchanged_pages:
                                if p.number in n:
                                    raise exceptions.ValidationError(_(
                                        "The value of page number must be unique. Please choose another number or change the other pages "))
                elif page[0] == 0:
                    if page[2]['number'] == 0:
                        raise exceptions.ValidationError(
                            _("The value of page number must be positive ."))
        return res


class OnboardingTutorialPage(models.Model):
    _name = "onboarding.tutorial.page"
    _description = "Onboarding tutorial page"
    _order = "number asc"

    title = fields.Html('Title', required=True)
    description = fields.Html('Description')
    support = fields.Binary('Support')
    number = fields.Integer(string='Concerned page')
    tutorial = fields.Many2one("onboarding.tutorial")

    @api.model
    def create(self, values):
        res = super(OnboardingTutorialPage, self).create(values)
        pages = self.search([])
        len_pages = len(pages)

        if res.number:
            if res.number > len_pages or res.number < 1 or res.number == 0:
                raise exceptions.ValidationError(
                    _("The value of page number must be positve and lower or equal to %s .") % len_pages)
            pages = self.search([('id', '!=', res.id)])
            for page in pages:
                if res.number == page.number:
                    raise exceptions.ValidationError(_(
                        "The value of page number must be unique. Please choose another number or change the other pages "))
        return res

    def write(self, vals):
        res = super(OnboardingTutorialPage, self).write(vals)
        all_pages = self.search([])
        len_pages = len(all_pages)

        if vals.get('number'):
            if vals.get('number') > len_pages or vals.get('number') < 1 or vals.get == 0:
                raise exceptions.ValidationError(
                    _("The value of page number must be positve and lower or equal to %s .") % len_pages)
        return res

    def unlink(self):
        pages = self.search([])
        len_pages = len(pages)
        if len(self) == 1:
            page_to_update = pages.filtered(lambda p: p.number == len_pages)
            page_to_update[0].write({'number': self.number})
        else:
            page_to_update = self.search([('id', 'not in', self.ids)], order='number DESC', limit=len(self))
            n = 1
            for page in self:
                if len(page_to_update) >= n:
                    page_to_update[n - 1].write({'number': page.number})
                    n += 1
        return super(OnboardingTutorialPage, self).unlink()
