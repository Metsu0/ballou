# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class IrModelFields(models.Model):
    _inherit = 'ir.model.fields'

    def _default_model_id_value(self):
        if self.env.context.get('hr_view', False) or self.env.context.get('hr_task_view', False):
            return self.env['ir.model'].search([('model', '=', 'hr.employee')], limit=1).id

    model_id = fields.Many2one(default=_default_model_id_value, readonly=True)

    is_visible_front_employee = fields.Boolean('Visible front Employee')
    is_visible_front_contact = fields.Boolean('Visible front Contact')

    @api.model
    def create(self, vals):

        state = vals.get('state', False) == 'manual'
        # Set column unique name and set number of characters up to 63
        res = super(IrModelFields, self).create(vals)
        if vals['name'].startswith('x_'):
            if vals['ttype'] in 'binary':
                fields_filename_val = {
                    'name': "x_filename_of_%s" % res.name,
                    'state': 'manual',
                    'model_id': self.env['ir.model'].search([('model', '=', 'hr.employee')], limit=1).id,
                    'ttype': "char",
                    'field_description': _("Filename of %s") % res.field_description,
                }
                self.sudo().create(fields_filename_val)
        return res

    def write(self, vals):
        # if set, *one* column can be renamed here
        column_rename = None
        # names of the models to patch
        patched_models = set()
        if 'serialization_field_id' in vals or 'name' in vals:
            for field in self:
                if field.serialization_field_id.id != vals['serialization_field_id']:
                    raise UserError(_('Changing the storing system for field "%s" is not allowed.') % field.name)
                if field.serialization_field_id and (field.name != vals['name']):
                    raise UserError(_('Renaming sparse field "%s" is not allowed') % field.name)

        if vals and self:
            # check selection if given
            if vals.get('selection'):
                self._check_selection(vals['selection'])

            for item in self:

                if vals.get('model_id', item.model_id.id) != item.model_id.id:
                    raise UserError(_("Changing the model of a field is forbidden!"))

                if vals.get('ttype', item.ttype) != item.ttype:
                    raise UserError(_("Changing the type of a field is not yet supported. "
                                      "Please drop it and create it again!"))

                obj = self.pool.get(item.model)
                field = getattr(obj, '_fields', {}).get(item.name)

                if vals.get('name', item.name) != item.name:
                    # We need to rename the field
                    item._prepare_update()
                    if item.ttype in ('one2many', 'many2many'):
                        # those field names are not explicit in the database!
                        pass
                    else:
                        if column_rename:
                            raise UserError(_('Can only rename one field at a time!'))
                        column_rename = (obj._table, item.name, vals['name'], item.index)

                # We don't check the 'state', because it might come from the context
                # (thus be set for multiple fields) and will be ignored anyway.
                if obj is not None and field is not None:
                    patched_models.add(obj._name)

        result = models.Model.write(self, vals)
        return result
