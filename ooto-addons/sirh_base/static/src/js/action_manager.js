odoo.define('sirh_base.action', function (require) {
    "use strict";
    var ActionManager = require('web.ActionManager');

    ActionManager.include({
        doAction: function (action, options) {
            if (typeof (action) === 'object' && 'clear_breadcrumb' in action) {
                options['clear_breadcrumbs'] = action['clear_breadcrumb'];
            }
            return this._super(action, options);
        },
    });
});