# -*- coding: utf-8 -*-
from lxml import etree

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    note2 = fields.Text('Deuxième note')

    def action_confirm(self):
        unavailable_stocks = {}
        warehouse_id = self.warehouse_id
        if not warehouse_id:
            warehouse_id = self.env.user.with_company(company_id)._get_default_warehouse_id().id
        location_id = warehouse_id.lot_stock_id
        if self.order_line:
            for line in self.order_line.sudo().filtered(lambda x: x.product_id.type != 'service'):
                rounding = line.product_id.uom_id.rounding
                available_quantity = self.env["stock.quant"].sudo()._get_available_quantity(
                    line.product_id, location_id)
                quantity = line.product_uom_qty
                if float_compare(quantity, available_quantity, precision_rounding=rounding) > 0:
                    unavailable_stocks[line.product_id] = {
                        'product': line.product_id.name,
                        'qty': available_quantity
                    }
            if unavailable_stocks and unavailable_stocks.keys():
                message = "Vous ne pouvez pas valider ce devis parce que la quantité demandée n'est pas disponible :\n"
                for product_id in unavailable_stocks.keys():
                    message += "\t- {}, {} disponible\n".format(
                        unavailable_stocks.get(product_id).get('product'),
                        unavailable_stocks.get(product_id).get('qty'))
                raise UserError(_(message))
            else:
                res = super(SaleOrder, self).action_confirm()
        else:
            raise UserError("Aucune ligne a confirmer!")

    def _prepare_invoice(self):
        res = super()._prepare_invoice()
        res["note2"] = self.note2
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_user_admin = fields.Boolean(compute='_check_user_group')

    def _check_user_group(self):
        if self.env.user.has_group('ballou_sales.group_admin'):
            self.is_user_admin = True
        else:
            self.is_user_admin = False
