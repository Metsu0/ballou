# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class HrPayslipConfig(models.Model):
    _name = 'hr.payslip.config'

    date_from = fields.Date('From date', required=True)
    date_to = fields.Date('To date', required=True)
    view_mode = fields.Selection([('simple', 'Simple'), ('detailed', 'Detailed')], default='detailed',
                                 string='View mode')
    payslip_resume_ids = fields.One2many('payslip.resume', 'payslip_config_id', 'Etat de paie')
    payslip_resume_count = fields.Integer('Payslip resume count', compute='_compute_payslip_resume_count')
    company_id = fields.Many2one('res.company', 'Company', required=True)

    def name_get(self):
        result = []
        for conf in self:
            date_start = conf.date_from.strftime('%d/%m/%Y')
            date_to = conf.date_to.strftime('%d/%m/%Y')
            name = _('Etat de paie du %s au %s' % (date_start, date_to))
            result.append((conf.id, name))
        return result

    @api.depends('payslip_resume_ids')
    def _compute_payslip_resume_count(self):
        for rec in self:
            rec.payslip_resume_count = len(rec.payslip_resume_ids)

    @api.onchange('date_from')
    def _onchange_date_from(self):
        if self.date_from and self.date_to and self.date_to < self.date_from:
            self.date_to = self.date_from

    @api.onchange('date_to')
    def _onchange_date_to(self):
        if self.date_to and self.date_to < self.date_from:
            self.date_from = self.date_to

    def generate_payslip_resume(self):
        self.ensure_one()
        self.payslip_resume_ids.unlink()
        domain = [('date_from', '>=', self.date_from), ('date_to', '<=', self.date_to)]
        payslip_obj = self.env['hr.payslip']
        payslips = payslip_obj.sudo().search(domain)
        new_payslips = []

        for payslip in payslips:
            payslip_lines = payslip.mapped('line_ids')
            payslip_input_lines = payslip.mapped('input_line_ids')
            new_payslips.append({
                'payslip_config_id': self.id,
                'payslip_reference': payslip.number,
                'employee_id': payslip.employee_id.id if payslip.employee_id else False,
                'department_id': payslip.employee_id.department_id.id if payslip.employee_id and payslip.employee_id.department_id else False,
                'department_parent_id': payslip.employee_id.department_id.parent_id.id if payslip.employee_id and payslip.employee_id.department_id and payslip.employee_id.department_id.parent_id else False,
                'company_id': payslip.company_id.id,
                'nom_employe': payslip.employee_id.name if payslip.employee_id else False,
                'poste': payslip.employee_id.job_id.name if payslip.employee_id and payslip.employee_id.job_id else '',
                'matricule': payslip.employee_id.registration_number if payslip.employee_id else '',
                'sexe': payslip.employee_id.gender if payslip.employee_id else '',
                'numero_cnaps': payslip.employee_id.cnaps_number if payslip.employee_id else '',
                'numero_cin': payslip.employee_id.identification_id if payslip.employee_id else '',
                'nom_lot_bulletin': payslip.payslip_run_id.name if payslip.payslip_run_id else '',
                'lot_bulletin_id': payslip.payslip_run_id.id if payslip.payslip_run_id else '',
                'payslip_run_id': payslip.payslip_run_id.id if payslip.payslip_run_id else False,
                'code_banque': payslip.employee_id.bank_account_id.bank_id.bic if payslip.employee_id and payslip.employee_id.bank_account_id else '',
                'guichet': payslip.employee_id.bank_account_id.agency_code if payslip.employee_id and payslip.employee_id.bank_account_id else '',
                'numero_compte': payslip.employee_id.bank_account_id.acc_number if payslip.employee_id and payslip.employee_id.bank_account_id else '',
                'banque': payslip.employee_id.bank_account_id.bank_id.name if payslip.employee_id and payslip.employee_id.bank_account_id and payslip.employee_id.bank_account_id.bank_id else '',
                'debut_fiche_bulletin': payslip.date_from,
                'fin_fiche_bulletin': payslip.date_to,
                'mode_paiement': payslip.contract_id.payslip_payment_mode_id.name if payslip.contract_id and payslip.contract_id.payslip_payment_mode_id else '',
                'etat_bulletin': payslip.state,
                # 'test': sum([hpi.amount for hpi in payslip_input_lines.filtered(lambda l: l.code == 'AUG')]),

                'sb': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('BASIC', 'BASIC_SANS_OSTIE', 'BASIC_SANS_OSTIE_SANS_CNAPS'))]),                
                'tj': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('TJ', 'TJ_SANS_OSTIE', 'TJ_SANS_OSTIE_SANS_CNAPS'))]),
                'th': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('TH', 'TH_SANS_OSTIE', 'TH_SANS_OSTIE_SANS_CNAPS'))]),
                'sb_j': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('SB_J', 'SB_J_SANS_OSTIE', 'SB_J_SANS_OSTIE_SANS_CNAPS'))]),
                'avtg_nat': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('AVTG_NAT', 'AVTG_NAT_SANS_OSTIE', 'AVTG_NAT_SANS_OSTIE_SANS_CNAPS'))]),
                'idmt_alg_frs': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('IDMT_ALG_FRS', 'IDMT_ALG_FRS_SANS_OSTIE', 'IDMT_ALG_FRS_SANS_OSTIE_SANS_CNAPS'))]),
                'idmt_logement': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('IDMT_LOGEMENT', 'IDMT_LOGEMENT_SANS_OSTIE', 'IDMT_LOGEMENT_SANS_OSTIE_SANS_OSTIE_SANS_CNAPS'))]),
                'idmt_depl': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('IDMT_DEPL', 'IDMT_DEPL_SANS_OSTIE', 'IDMT_DEPL_SANS_OSTIE_SANS_CNAPS'))]),
                'idmt_diverses': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('IDMT_DIVERSES', 'IDMT_DIVERSES_SANS_OSTIE', 'IDMT_DIVERSES_SANS_OSTIE_SANS_CNAPS'))]),
                'idmt_var_depl': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('IDMT_VAR_DEPL', 'IDMT_VAR_DEPL_SANS_OSTIE', 'IDMT_VAR_DEPL_SANS_OSTIE_SANS_CNAPS'))]),
                'compl_repas': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('COMPL_REPAS', 'COMPL_REPAS_SANS_OSTIE', 'COMPL_REPAS_SANS_OSTIE_SANS_CNAPS'))]),
                'coms': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('COMS', 'COMS_SANS_OSTIE', 'COMS_SANS_OSTIE_SANS_CNAPS'))]),
                'prime_chnt': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('PRIME_CHNT', 'PRIME_CHNT_SANS_OSTIE', 'PRIME_CHNT_SANS_OSTIE_SANS_CNAPS'))]),
                'prime_chnt_air': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('PRIME_CHNT_AIR', 'PRIME_CHNT_AIR_SANS_OSTIE', 'PRIME_CHNT_AIR_SANS_OSTIE_SANS_CNAPS'))]),
                'prime_prod': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('PRIME_PROD', 'PRIME_PROD_SANS_OSTIE', 'PRIME_PROD_SANS_OSTIE_SANS_CNAPS'))]),
                'prime_fct': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('PRIME_FCT', 'PRIME_FCT_SANS_OSTIE', 'PRIME_FCT_SANS_OSTIE_SANS_CNAPS'))]),
                'prime_expt': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('PRIME_EXPT', 'PRIME_EXPT_SANS_OSTIE', 'PRIME_EXPT_SANS_OSTIE_SANS_CNAPS'))]),
                'prime_asdt': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('PRIME_ASDT', 'PRIME_ASDT_SANS_OSTIE', 'PRIME_ASDT_SANS_OSTIE_SANS_CNAPS'))]),
                'prime_rdmnt': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('PRIME_RDMNT', 'PRIME_RDMNT_SANS_OSTIE', 'PRIME_RDMNT_SANS_OSTIE_SANS_CNAPS'))]),
                'prime_cpmnt': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('PRIME_CPMNT', 'PRIME_CPMNT_SANS_OSTIE', 'PRIME_CPMNT_SANS_OSTIE_SANS_CNAPS'))]),
                'primes_diverses': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('PRIMES_DIVERSES', 'PRIMES_DIVERSES_SANS_OSTIE', 'PRIMES_DIVERSES_SANS_OSTIE_SANS_CNAPS'))]),
                'prime_astr': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('PRIME_ASTR', 'PRIME_ASTR_SANS_OSTIE', 'PRIME_ASTR_SANS_OSTIE_SANS_CNAPS'))]),
                'prime_grtf': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('PRIME_GRTF', 'PRIME_GRTF_SANS_OSTIE', 'PRIME_GRTF_SANS_OSTIE_SANS_CNAPS'))]),
                'prime_fin_annee': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('PRIME_FIN_ANNEE', 'PRIME_FIN_ANNEE_SANS_OSTIE', 'PRIME_FIN_ANNEE_SANS_OSTIE_SANS_CNAPS'))]),
                'prime_var_mens': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('PRIME_VAR_MENS', 'PRIME_VAR_MENS_SANS_OSTIE', 'PRIME_VAR_MENS_SANS_OSTIE_SANS_CNAPS'))]),
                'prime_obj_m1': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('PRIME_OBJ_M1', 'PRIME_OBJ_M1_SANS_OSTIE', 'PRIME_OBJ_M1_SANS_OSTIE_SANS_CNAPS'))]),
                'prime_ca_m1': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('PRIME_CA_M1', 'PRIME_CA_M1_SANS_OSTIE', 'PRIME_CA_M1_SANS_OSTIE_SANS_CNAPS'))]),
                'prime_hyg_srv_m1': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('PRIME_HYG_SRV_M1', 'PRIME_HYG_SRV_M1_SANS_OSTIE', 'PRIME_HYG_SRV_M1_SANS_OSTIE_SANS_CNAPS'))]),
                'prime_clo_exr': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('PRIME_CLO_EXR', 'PRIME_CLO_EXR_SANS_OSTIE', 'PRIME_CLO_EXR_SANS_OSTIE_SANS_CNAPS'))]),
                'prime_anciennete': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('PRIME_ANCIENNETE', 'PRIME_ANCIENNETE_SANS_OSTIE', 'PRIME_ANCIENNETE_SANS_OSTIE_SANS_CNAPS'))]),
                'prime_intrs': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('PRIME_INTRS', 'PRIME_INTRS_SANS_OSTIE', 'PRIME_INTRS_SANS_OSTIE_SANS_CNAPS'))]),
                'hs_130': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('HS_130', 'HS_130_SANS_OSTIE', 'HS_130_SANS_OSTIE_SANS_CNAPS'))]),
                'hs_150': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('HS_150', 'HS_150_SANS_OSTIE', 'HS_150_SANS_OSTIE_SANS_CNAPS'))]),
                'hn_30': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('HN_30', 'HN_30_SANS_OSTIE', 'HN_30_SANS_OSTIE_SANS_CNAPS'))]),
                'hn_50': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('HN_50', 'HN_50_SANS_OSTIE', 'HN_50_SANS_OSTIE_SANS_CNAPS'))]),
                'md_40': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('MD_40', 'MD_40_SANS_OSTIE', 'MD_40_SANS_OSTIE_SANS_CNAPS'))]),
                'mf_100': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('MF_100', 'MF_100_SANS_OSTIE', 'MF_100_SANS_OSTIE_SANS_CNAPS'))]),
                'alloc_conge': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('ALLOC_CONGE', 'ALLOC_CONGE_SANS_OSTIE', 'ALLOC_CONGE_SANS_OSTIE_SANS_CNAPS'))]),
                'icc': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('ICC', 'ICC_SANS_OSTIE', 'ICC_SANS_OSTIE_SANS_CNAPS'))]),
                'abs_conge': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('ABS_CONGE', 'ABS_CONGE_SANS_OSTIE', 'ABS_CONGE_SANS_OSTIE_SANS_CNAPS'))]),
                'abs_rem_aut': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('ABS_REM_AUT', 'ABS_REM_AUT_SANS_OSTIE', 'ABS_REM_AUT_SANS_OSTIE_SANS_CNAPS'))]),
                'abs_non_rem': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('ABS_NON_REM', 'ABS_NON_REM_SANS_OSTIE', 'ABS_NON_REM_SANS_OSTIE_SANS_CNAPS'))]),
                'brut': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('BRUT', 'BRUT_SANS_OSTIE', 'SB_TRIAL_PERIOD', 'SB_TRIAL_PERIOD_SANS_CNAPS'))]),
                'cnaps_pat': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('CNAPS_PAT', 'CNAPS_PAT_SANS_OSTIE'))]),
                'cnaps': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('CNAPS', 'CNAPS_SANS_OSTIE'))]),
                'ostie_pat': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code == 'OSTIE_PAT')]),
                'ostie': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code == 'OSTIE')]),
                'rappel_salaire': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('RAPPEL_SALAIRE', 'RAPPEL_SALAIRE_SANS_OSTIE', 'RAPPEL_SALAIRE_SANS_OSTIE_SANS_CNAPS'))]),
                'rappel_alloc_conge': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('RAPPEL_ALLOC_CONGE', 'RAPPEL_ALLOC_CONGE_SANS_OSTIE', 'RAPPEL_ALLOC_CONGE_SANS_OSTIE_SANS_CNAPS'))]),
                'rappel_prime_clo_exr': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('RAPPEL_PRIME_CLO_EXR', 'RAPPEL_PRIME_CLO_EXR_SANS_OSTIE', 'RAPPEL_PRIME_CLO_EXR_SANS_OSTIE_SANS_CNAPS'))]),
                'rappel_prime_fin_annee': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('RAPPEL_PRIME_FIN_ANNEE', 'RAPPEL_PRIME_FIN_ANNEE_SANS_OSTIE', 'RAPPEL_PRIME_FIN_ANNEE_SANS_OSTIE_SANS_CNAPS'))]),
                'rappel_prime_asdt': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('RAPPEL_PRIME_ASDT', 'RAPPEL_PRIME_ASDT_SANS_OSTIE', 'RAPPEL_PRIME_ASDT_SANS_OSTIE_SANS_CNAPS'))]),
                'rappel_prime_prod': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('RAPPEL_PRIME_PROD', 'RAPPEL_PRIME_PROD_SANS_OSTIE', 'RAPPEL_PRIME_PROD_SANS_OSTIE_SANS_CNAPS'))]),
                'rappel_prime_ca_m1': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('RAPPEL_PRIME_CA_M1', 'RAPPEL_PRIME_CA_M1_SANS_OSTIE', 'RAPPEL_PRIME_CA_M1_SANS_OSTIE_SANS_CNAPS'))]),
                'rappel_prime_cpmnt': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('RAPPEL_PRIME_CPMNT', 'RAPPEL_PRIME_CPMNT_SANS_OSTIE', 'RAPPEL_PRIME_CPMNT_SANS_OSTIE_SANS_CNAPS'))]),
                'rappel_prime_expt': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('RAPPEL_PRIME_EXPT', 'RAPPEL_PRIME_EXPT_SANS_OSTIE', 'RAPPEL_PRIME_EXPT_SANS_OSTIE_SANS_CNAPS'))]),
                'rappel_prime_rdmnt': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('RAPPEL_PRIME_RDMNT', 'RAPPEL_PRIME_RDMNT_SANS_OSTIE', 'RAPPEL_PRIME_RDMNT_SANS_OSTIE_SANS_CNAPS'))]),
                'rappel_prime_astr': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('RAPPEL_PRIME_ASTR', 'RAPPEL_PRIME_ASTR_SANS_OSTIE', 'RAPPEL_PRIME_ASTR_SANS_OSTIE_SANS_CNAPS'))]),
                'rappel_prime_anciennete': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('RAPPEL_PRIME_ANCIENNETE', 'RAPPEL_PRIME_ANCIENNETE_SANS_OSTIE', 'RAPPEL_PRIME_ANCIENNETE_SANS_OSTIE_SANS_CNAPS'))]),
                'rappel_prime_fct': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('RAPPEL_PRIME_FCT', 'RAPPEL_PRIME_FCT_SANS_OSTIE', 'RAPPEL_PRIME_FCT_SANS_OSTIE_SANS_CNAPS'))]),
                'rappel_prime_grtf': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('RAPPEL_PRIME_GRTF', 'RAPPEL_PRIME_GRTF_SANS_OSTIE', 'RAPPEL_PRIME_GRTF_SANS_OSTIE_SANS_CNAPS'))]),
                'rappel_prime_chantier': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('RAPPEL_PRIME_CHANTIER', 'RAPPEL_PRIME_CHANTIER_SANS_OSTIE', 'RAPPEL_PRIME_CHANTIER_SANS_OSTIE_SANS_CNAPS'))]),
                'rappel_prime_intrs': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('RAPPEL_PRIME_INTRS', 'RAPPEL_PRIME_INTRS_SANS_OSTIE', 'RAPPEL_PRIME_INTRS_SANS_OSTIE_SANS_CNAPS'))]),
                'rappel_prime_chantier_air': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('RAPPEL_PRIME_CHANTIER_AIR', 'RAPPEL_PRIME_CHANTIER_AIR_SANS_OSTIE', 'RAPPEL_PRIME_CHANTIER_AIR_SANS_OSTIE_SANS_CNAPS'))]),
                'rappel_prime_hyg_srv_m1': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('RAPPEL_PRIME_HYG_SRV_M1', 'RAPPEL_PRIME_HYG_SRV_M1_SANS_OSTIE', 'RAPPEL_PRIME_HYG_SRV_M1_SANS_OSTIE_SANS_CNAPS'))]),
                'rappel_prime_obj_m1': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('RAPPEL_PRIME_OBJ_M1', 'RAPPEL_PRIME_OBJ_M1_SANS_OSTIE', 'RAPPEL_PRIME_OBJ_M1_SANS_OSTIE_SANS_CNAPS'))]),
                'rappel_prime_var_mens': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('RAPPEL_PRIME_VAR_MENS', 'RAPPEL_PRIME_VAR_MENS_SANS_OSTIE', 'RAPPEL_PRIME_VAR_MENS_SANS_OSTIE_SANS_CNAPS'))]),
                'rappel_primes_diverses': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('RAPPEL_PRIMES_DIVERSES', 'RAPPEL_PRIMES_DIVERSES_SANS_OSTIE', 'RAPPEL_PRIMES_DIVERSES_SANS_OSTIE_SANS_CNAPS'))]),
                'mi': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('MI_HSE_20', 'MI_HSE_20_SANS_OSTIE', 'MI_HSE_20_SANS_OSTIE_SANS_CNAPS'))]),
                'irsa': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('IRSA', 'IRSA_SANS_OSTIE', 'IRSA_SANS_OSTIE_SANS_CNAPS'))]),
                'avc_quinzaine': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('AVC_QUINZAINE', 'AVC_QUINZAINE_SANS_OSTIE', 'AVC_QUINZAINE_SANS_OSTIE_SANS_CNAPS'))]),
                'avc_spec': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('AVC_SPEC', 'AVC_SPEC_SANS_OSTIE', 'AVC_SPEC_SANS_OSTIE_SANS_CNAPS'))]),
                'alloc_fam': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('ALLOC_FAM', 'ALLOC_FAM_SANS_OSTIE', 'ALLOC_FAM_SANS_OSTIE_SANS_CNAPS'))]),
                'sal_net': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('NET', 'NET_SANS_OSTIE', 'SAL_NET_TRIAL_PERIOD', 'SAL_JOURNALIER', 'NET_SANS_OSTIE_SANS_CNAPS'))]),

                'fmfp': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('FMFP', 'FMFP_SANS_OSTIE', 'FMFP_SANS_OSTIE_SANS_CNAPS'))]),

                'avance_scolaire': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('AVC_SCO', 'AVC_SCO_SANS_OSTIE', 'AVC_SCO_SANS_OSTIE_SANS_CNAPS'))]),
                'prime_rappel_risque': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('RAPPEL_PRIME_RISK', 'RAPPEL_PRIME_RISK_SANS_OSTIE', 'RAPPEL_PRIME_RISK_SANS_OSTIE_SANS_CNAPS'))]),
                'indemnite_preavis': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('IDMT_PREAVIS', 'IDMT_PREAVIS_SANS_OSTIE', 'IDMT_PREAVIS_SANS_OSTIE_SANS_CNAPS'))]),
                'demi_salaire_maternite': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('DEMI_SAL_MAT', 'DEMI_SAL_MAT_SANS_OSTIE', 'DEMI_SAL_MAT_SANS_OSTIE_SANS_CNAPS'))]),
                'absence_pour_conge_maternite': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('ABS_MAT', 'ABS_MAT_SANS_OSTIE', 'ABS_MAT_SANS_OSTIE_SANS_CNAPS'))]),
                'prime_de_risque': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('PRIME_RISK', 'PRIME_RISK_SANS_OSTIE', 'PRIME_RISK_SANS_OSTIE_SANS_CNAPS'))]), 
                'indmt_stage': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code == 'INDMT_STAGE')]), 
                
                'commission_sur_vente': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('COMS_VENTE', 'COMS_VENTE_SANS_OSTIE', 'COMS_VENTE_SANS_OSTIE_SANS_CNAPS'))]), 
                'ded_enfant_a_charge': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('DED_ENFANT', 'DED_ENFANT_SANS_OSTIE', 'DED_ENFANT_SANS_OSTIE_SANS_CNAPS'))]), 
                'indemnite_de_licenciement': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('IDMT_LICEN', 'IDMT_LICEN_SANS_OSTIE', 'IDMT_LICEN_SANS_OSTIE_SANS_CNAPS'))]), 
                'indemnite_de_logement_non_imposable': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('IDMT_LOG_NI', 'IDMT_LOG_NI_SANS_OSTIE', 'IDMT_LOG_NI_SANS_OSTIE_SANS_CNAPS'))]), 
                'irsa_brut': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('IRSA_BRUT', 'IRSA_BRUT_SANS_OSTIE', 'IRSA_BRUT_SANS_OSTIE_SANS_CNAPS'))]), 
                'mise_a_pied': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('MAP', 'MAP_SANS_OSTIE', 'MAP_SANS_OSTIE_SANS_CNAPS'))]), 
                'preavis_non_effectue': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('PREAVIS_NE', 'PREAVIS_NE_SANS_OSTIE', 'PREAVIS_NE_SANS_OSTIE_SANS_CNAPS'))]), 
                'prime_de_depart': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('PRIME_DEP', 'PRIME_DEP_SANS_OSTIE', 'PRIME_DEP_SANS_OSTIE_SANS_CNAPS'))]), 
                'prime_de_retraite': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('PRIME_RET', 'PRIME_RET_SANS_OSTIE', 'PRIME_RET_SANS_OSTIE_SANS_CNAPS'))]), 
                'prime_d_interessement': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('PRIME_INTER', 'PRIME_INTER_SANS_OSTIE', 'PRIME_INTER_SANS_OSTIE_SANS_CNAPS'))]), 
                'prime_interessement': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('PRIME_INTRS', 'PRIME_INTRS_SANS_OSTIE', 'PRIME_INTRS_SANS_OSTIE_SANS_CNAPS'))]), 
                'rappel': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('RAPPEL_SALAIRE', 'RAPPEL_SALAIRE_SANS_OSTIE', 'RAPPEL_SALAIRE_SANS_OSTIE_SANS_CNAPS'))]), 
                'regul_cnaps': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('REGUL_CNAPS', 'REGUL_CNAPS_SANS_OSTIE'))]), 
                'regul_ostie': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code == 'REGUL_SMIE')]), 
                'retraite_complementaire': sum([hpl.total for hpl in payslip_lines.filtered(lambda l: l.code in ('RET_COMP', 'RET_COMP_SANS_OSTIE', 'RET_COMP_SANS_OSTIE_SANS_CNAPS'))]), 
            })
 
        if new_payslips:
            self.env['payslip.resume'].create(new_payslips)

    def view_payslip_resume(self):
        self.ensure_one()
        graph_view_id = self.env.ref('ballou_hr_payroll.payslip_resume_view_graph2').id
        tree_view_id = self.env.ref('ballou_hr_payroll.simple_payslip_resume_view_tree2').id
        if self.view_mode == 'detailed':
            tree_view_id = self.env.ref('ballou_hr_payroll.detailed_payslip_resume_view_tree2').id
        return {
            'name': 'Simple' if self.view_mode == 'simple' else _('Detailed'),
            'view_mode': 'tree, graph',
            'res_model': 'payslip.resume',
            'view_id': False,
            'views': [
                (tree_view_id, 'tree'),
                (graph_view_id, 'graph')
            ],
            'type': 'ir.actions.act_window',
            'nodestroy': False,
            'target': 'current',
            'domain': [('payslip_config_id', '=', self.id)]
        }
