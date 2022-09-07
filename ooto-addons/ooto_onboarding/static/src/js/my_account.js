odoo.define('ooto_onboarding.my_account', function (require) {
    "use strict";

    var rpc = require('web.rpc');

    $(document).ready(function () {

        $(function () {
            $('.custom_datetimepicker').datetimepicker({locale:'fr', format: 'YYYY-MM-DD HH:mm'});
        });
        //justification code Arnaud
        $('.upload.upload_button').prev().change(function () {
            var input = $(this)
            var file = input[0].files[0],
                reader = new FileReader();
            var input_name = this.name;

            reader.onloadend = function (e) {
                var b64 = reader.result.replace(/^data:.+;base64,/, '');
                rpc.query({
                    model: 'hr.employee',
                    method: 'upload_file',
                    args: [this, input_name, file.name, b64],
                }).then(function () {
                    var binaryString = e.target.result;
                    var x = $(input).closest('.dropdown_list_dashboard_ensemble_liste_link').find('.base64textarea');
                    x.val(btoa(binaryString)) ;
                    //console.log(x);
                    var y = $(input).closest('.dropdown_list_dashboard_ensemble_liste_link').find('.name-file');
                    y.val(file.name) ;
                })
            };
            reader.readAsDataURL(file);
            $(this).prev().addClass('checked');
            $(this).next('.docafournir').css('display', 'none');
            $(this).prev().css('display', 'inline-block');
            $(this).closest('.dropdown_list_dashboard_ensemble_liste_link').find('.remove-downloaded-content').css('display', 'inline-block');
            $(this).prev().html(file.name);

        });

        $('.show_name_pagedocensemble').on('click', function() {
                if ($(this).next().val()) {
                    var x = $(this).closest('.dropdown_list_dashboard_ensemble_liste_link').find('.base64textarea').val();
                    //console.log(x);
                    const base64_data = 'data:application/octet-stream;base64,' + x;
                    const linkSource = base64_data;
                    const downloadLink = document.createElement("a");
                    var y = $(this).closest('.dropdown_list_dashboard_ensemble_liste_link').find('.name-file').val();
                    const fileName = y;
                    //console.log(y);
                    downloadLink.href = linkSource;
                    downloadLink.download = fileName;
                    downloadLink.click();
                }
            });

        $('.remove-downloaded-content').on('click', function() {
                $('.base64textarea1').val('');
                $('.name-file').val('');
                $(this).closest('.dropdown_list_dashboard_ensemble_liste_link').find('.docafournir ').css('display', 'inline-block');
                $(this).closest('.dropdown_list_dashboard_ensemble_liste_link').find('.show_name_pagedocensemble  ').css('display', 'none');
                $(this).hide();
                $(this).closest('.dropdown_list_dashboard_ensemble_liste_link').find(':input').val('');

            })
        //fin justification code Arnaud

        //code que dev a ignoré dans doc a remplir check si les champs remplie et animation
        $("#save-admin-task-changes").on("click", function(e) {

            var isValidForm = true;
              $('#fields_to_fill_form .form-control').each(function() {
                if (!this.value.trim()) {
                  isValidForm = false;
                  $(this).css('border','1px solid red');
                  $( "<p class='required_champ'>Champs Obligatoire</p>" ).insertAfter( this );
                }
              });
              if (isValidForm == true)
              {
                console.log('click bouton');
                console.log('test = 0');
                $(this).addClass("realized");
                lottie.play();
                $(this).text("Tâche réalisée").fadeIn('fast');
                setTimeout(function () {
                    $( "#fields_to_fill_form" ).submit();
                }, 3000);
              }

        });

        /*$('#fields_to_fill_form').on('submit', function(e){
          e.preventDefault();
          $(this).addClass("realized");
        lottie.play();
        $(this).text("Tâche réalisée").fadeIn('fast');
        });*/


    })
});