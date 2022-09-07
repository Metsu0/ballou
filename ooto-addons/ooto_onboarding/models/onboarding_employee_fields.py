# -*- coding: utf-8 -*-

import base64
from odoo import models, fields, api, modules, tools, _


class OnboardingEmployeeFieldsDocument(models.Model):
	_name = 'onboarding.employee.fields.document'
	_description = 'Creation fields dynamic task'

	fields_id = fields.Many2one('ir.model.fields', string="Field name",
										 domain="[('model', '=', 'hr.employee'), ('can_not_be_modified_by_employee', '=', False),('store', '=', True), ('ttype', 'not in', ['binary', 'many2many', 'one2many', 'reference']), ('name', 'not like', 'x_filename_of_')]")

	# employees_fields = fields.Many2one('onboarding.employee.section.fields', string="Section employee", ondelete="cascade")

	def _default_onboarding_task(self):
		return self.env['hr.onboarding.task'].browse(self._context.get('active_id'))

	onboarding_task = fields.Many2one('hr.onboarding.task', string="Employee Fields",
									  default=_default_onboarding_task, ondelete="cascade")
	is_visible_front_employee = fields.Boolean(string="Visible front", default=True)

	employee_ids = fields.Many2many('hr.employee', 'employee_fields_document_onboarding_rel', 'onb_emp_fields_id', 'emp_id',
									string="Employee Fields")

	@api.model
	def create(self, vals):
		res = super(OnboardingEmployeeFieldsDocument, self).create(vals)
		onboarding_task = self.env['hr.onboarding.task'].search([('id', '=', vals['onboarding_task'])])
		onboarding = onboarding_task.onboarding_id if onboarding_task.onboarding_id else self.env['hr.onboarding'].browse(self._context.get('onboarding_id'))
		emp = onboarding.employee_id
		if onboarding_task and emp and not onboarding_task.parent_id:
			res.employee_ids = [(4, emp.id, 0)]
		return res


class OnboardingEmployeeFieldsUpload(models.Model):
	_name = 'onboarding.employee.fields.upload'
	_description = 'Creation fields dynamic task'

	fields_id = fields.Many2one('ir.model.fields', string="Field name",
										 domain="[('model', '=', 'hr.employee'), ('can_not_be_modified_by_employee', '=', False), ('store', '=', True), ('ttype', '=', 'binary')]")

	def _default_onboarding_task(self):
		return self.env['hr.onboarding.task'].browse(self._context.get('active_id'))

	onboarding_task = fields.Many2one('hr.onboarding.task', string="Employee Fields",
									  default=_default_onboarding_task, ondelete="cascade")
	is_visible_front_employee = fields.Boolean(string="Visible front", default=True)

	employee_ids = fields.Many2many('hr.employee', 'employee_fields_uploads_onboarding_rel', 'onb_emp_fields_id', 'emp_id',
									string="Employee Fields")

	@api.model
	def create(self, vals):
		res = super(OnboardingEmployeeFieldsUpload, self).create(vals)
		onboarding_task = self.env['hr.onboarding.task'].search([('id', '=', vals['onboarding_task'])])
		onboarding = onboarding_task.onboarding_id if onboarding_task.onboarding_id else self.env['hr.onboarding'].browse(self._context.get('onboarding_id'))
		emp = onboarding.employee_id
		if onboarding_task and emp and not onboarding_task.parent_id:
			res.employee_ids = [(4, emp.id, 0)]
		return res
