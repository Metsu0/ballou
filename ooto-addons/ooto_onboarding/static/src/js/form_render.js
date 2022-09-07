odoo.define('ooto_onboarding.FormRenderer', function (require) {
    "use strict";

    var formRenderer = require('web.FormRenderer');

    formRenderer.include({

        /**
         * Inherit _addOnClickAction method to add action of _o_valid_option button
         * @param $el
         * @param node
         * @private
         */
        _addOnClickAction: function ($el, node) {
            var self = this;
            $el.click(function () {
                if (node.attrs.name === 'valid_option') {
                    // Variable init
                    console.log(self)
                    var vals = self.state.context.create_vals;
                    var options = self.state.data;
                    var ctx = self.state.context;
                    // Call do_option_validation method
                    var res = self._rpc({
                        model: 'employee.option',
                        method: 'do_option_validation',
                        args: [vals, options],
                        context: ctx
                    }).then(function (res_id) {
                        self.do_action({
                            type: 'ir.actions.act_window',
                            views: [[false, 'form']],
                            res_model: 'hr.employee',
                            res_id: res_id,
                            target: 'current',
                            view_type: 'form',
                            context: ctx
                        })
                    });
                }
                else if (node.attrs.name === 'edit_mail'){
                    self.do_action({
                        type: 'ir.actions.act_window',
                        views: [[false, 'form']],
                        res_model: 'mail.compose.message',
                        view_type: 'form',
                        target: 'new',
//                        args: [record],
//                        context: context
                    })
                }
                else {
                    self.trigger_up('button_clicked', {
                        attrs: node.attrs,
                        record: self.state,
                    });
                }
            });
        },
    });
});