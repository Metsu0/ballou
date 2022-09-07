# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

DEFAULT_PRIMARY = '#000000'
DEFAULT_SECONDARY = '#000000'


class BaseDocumentLayout(models.TransientModel):
    _inherit = 'base.document.layout'

    report_footer_receipt = fields.Text(related='company_id.report_footer_receipt', readonly=False)
    nif = fields.Char(related='company_id.partner_id.nif', readonly=True)
    stat = fields.Char(related='company_id.partner_id.stat', readonly=True)
    rcs = fields.Char(related='company_id.partner_id.rcs', readonly=True)
    street = fields.Char(related='company_id.street', readonly=True)
    street2 = fields.Char(related='company_id.street2', readonly=True)
    city = fields.Char(related='company_id.city', readonly=True)
    state_id = fields.Many2one('res.country.state', related='company_id.state_id', readonly=True)
    zip = fields.Char(related='company_id.zip', readonly=True)
    country_id = fields.Many2one('res.country', related='company_id.country_id', readonly=True)

    name = fields.Char(related='company_id.name', readonly=True)

    @api.depends('report_layout_id', 'logo', 'font', 'primary_color', 'secondary_color', 'report_header',
                 'report_footer', 'report_footer_receipt')
    def _compute_preview(self):
        """ compute a qweb based preview to display on the wizard """

        styles = self._get_asset_style()

        for wizard in self:
            if wizard.report_layout_id:
                preview_css = self._get_css_for_preview(styles, wizard.id)
                ir_ui_view = wizard.env['ir.ui.view']
                wizard.preview = ir_ui_view._render_template('web.report_invoice_wizard_preview',
                                                             {'company': wizard, 'preview_css': preview_css})
            else:
                wizard.preview = False

    @api.onchange('company_id')
    def _onchange_company_id(self):
        for wizard in self:
            wizard.logo = wizard.company_id.logo
            wizard.report_header = wizard.company_id.report_header
            wizard.report_footer = wizard.company_id.report_footer
            wizard.report_footer_receipt = wizard.company_id.report_footer_receipt
            wizard.paperformat_id = wizard.company_id.paperformat_id
            wizard.external_report_layout_id = wizard.company_id.external_report_layout_id
            wizard.font = wizard.company_id.font
            wizard.primary_color = wizard.company_id.primary_color
            wizard.secondary_color = wizard.company_id.secondary_color
            wizard_layout = wizard.env["report.layout"].search([
                ('view_id.key', '=', wizard.company_id.external_report_layout_id.key)
            ])
            wizard.report_layout_id = wizard_layout or wizard_layout.search([], limit=1)

            if not wizard.primary_color:
                wizard.primary_color = wizard.logo_primary_color or DEFAULT_PRIMARY
            if not wizard.secondary_color:
                wizard.secondary_color = wizard.logo_secondary_color or DEFAULT_SECONDARY
