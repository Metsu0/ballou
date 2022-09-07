odoo.define('ooto_onboarding.sign', function (require) {
    'use strict';

    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var Widget = require('web.Widget');
    var document_signing = require('sign.document_signing');
    var _t = core._t;

    var NoPubThankYouDialog = document_signing.ThankYouDialog.extend({
        template: "sign.no_pub_thank_you_dialog",
    });

    document_signing.SignableDocument.include({
        get_thankyoudialog_class: function () {
            return NoPubThankYouDialog;
        }
    })


});