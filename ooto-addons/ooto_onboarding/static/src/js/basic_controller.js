odoo.define("ooto_onboarding.BasicController", function(require){
'user strict';
console.log('Kanban controller ready');

var BasicController = require('web.BasicController');
var Dialog = require('web.Dialog');
var core = require('web.core');

var _t = core._t;

var BasicController = BasicController.include(
{
canBeDiscarded: function (recordID) {
        var self = this;
        if (!this.isDirty(recordID) || this.modelName == 'hr.employee') {
            return Promise.resolve(false);
        }

        var message = _t("The record has been modified, your changes will be discarded. Do you want to proceed?");
        var def;
        def = new Promise(function (resolve, reject) {
            var dialog = Dialog.confirm(self, message, {
                title: _t("Warning"),
                confirm_callback: resolve.bind(self, true),
                cancel_callback: reject,
            });
            dialog.on('closed', def, reject);
        });
        return def;
    },
});
return BasicController;

});