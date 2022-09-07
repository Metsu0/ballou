# -*- coding: utf-8 -*-
import re
from collections import OrderedDict

from odoo import _
from odoo import http
from odoo.addons.website.controllers.main import QueryURL
from odoo.http import request


class AnnuaireController(http.Controller):

    @http.route('/my/annuaire', type='http', auth="user", website=True)
    def my_annuaire(self, search=None, filter=None, new_cumulated_search_list=None, **kwargs):
        values = dict()
        employee_obj = request.env['hr.employee']
        employe_id = employee_obj.sudo().search([('user_id', '=', request.session.uid)])
        if employe_id:
            employe_id = employe_id[0]

            p = {}
            c = r"<p>[ \n]*(<br>)?[ \n]*</p>"
            pages = []

            # ASSOCIATED CONTACTS FOR CONNECTED USER
            employee_ids = request.env.user.visible_contact_employee_ids

            an_fields_employee = request.env['annuaire.employee.section'].search(
                [('is_visible_front_employee', '=', True)])
            an_fields_employee = an_fields_employee - an_fields_employee[0:3]
            an_fields_contact = request.env['annuaire.associated.contacts'].search(
                [('is_visible_front_contact', '=', True)]).sorted('id')

            list_many2one_fields = []

            list_many2one_fields_setion_employee = an_fields_employee.mapped("fields_id").filtered(
                lambda f: f.ttype == 'many2one')
            for fld in list_many2one_fields_setion_employee:
                list_many2one_fields.append(fld.name)

            list_many2one_fields_setion_contact = an_fields_contact.mapped("fields_id").filtered(
                lambda f: f.ttype == 'many2one')
            for fld in list_many2one_fields_setion_contact:
                list_many2one_fields.append(fld.name)

            # FOR SEARCH AND FILTER
            filters = [('none', _('None')),
                       ('parent_id', _('Manager')),
                       ('coach_id', _('Coach')),
                       ('admin_responsible_id', _('Administration responsible')),
                       ('software_responsible_id', _('Software responsible')), ]
            employees = employee_obj.sudo().search([('is_empty', '=', False)])

            user = request.env.user
            full_path = request.httprequest.full_path
            if ('my/annuaire?search' not in full_path) and (
                    'my/annuaire?new_cumulated_search_list' not in full_path and not filter):
                user.write({'cumulated_search': ''})
                employee_ids = employee_ids

            elif new_cumulated_search_list:

                user.write({'cumulated_search': new_cumulated_search_list})
                list_employee = request.env['hr.employee'].search([('id', '=', False)])
                liste_cumulated_search = new_cumulated_search_list.split(";")
                for c_search in liste_cumulated_search:
                    new_list_employee = request.env['hr.employee'].search(
                        ['|', ('name', 'ilike', c_search), ('work_email', 'ilike', c_search)])
                    final_list = set(list_employee).union(set(new_list_employee))
                    list_employee = final_list
                    employee_ids = list_employee
                values.update({
                    'liste_cumulated_search': liste_cumulated_search,
                    'employees': employee_ids,
                })

            elif search:
                list_employee = request.env['hr.employee'].sudo().search([('id', '=', False)])
                if user.cumulated_search:
                    liste_cumulated_search = user.cumulated_search.split(";")
                    if search not in liste_cumulated_search:
                        user.write({'cumulated_search': user.cumulated_search + ";" + search})
                else:
                    user.write({'cumulated_search': search})
                liste_cumulated_search = user.cumulated_search.split(";")
                for c_search in liste_cumulated_search:
                    new_list_employee = request.env['hr.employee'].search(
                        ['|', ('name', 'ilike', c_search), ('work_email', 'ilike', c_search)])
                    final_list = set(list_employee).union(set(new_list_employee))
                    list_employee = final_list
                    employee_ids = list_employee
                values.update({
                    'liste_cumulated_search': liste_cumulated_search,
                })
            elif filter:
                if filter == 'none':
                    employee_ids = employee_ids
                if filter == 'parent_id':
                    employee_ids = employee_ids.filtered(lambda l: l.id == employe_id.parent_id.id)
                elif filter == 'coach_id':
                    employee_ids = employee_ids.filtered(lambda l: l.id == employe_id.coach_id.id)
                elif filter == 'admin_responsible_id':
                    employee_ids = employee_ids.filtered(lambda l: l.id == employe_id.admin_responsible_id.id)
                elif filter == 'software_responsible_id':
                    employee_ids = employee_ids.filtered(lambda l: l.id == employe_id.software_responsible_id.id)

            elif search and employee_ids:
                for fd_emp in an_fields_employee:
                    search_employees = employee_obj.sudo().search([(fd_emp.fields_id.name, 'ilike', search)])
                    employees = employees + search_employees

                for fd_con in an_fields_contact:
                    search_employees = employee_obj.sudo().search([(fd_con.fields_id.name, 'ilike', search)])
                    employees = employees + search_employees

            elif not search and not filter:
                employee_ids = employee_ids

            employee_manager = employee_obj.sudo().search([('id', '=', employe_id.parent_id.id)])
            employee_coach = employee_obj.sudo().search([('id', '=', employe_id.coach_id.id)])
            employee_ra = employee_obj.sudo().search([('id', '=', employe_id.admin_responsible_id.id)])
            employee_rs = employee_obj.sudo().search([('id', '=', employe_id.software_responsible_id.id)])

            # BODY OF ANNUAIRE

            # CHECKING MANY2ONE TYPE AND ADD ONBOARDING TAG
            if employee_ids:
                all_emp = []
                manager_label = ''
                coach_label = ''
                ra_label = ''
                rs_label = ''
                for employee in employee_ids:
                    info_key = OrderedDict({})
                    # contact_key = {}
                    nbr_logo = 0
                    if employee.id == employee_manager.id:
                        manager_label = 'M'
                    if employee.id == employee_coach.id:
                        coach_label = 'ME'
                    if employee.id == employee_ra.id:
                        ra_label = 'RA'
                    if employee.id == employee_rs.id:
                        rs_label = 'RL'

                    for fd_emp in an_fields_employee:
                        if fd_emp.fields_id.name == "name" or fd_emp.fields_id.name == "work_email" or fd_emp.fields_id.name == "image":
                            pass
                        else:
                            # acc_number
                            if fd_emp.fields_id.ttype == 'many2one':
                                name_field_many2one = fd_emp.fields_id.name
                                if name_field_many2one != 'bank_account_id':
                                    objet = employee.mapped(name_field_many2one).sudo()
                                    if objet.name:
                                        info_key[
                                            fd_emp.fields_id.field_description] = objet.name if objet.name else " "

                                else:
                                    objet = employee.mapped(name_field_many2one)
                                    if objet.acc_number:
                                        info_key[
                                            fd_emp.fields_id.field_description] = objet.acc_number if objet.acc_number else " "

                            else:
                                if getattr(employee, fd_emp.fields_id.name):
                                    info_key[fd_emp.fields_id.field_description] = getattr(employee,
                                                                                           fd_emp.fields_id.name)
                    list_contact_key = []
                    for fd_con in an_fields_contact:
                        contact_key = {}
                        nbr_logo = nbr_logo + 1

                        contact_key['logo' + str(nbr_logo)] = fd_con.logo
                        if fd_con.fields_id.ttype == 'many2one':
                            name_field_many2one = fd_con.fields_id.name
                            if name_field_many2one != 'bank_account_id':
                                objet = employee.mapped(name_field_many2one)
                                contact_key[fd_con.fields_id.field_description] = objet.name if objet.name else " "

                                if objet.name:
                                    list_contact_key.append(contact_key)
                            else:
                                objet = employee.mapped(name_field_many2one)
                                contact_key[
                                    fd_con.fields_id.field_description] = objet.acc_number if objet.acc_number else " "

                                if objet.acc_number:
                                    list_contact_key.append(contact_key)
                        else:
                            if employee and fd_con.fields_id.name:
                                contact_key[fd_con.fields_id.field_description] = getattr(
                                    employee,
                                    fd_con.fields_id.name
                                )
                                if getattr(employee, fd_con.fields_id.name):
                                    list_contact_key.append(contact_key)
                    info_employee = {
                        'employee': employee,
                        'info': OrderedDict(info_key),
                        'list_contact_key': list_contact_key
                    }
                    all_emp.append(info_employee)
                keep = QueryURL('/my/annuaire')

                dict_filter = dict((x, y) for x, y in filters)

                values.update({
                    'employees': all_emp,
                    'filters': filters,
                    'search': search if search else False,
                    'current_filter': dict_filter[filter] if filter else False,
                    'manager': employee_manager,
                    'coach': employee_coach,
                    'ra': employee_ra,
                    'rs': employee_rs,
                    'keep': keep,
                    'p': pages,
                })
            return request.render('ooto_annuaire_front.annuaire_template', values)
        else:
            values.update({'error': _("The user is not registered as an employee")})
