# -*- encoding: utf-8 -*-

import logging

from odoo.exceptions import AccessError
from odoo.osv.query import Query
from odoo import api, _
from odoo.models import BaseModel

_logger = logging.getLogger(__name__)


class ExtendBaseModel(BaseModel):
    _name = 'basemodel.extend'

    @api.model
    def _check_bypass_model(self, model_name, active_model):
        if model_name != active_model:
            query_args = {'active_model': active_model}
            query = """
                select t1.id from dynamic_bypass_rule as t1 
                left join ir_model as t2 on t1.model_id = t2.id where t2.model = %(active_model)s
            """
            self._cr.execute(query, query_args)
            res = self._cr.dictfetchall()
            if res:
                query_args = {'bypass_rule_id': res[0].get('id'), 'model': model_name}
                query = """
                    select count(*) from dynamic_bypass_rule_ir_model_rel as t1 
                    left join ir_model as t2 on t1.ir_model_id =  t2.id 
                    where t1.dynamic_bypass_rule_id = %(bypass_rule_id)s and t2.model = %(model)s
                """
                self._cr.execute(query, query_args)
                res = self._cr.fetchall()
                if res and res[0][0] > 0:
                    return True
        return False

    def _read(self, fields):
        """ Read the given fields of the records in ``self`` from the database,
            and store them in cache. Access errors are also stored in cache.
            Skip fields that are not stored.

            :param field_names: list of column names of model ``self``; all those
                fields are guaranteed to be read
            :param inherited_field_names: list of column names from parent
                models; some of those fields may not be read
        """
        if not self:
            return
        self.check_access_rights('read')

        # if a read() follows a write(), we must flush updates, as read() will
        # fetch from database and overwrites the cache (`test_update_with_id`)
        self.flush(fields, self)

        field_names = []
        inherited_field_names = []
        for name in fields:
            field = self._fields.get(name)
            if field:
                if field.store:
                    field_names.append(name)
                elif field.base_field.store:
                    inherited_field_names.append(name)
            else:
                _logger.warning("%s.read() with unknown field '%s'", self._name, name)

        env = self.env
        cr, user, context, su = env.args

        # make a query object for selecting ids, and apply security rules to it
        param_ids = object()
        query = Query(['"%s"' % self._table], ['"%s".id IN %%s' % self._table], [param_ids])

        # bypass rule
        active_model = self._context.get('model', False)
        if active_model:
            if not self._check_bypass_model(self._name, active_model):
                self._apply_ir_rules(query, 'read')
        else:
            self._apply_ir_rules(query, 'read')

        # determine the fields that are stored as columns in tables; ignore 'id'
        fields_pre = [
            field
            for field in (self._fields[name] for name in field_names + inherited_field_names)
            if field.name != 'id'
            if field.base_field.store and field.base_field.column_type
            if not (field.inherited and callable(field.base_field.translate))
        ]

        # the query may involve several tables: we need fully-qualified names
        def qualify(field):
            col = field.name
            res = self._inherits_join_calc(self._table, field.name, query)
            if field.type == 'binary' and (context.get('bin_size') or context.get('bin_size_' + col)):
                # PG 9.2 introduces conflicting pg_size_pretty(numeric) -> need ::cast
                res = 'pg_size_pretty(length(%s)::bigint)' % res
            return '%s as "%s"' % (res, col)

        # selected fields are: 'id' followed by fields_pre
        qual_names = [qualify(name) for name in [self._fields['id']] + fields_pre]

        # determine the actual query to execute
        from_clause, where_clause, params = query.get_sql()
        query_str = "SELECT %s FROM %s WHERE %s" % (",".join(qual_names), from_clause, where_clause)

        # fetch one list of record values per field
        param_pos = params.index(param_ids)

        result = []
        for sub_ids in cr.split_for_in_conditions(self.ids):
            params[param_pos] = tuple(sub_ids)
            cr.execute(query_str, params)
            result += cr.fetchall()

        fetched = self.browse()
        if result:
            cols = zip(*result)
            ids = next(cols)
            fetched = self.browse(ids)

            for field in fields_pre:
                values = next(cols)
                if context.get('lang') and not field.inherited and callable(field.translate):
                    translate = field.get_trans_func(fetched)
                    values = list(values)
                    for index in range(len(ids)):
                        values[index] = translate(ids[index], values[index])

                # store values in cache
                self.env.cache.update(fetched, field, values)

            # determine the fields that must be processed now;
            # for the sake of simplicity, we ignore inherited fields
            for name in field_names:
                field = self._fields[name]
                if not field.column_type:
                    field.read(fetched)
                if field.deprecated:
                    _logger.warning('Field %s is deprecated: %s', field, field.deprecated)

        # possibly raise exception for the records that could not be read
        missing = self - fetched
        if missing:
            extras = fetched - self
            if extras:
                raise AccessError(
                    _("Database fetch misses ids ({}) and has extra ids ({}), may be caused by a type incoherence in a previous request").format(
                        missing._ids, extras._ids,
                    ))
            # mark non-existing records in missing
            forbidden = missing.exists()
            if forbidden:
                raise self.env['ir.rule']._make_access_error('read', forbidden)


BaseModel._read = ExtendBaseModel._read
BaseModel._check_bypass_model = ExtendBaseModel._check_bypass_model
