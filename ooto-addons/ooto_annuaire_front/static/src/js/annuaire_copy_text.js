odoo.define('ooto_annuaire_front.annuaire_copy_text', function (require) {
    'use strict';
    $(document).ready(function () {
        $(".contact_bloc").dblclick(function () {
            event.stopPropagation();
            var target = $(event.target).closest('div[class="contact_bloc"]').find('.contact_field_value')[0];
            var range = document.createRange();
            range.selectNodeContents(target);
            var sel = window.getSelection();
            sel.removeAllRanges();
            sel.addRange(range);
            document.execCommand('copy');
            $(".copied").show().fadeOut(3000);
        });
    });

});