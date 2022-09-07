from odoo import models, fields


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    name = fields.Char(string="Catégorie Partenaire")

    def _select(self):
        return super(AccountInvoiceReport, self)._select() + """,
            categ.name"""

    def _from(self):
        return super(AccountInvoiceReport, self)._from() + """
            left join res_partner_res_partner_personalized_category_rel rel on partner.id = rel.res_partner_id
            left join res_partner_personalized_category categ on rel.res_partner_personalized_category_id = categ.id"""