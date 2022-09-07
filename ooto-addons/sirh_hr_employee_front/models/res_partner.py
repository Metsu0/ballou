# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

PARTNER_EMPLOYEE_FIELDS_MAP = {
	'marital_status': 'marital',
	'gender': 'gender',
	'visa_expire': 'visa_expire',
	'birthday': 'birthday'

}


class ResPartner(models.Model):
	_inherit = 'res.partner'

	function_emp = fields.Many2one('hr.job', related='employee_id.job_id', readonly=False)
	work_phone = fields.Char(_('Work phone'), related='employee_id.work_phone', readonly=False)
	gender = fields.Selection([
		(_('male'), _('Male')),
		(_('female'), _('Female')),
		(_('other'), _('Other'))
	], groups="hr.group_hr_user", default="male", related="employee_id.gender")
	birthday = fields.Date(related='employee_id.birthday')
	# Fields of Group Marital status
	marital_status = fields.Selection([
		(_('single'), _('Single')),
		(_('divorced'), _('Divorced')),
		(_('married'), _('Attached')),
		(_('pacs'), _('PACS')),
		(_('widower'), _('Widower'))
	], string=_('Marital Status'), default='single', related='employee_id.marital')

	identification_id = fields.Char(related='employee_id.identification_id')

	@api.model
	def check_and_create_employee(self):
		"""
		This function is used to check all the partner who haven't yet employee. And create the employee
		"""
		partners = self.env['res.partner'].search([('employee_id', '=', False)])

		# Create employee for each "partner"
		for partner in partners:
			employee_vals = partner._prepare_new_employee_value_for_import_partner(partner)
			employee = self.env['hr.employee'].create(employee_vals)
			partner.write({'employee_id': employee.id})

	@api.onchange('birthday')
	def onchange_birthday(self):
		for res in self:
			res.employee_id.birthday = res.birthday

	def _prepare_new_empl_vals(self, values):
		employee_vals = {
			'name': values.get('name'),
			'address_home_id': self.id,
			'address_id': values.get('id'),
			'work_email': values.get('email'),
			'work_phone': values.get('work_phone'),
			'mobile_phone': values.get('phone'),
			'identification_id': values.get('identification_id'),
			'gender': values.get('gender'),
			'department_id': values.get('service'),
			'job_id': values.get('function_emp'),
			'resource_calendar_id': values.get('contract_type', 1)
		}
		return employee_vals

	def _prepare_new_employee_value_for_import_partner(self, partner):
		employee_vals = {
			'name': partner.name,
			'address_home_id': partner.id,
			'address_id': partner.id,
			'work_email': partner.email,
			'work_phone': partner.phone,
			'mobile_phone': partner.mobile,
			'identification_id': partner.identification_id.id if partner.identification_id else False,
			'gender': partner.gender,
			'job_id': partner.function.id if partner.function else False,
			'resource_calendar_id': partner.contract_type.id if partner.contract_type else self.env.user.sudo().company_id.resource_calendar_id.id
		}
		return employee_vals

	def write(self, vals):
		# Create dde only if write not from_demande_validation
		res = super(ResPartner, self).write(vals)
		for rec in self:
			if rec._context.get('from_portal'):

				#     # Write corresponding fields in employee side if changed in partner
				if rec.employee_id:
					empl_vals = {}
					for k in list(PARTNER_EMPLOYEE_FIELDS_MAP.keys()):
						if k in vals:
							empl_vals.update({PARTNER_EMPLOYEE_FIELDS_MAP[k]: vals.get(k)})
					if rec.user_ids:
						user = rec.user_ids[0]
						empl_vals['user_id'] = user.id
					empl_vals['user_partner_id'] = self.id
					if empl_vals:
						rec.employee_id.write(empl_vals)
		return res
