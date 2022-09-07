odoo.define('ooto_annuaire_front.annuaire_search', function (require) {
    'use strict';
    var rpc = require('web.rpc');

    $("button[id^='to_delete']").click(function () {
        var to_delete = $(this).attr("id").split('-')[1];
        rpc.query({
            model: 'res.users',
            method: "update_cumulated_search_list",
            args: [['to_delete'], to_delete],
        })
            .then(function (result) {
                var add_class = 'to_delete-' + to_delete;
                $("div[class='" + add_class + "']").remove();
                var url = '/my/annuaire?new_cumulated_search_list=' + result;
                document.location = url;

            });
    });
});