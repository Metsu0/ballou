odoo.define('ooto_annuaire_front.annuaire_tuto', function (require) {
    'use strict';

    var rpc = require('web.rpc');

    $(document).ready(function () {
        // On click of tutorial button
        $('.annuaire-tutorial-btn').click(() => show_tuto('annuaire.tuto', 'get_annuaire_tuto_pages'));

        // Check if first connexion
        if (window.location.href.includes('/my/annuaire')) {
            rpc.query({
                model: 'res.users',
                method: 'get_is_connected_front',
                args: []
            }, []).then(res => {
                if (!res) {
                        show_tuto('annuaire.tuto', 'get_annuaire_tuto_pages');
                    rpc.query({
                        model: 'res.users',
                        method: 'set_is_connected_front',
                        args: [true]
                    }, [])
                }
            });
        }
    });
});