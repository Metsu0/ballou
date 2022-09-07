# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    preavis = fields.Float(string="Préavis", compute="_get_preavis")

    def _get_preavis(self):
        contract = self.env['hr.contract'].search([('employee_id', '=', self.id), ('state', '=', 'open')])
        preavis = 0
        if contract:
            days = (fields.datetime.now().date() - contract.date_start).days
            if days < 8:
                i = contract.group_id
                if contract.group_id.id == self.env.ref('ballou_contract_category.group1').id:
                    preavis = 1
                elif contract.group_id.id == self.env.ref('ballou_contract_category.group2').id:
                    preavis = 2
                elif contract.group_id.id == self.env.ref('ballou_contract_category.group3').id:
                    preavis = 3
                elif contract.group_id.id == self.env.ref('ballou_contract_category.group4').id:
                    preavis = 4
                elif contract.group_id.id == self.env.ref('ballou_contract_category.group5').id:
                    preavis = 5

            elif (days >= 8) and (days < 90):
                if contract.group_id.id == self.env.ref('ballou_contract_category.group1').id:
                    preavis = 3
                elif contract.group_id.id == self.env.ref('ballou_contract_category.group2').id:
                    preavis = 8
                elif contract.group_id.id == self.env.ref('ballou_contract_category.group3').id:
                    preavis = 15
                elif contract.group_id.id == self.env.ref('ballou_contract_category.group4').id:
                    preavis = 30
                elif contract.group_id.id == self.env.ref('ballou_contract_category.group5').id:
                    preavis = 30

            elif (days >= 90) and (days < 365):
                if contract.group_id.id == self.env.ref('ballou_contract_category.group1').id:
                    preavis = 8
                elif contract.group_id.id == self.env.ref('ballou_contract_category.group2').id:
                    preavis = 15
                elif contract.group_id.id == self.env.ref('ballou_contract_category.group3').id:
                    preavis = 30
                elif contract.group_id.id == self.env.ref('ballou_contract_category.group4').id:
                    preavis = 45
                elif contract.group_id.id == self.env.ref('ballou_contract_category.group5').id:
                    preavis = 90

            elif (days >= 365) and (days < 1095):
                if contract.group_id.id == self.env.ref('ballou_contract_category.group1').id:
                    preavis = 10
                elif contract.group_id.id == self.env.ref('ballou_contract_category.group2').id:
                    preavis = 30
                elif contract.group_id.id == self.env.ref('ballou_contract_category.group3').id:
                    preavis = 45
                elif contract.group_id.id == self.env.ref('ballou_contract_category.group4').id:
                    preavis = 76
                elif contract.group_id.id == self.env.ref('ballou_contract_category.group5').id:
                    preavis = 121

            elif (days >= 1095) and (days < 1825):
                if contract.group_id.id == self.env.ref('ballou_contract_category.group1').id:
                    preavis = 10 + (2*self.years)
                elif contract.group_id.id == self.env.ref('ballou_contract_category.group2').id:
                    preavis = 30 + (2*self.years)
                elif contract.group_id.id == self.env.ref('ballou_contract_category.group3').id:
                    preavis = 45 + (2*self.years)
                elif contract.group_id.id == self.env.ref('ballou_contract_category.group4').id:
                    preavis = 76 + (2*self.years)
                elif contract.group_id.id == self.env.ref('ballou_contract_category.group5').id:
                    preavis = 121 + (2*self.years)

            elif days >= 1825:
                if contract.group_id.id == self.env.ref('ballou_contract_category.group1').id:
                    preavis = 30
                elif contract.group_id.id == self.env.ref('ballou_contract_category.group2').id:
                    preavis = 45
                elif contract.group_id.id == self.env.ref('ballou_contract_category.group3').id:
                    preavis = 60
                elif contract.group_id.id == self.env.ref('ballou_contract_category.group4').id:
                    preavis = 90
                elif contract.group_id.id == self.env.ref('ballou_contract_category.group5').id:
                    preavis = 180

        self.preavis = preavis

