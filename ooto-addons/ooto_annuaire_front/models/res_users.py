# -*- coding: utf-8 -*-

from odoo import fields, models


class Users(models.Model):
    _inherit = "res.users"

    cumulated_search = fields.Char("Cumulated search")

    def array_to_str(self, cumulated_search, to_delete):
        new_val = []
        for val in cumulated_search.split(";"):
            if val != to_delete:
                new_val.append(val)
        return ";".join(new_val)

    def update_cumulated_search_list(self, to_delete):
        current_user = self.env.user
        new_cumulated_search = self.array_to_str(current_user.cumulated_search, to_delete)
        current_user.write({
            "cumulated_search": new_cumulated_search,
        })
        return new_cumulated_search
