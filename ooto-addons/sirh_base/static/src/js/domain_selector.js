odoo.define('sirh_base.domain_selector', function (require) {
    "use strict";

    var DomainSelector = require('web.DomainSelector');

    // by Lanto R.
    DomainSelector.include({
        _onAddFirstButtonClick: function () {
            this._addChild(this.options.default || [["id", "=", '1']]);
        }
    });

});