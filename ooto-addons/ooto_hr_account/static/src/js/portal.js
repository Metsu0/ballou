odoo.define('ooto_hr_account.portal', function(require) {
    'use strict';
    var ajax = require('web.ajax');
    var rpc = require('web.rpc');
    require('web.dom_ready');

    jQuery(window).resize(function() {
        if (jQuery(window).width() < 767) {
            $("body.formulaire_page .o_affix_enabled .mobile-toggle").after('<a href=\"/my/account\" class=\"bouton_retour mobile\">Retour</a>');
        }
    });

    $(document).ready(function() {
        //new code regarde si un champ a été modifié et
        var map = new Map();
        var editedFields = [];

        $('#employee_information_form input,#employee_information_form select,#employee_information_form input,#employee_information_form input').each(function() {
            map.set($(this).attr('name'), $(this).val());
            //console.log(map);
        });

        $("#employee_information_form input,#employee_information_form select,#employee_information_form input,#employee_information_form input").on("change", function() {
            var field_val = $(this).val();
            var field_name = $(this).attr('name');
            if (field_val !== map.get(field_name)) {
                editedFields.push(field_name);
            } else {
                editedFields.splice(editedFields.indexOf(field_name));
            }
            if (editedFields.length > 0) {
                //console.log('show button');
                $('#save-changes').show();
            } else {
                //console.log('tsy miseho');
                $('#save-changes').hide();
            }
        });

        //fin new code

        $('.custom_datetimepicker_account').datetimepicker({locale:'fr', format: 'YYYY-MM-DD HH:mm'});

//        $('.o_portal.container').hide();

        //OTO-3022
        $('.o_portal_submenu.breadcrumb').parent().parent().parent().addClass("breadcrumb_portal_shop");
        //fin OTO-3022

        $('.avatar-edit').on('click', function() {
            $('#avatar_user').trigger('click');
        });

        if ($('div').hasClass('content-top_profil')) {
            $('#wrap').addClass('pt0account');
        }

        if ($('div').hasClass('formulaire_banner')) {
            $('main').addClass('formulaire_page');
            $('body').addClass('formulaire_page');
        }

        if (jQuery(window).width() < 767) {
            $("body.formulaire_page .o_affix_enabled .mobile-toggle").after('<a href=\"/my/account\" class=\"bouton_retour mobile\">Retour</a>');
        }

        new Skroll({ mobile: true }).add(".animationblockeffect", {
                animation: "spinIn",
                delay: 300,
                duration: 500,
                easing: "cubic-bezier(0.37, 0.27, 0.24, 1.26)"
            })
            /*.add(".dropdown_list_dashboard_ensemble_liste", {
                animation: "fadeInDown",
                delay: 2100,
                duration: 150,
                triggerBottom: .98,
                easing: "cubic-bezier(0.37, 0.27, 0.24, 1.26)"
            })*/.init();





        $(':file#avatar_user').on('change', function() {
            if ($(this)[0].value) {
                console.log('Changement avatar front');
                var filereader = new FileReader();
                var file_info = $(this)[0].files[0];
                var $img_src = $(this).siblings('img');
                filereader.readAsDataURL(file_info);
                filereader.onloadend = function(upload) {
                    var new_src_val = upload.srcElement.result;
                    var bin_img = new_src_val.split(',')[1];
                    ajax.jsonRpc('/user/change_user_avatar', 'call', { 'image_bin': bin_img }).then(function(data) {
                        $img_src.attr('src', new_src_val);
                        $('#user_avatar_desktop').attr('src', new_src_val)
                    }).guardedCatch(function(err, data) {
                        console.log('ERROR :' + err);
                        console.log('DATA :' + data);
                    })
                }
            }
        });

        //date picker
        $.datepicker.regional['fr'] = {
            clearText: 'Effacer',
            clearStatus: '',
            closeText: 'Fermer',
            closeStatus: 'Fermer sans modifier',
            prevText: '<Préc',
            prevStatus: 'Voir le mois précédent',
            nextText: 'Suiv>',
            nextStatus: 'Voir le mois suivant',
            currentText: 'Courant',
            currentStatus: 'Voir le mois courant',
            monthNames: ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'
            ],
            monthNamesShort: ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun',
                'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc'
            ],
            monthStatus: 'Voir un autre mois',
            yearStatus: 'Voir un autre année',
            weekHeader: 'Sm',
            weekStatus: '',
            dayNames: ['Dimanche', 'Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi'],
            dayNamesShort: ['Dim', 'Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam'],
            dayNamesMin: ['Di', 'Lu', 'Ma', 'Me', 'Je', 'Ve', 'Sa'],
            dayStatus: 'Utiliser DD comme premier jour de la semaine',
            dateStatus: 'Choisir le DD, MM d',
            dateFormat: 'yy-mm-dd',
            firstDay: 0,
            initStatus: 'Choisir la date',
            isRTL: false
        };
        $.datepicker.setDefaults($.datepicker.regional['fr']);
        $(".datepicker").datepicker({
            dateFormat: "yy-mm-dd",
        });

        $('.upload_dynamic').prev().change(function() {
            var input = $(this)
            var file = input[0].files[0],
                reader = new FileReader();
            var input_name = this.name;

            reader.onloadend = function() {
                var b64 = reader.result.replace(/^data:.+;base64,/, '');
                //                rpc.query({
                //                    model: 'hr.employee',
                //                    method: 'upload_file_dynamic',
                //                    args: [this, input_name, file.name, b64],
                //                }).then(function () {
                //                    alert('Loaded File')
                //                })
                ajax.jsonRpc('/user/upload_file_dynamic', 'call', { 'input_name': input_name, 'file_name': file.name, 'file': b64 }).then(function(data) {
                    alert('Loaded File');
                }).guardedCatch(function(err, data) {
                    console.log('ERROR :' + err);
                    console.log('DATA :' + data);
                })
            };
            reader.readAsDataURL(file);
        })
        var isValid;
        console.log($("input").length)


    });
});