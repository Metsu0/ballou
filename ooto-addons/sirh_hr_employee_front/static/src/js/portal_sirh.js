odoo.define('sirh_hr_employee_front.portal', function (require) {
    'use strict';
     var ajax = require('web.ajax');
     require('web.dom_ready');

     $(document).ready(function () {
//        $('.o_portal.container').hide();
        $('.tab-pane.fade.portal_oto').hide();
//
//         $('.avatar-edit').on('click', function() {
//            $('#avatar_user').trigger('click');
//        })
//
//        $(':file#avatar_user').on('change', function () {
//            if ($(this)[0].value) {
//                console.log('Changement avatar front');
//                var filereader = new FileReader();
//                var file_info = $(this)[0].files[0];
//                var $img_src = $(this).siblings('img');
//                filereader.readAsDataURL(file_info);
//                filereader.onloadend = function (upload) {
//                    var new_src_val = upload.srcElement.result;
//                    var bin_img = new_src_val.split(',')[1];
//                    ajax.jsonRpc('/user/change_user_avatar', 'call', {'image_bin': bin_img}).then(function (data){
//                        $img_src.attr('src', new_src_val);
//                        $('#user_avatar_desktop').attr('src',new_src_val)
//                    }).guardedCatch(function (err, data) {
//                        console.log('ERROR :' + err);
//                        console.log('DATA :' + data);
//                    })
//                }
//            }
//        });

        //date picker
		$.datepicker.regional['fr'] = {
			clearText : 'Effacer',
			clearStatus : '',
			closeText : 'Fermer',
			closeStatus : 'Fermer sans modifier',
			prevText : '<Préc',
			prevStatus : 'Voir le mois précédent',
			nextText : 'Suiv>',
			nextStatus : 'Voir le mois suivant',
			currentText : 'Courant',
			currentStatus : 'Voir le mois courant',
			monthNames : [ 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
				'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre' ],
			monthNamesShort : [ 'Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun',
				'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc' ],
			monthStatus : 'Voir un autre mois',
			yearStatus : 'Voir un autre année',
			weekHeader : 'Sm',
			weekStatus : '',
			dayNames : [ 'Dimanche', 'Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi' ],
			dayNamesShort : [ 'Dim', 'Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam' ],
			dayNamesMin : [ 'Di', 'Lu', 'Ma', 'Me', 'Je', 'Ve', 'Sa' ],
			dayStatus : 'Utiliser DD comme premier jour de la semaine',
			dateStatus : 'Choisir le DD, MM d',
			dateFormat : 'dd/mm/yy',
			firstDay : 0,
			initStatus : 'Choisir la date',
			isRTL : false
		};
		$.datepicker.setDefaults($.datepicker.regional['fr']);
		$(".datepicker").datepicker({
			dateFormat : "dd/mm/yy",
		});

		let b = $('#save-changes-sirh').hide();
		$('.form-control').keyup(function(){
		    $('#save-changes-sirh').show();
		});
		$('#ui-datepicker-div').mouseup(function(){
		    $('#save-changes-sirh').show();
		});
		$('.form-control').mouseup(function(){
			$('#save-changes-sirh').show();
		});



     });
});


