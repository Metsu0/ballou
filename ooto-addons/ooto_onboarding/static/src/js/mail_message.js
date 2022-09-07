odoo.define('ooto_onboarding.mail_message', function(require){
var rpc = require('web.rpc');
console.log('mandeha eh');
return rpc.query({
    model: 'mail.message',
    method: 'archive_mail_10_days_ago',
});
});