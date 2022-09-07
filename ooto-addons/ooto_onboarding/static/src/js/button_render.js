odoo.define('ooto_onboarding.pass_button', function (require) {
    "use strict";

    var core = require('web.core');
    var ajax = require('web.ajax');
    var KanbanController = require('web.KanbanController');
    var Dialog = require('web.Dialog');
    var web_client = require('web.web_client');

    var _t = core._t;
    var _lt = core._lt;
    var QWeb = core.qweb;

    KanbanController.include({
        renderButtons: function ($node) {
            this._super($node);
            var self = this;
            if (this.initialState.context && this.initialState.context.is_create_child_task === true) {
                if (self && self.$buttons && self.modelName === 'hr.onboarding.task' && self.renderer.state.context.is_create_child_task === true) {
                    $(self.$buttons).find('.o_kanban_custom_button').on('click', function (result) {
//                        var action = {
//                            name: _t('Send mail'),
//                            type: 'ir.actions.act_window',
//                            res_model: 'mail.mass_mailing',
//                            view_mode: 'form',
//                            view_type: 'form',
//                            views: [[false, 'form']],
//                            target: 'current',
//                            context: {
//                                'default_name': _t('Password initialization'),
//                                'default_mailing_model_id': self.renderer.state.context.mailing_model_id,
//                                'default_mailing_domain': [["email", "=", self.renderer.state.context.current_employee_email]],
//                                'employee_mail': self.renderer.state.context.current_employee_email,
//                                // 'default_body_html': self.renderer.state.context.mailing_body_html,
//                            }
//                        };
//                        self.do_action(action)
                    self._rpc({
                        model: 'hr.onboarding',
                        method: 'action_invitation_send',
                        args: [self.renderer.state.context.onboarding_id],
                    }).then(function (action_send){
                        self.do_action(action_send);
                        });
                    });
                }
            } else {
                $(self.$buttons).find('.o_kanban_custom_button').hide();
            }
        },
    })
});