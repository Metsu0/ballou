odoo.define('dynamic_bypass_rule.action_manager', function (require) {
    "use strict";
    var ActionManager = require('web.ActionManager');
    var core = require('web.core');
    var QWeb = core.qweb;
    var rpc = require('web.rpc');
    var _t = core._t;

    ActionManager.include({
        _handleAction: function (action, options) {
            action.context.model = action.res_model;
            return this._super.apply(this, arguments);
        },
    });
});
