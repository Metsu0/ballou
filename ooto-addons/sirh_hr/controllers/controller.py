# coding: utf-8

from odoo import http
from odoo.http import request

from odoo.addons.portal.controllers.portal import pager as portal_pager


class ContractController(http.Controller):
    @http.route(['/my/contract', '/my/contract/page/<int:page>'], type="http", auth="public", website=True)
    def my_contract(self, page=1, search=None):
        """
        Controller to return list of contract in frontend
        :return: contract
        """
        # Variable initialization
        employe_id = request.env.user.partner_id.employee_id
        values = {}
        domain = [('employee_id', '=', employe_id.id)]
        # Set pager
        contract_count = request.env['hr.contract'].sudo().search_count(domain)
        pager = portal_pager(
            url="/my/contract",
            total=contract_count,
            page=page,
            step=10,
            url_args={'filter': filter, 'search': search},
        )
        contract_ids = request.env['hr.contract'].sudo().search(domain, limit=10, offset=pager['offset'], order='state desc')
        # update "values"
        values.update({
            'contract_ids': contract_ids.sorted(key=lambda r: r.state, reverse=True),
            'employee_id': employe_id,
            'pager': pager,
        })
        return request.render('sirh_hr.contract_template', values)

    @http.route('/print_contract', methods=['POST', 'GET'], csrf=False, type='http', auth="user", website=True)
    def print_contract(self, id=None, **kwargs):
        """
        Print contract
        :param id: id of contract to print
        :param kwargs:
        :return:
        """
        contract_id = request.env['hr.contract'].sudo().browse(int(id))
        if contract_id and contract_id.sudo().employee_id.user_id == request.env.user:
            report_action = http.request.env.ref('sirh_hr.action_report_contract').sudo()
            pdf_content, __ = report_action.render_qweb_pdf(contract_id.id)
            pdfhttpheaders = [
                ('Content-Type', 'application/pdf'),
                ('Content-Length', len(pdf_content)),
                ('Content-Disposition', 'attachment; filename=' + "%s.pdf;" % (contract_id.name))
            ]
            return request.make_response(pdf_content, headers=pdfhttpheaders)
        else:
            return request.redirect('/my/contract')
