# -*- encoding: utf-8 -*-

from odoo import _, api, models
from odoo.exceptions import AccessError


class Base(models.AbstractModel):
    _inherit = 'base'

    def export_data(self, fields_to_export):
        if self.env.user.has_group('web_disable_export_group.group_export_data'):
            field_names = map(
                lambda path_array: path_array[0], map(
                    models.fix_import_export_id_paths,
                    fields_to_export,
                ),
            )
            self.env['export.event'].log_export(self, field_names)
            return super(Base, self).export_data(fields_to_export)
        else:
            raise AccessError(
                _('You do not have permission to export data'),
            )
