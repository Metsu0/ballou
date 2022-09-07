odoo.define('ooto_hr_holidays_front.registration_leave', function(require) {
    'use strict';
    var ajax = require('web.ajax');
    var core = require('web.core');
    var _t = core._t;
    $(document).ready(function() {
        var checkbox = $("#halfday_checkbox");
        var period = $("#date_request_from_period");
        var hidden = $("#hide_field_if_halfday");
        hidden.show();
        period.hide();

        // Jauge
        $('#cont').attr('data-day','jour');
        if ( $('#reste_conge').text() && $('.acquiredcpnvalue').val() ){
            var val_1 = parseFloat($('#reste_conge').text()).toFixed(2);
            var val_2 = parseInt($('.acquiredcpnvalue').val());
            var val = (val_1 * 100 )/ val_2;
            var $circle = $('#svg #bar');
            if (isNaN(val)) {
                val = 0;
            } else {
                var r = $circle.attr('r');
                var c = Math.PI * (r * 2);

                if (val < 0) { val = 0; }
                if (val > 100) { val = 100; }

                var pct = ((100 - val) / 100) * c;

                $circle.css({ strokeDashoffset: pct });

                $('#cont').attr('data-pct', val_1);
            }
            if (val_1 > 1){
                $('#cont').attr('data-day','jours');
            }
            else{
                $('#cont').attr('data-day','jour');
            }
        }
        // ************

        // Justificatory
        var size_justif = 0
           ajax.jsonRpc('/params/justificatory', 'call', {}).then(function (data){
                if (data['size']){
                    size_justif = parseInt(data['size'], 10) * 1024 * 1024;
                }
            })
        $("#file-justificatory").change(function(){
         if(this.files[0].size > size_justif){
               $("#size_limit").text(size_justif / 1048576);
               jQuery("#error-leave-size").show();
               this.value = "";
            }
            else {
             jQuery("#error-leave-size").hide();
            }
        });
        $('#download-justificatory-create').hide();
        $('#remove-justificatory-create').hide();
        $('#file-name-justificatory').hide();
        var handleFileSelect = function(evt) {
            var files = evt.target.files;
            var file = files[0];
            if (files && file) {
                var reader = new FileReader();
                document.getElementById("name-file").value = file.name;
                $('#file-name-justificatory').text(file.name);
                $('#file-name-justificatory').css("display", "inline-block");
                $('#upload-file').hide();

                reader.onload = function(readerEvt) {
                    var binaryString = readerEvt.target.result;
                    document.getElementById("base64textarea1").value = btoa(binaryString);
                    $('#download-justificatory-create').show();
                    $('#remove-justificatory-create').show();
                };
                reader.readAsBinaryString(file);
            }
        };
        if (window.File && window.FileReader && window.FileList && window.Blob) {
            if ($('#upload-file').is(':visible')) {
                document.getElementById('file-justificatory').addEventListener('change', handleFileSelect, false);
            }
        } else {
            alert('The File APIs are not fully supported in this browser.');
        }
        $('#remove-justificatory-create').on('click', function() {
                $('#base64textarea1').val('');
                $('#name-file').val('');
                $('#file-justificatory').val('');
                $('#download-justificatory-create').hide();
                $('#remove-justificatory-create').hide();
                $('#file-name-justificatory').hide();
                $('#upload-file').show();
            })
        $('#upload-file').on('click', function() {
            $('#file-justificatory').trigger("click");
        })
        if ($('#name-file').val() && $('#base64textarea1').val()) {
            $('#file-name-justificatory').text($('#name-file').val());
            $('#file-name-justificatory').show();
            $('#upload-file').hide();
            $('#download-justificatory-create').show();
            $('#remove-justificatory-create').show();
        }
        $('#file-name-justificatory').on('click', function() {
                if ($("#name-file").val()) {
                    const base64_data = 'data:application/octet-stream;base64,' + document.getElementById("base64textarea1").value;
                    const linkSource = base64_data;
                    const downloadLink = document.createElement("a");
                    const fileName = document.getElementById("name-file").value;

                    downloadLink.href = linkSource;
                    downloadLink.download = fileName;
                    downloadLink.click();
                }
            })
            //
        $('#cancel-create').on('click', function() {
            $('.part_1_bloc').show();
            $('.part_2_bloc').hide();
        })
        $('.leave_read_only').hide();
        if ($('.leave_read_only').is(':checked')) {
            $('#type-leave').attr('readonly', true);
            $('#file-justificatory').attr('readonly', true);
            $('#halfday_checkbox').attr('readonly', true);
            $('.date_begin').attr('readonly', true);
            $('.period-leave').attr('readonly', true);
            $('#cancel-edit').hide();
            $('#save-edit').hide();
        }

        // DASHBOARD CALENDAR ADD LEAVE
        var datetest;
        ajax.jsonRpc('/leave/date','call',{}).then(function (data){
            if (data){
                datetest = data
                $('.calendar_dashboard').pignoseCalendar({
                    lang: 'fr',
                    scheduleOptions: {
                        colors: {
                            leave: '#EDEEF2',
                        }
                    },
                    schedules: datetest,
                });
            }
        })
        // calendar
        function set_date(date_1,date_2){
            var new_date_1 = new Date(date_1);
            var new_date_2 = new Date(date_2);
            if (new_date_1 > new_date_2){
                $('.calendar').pignoseCalendar('set', date_1);
                while(!$("[data-date=" + date_2 + "]").length){
                    $('.pignose-calendar-top-prev').trigger('click');
                }
                $("[data-date=" + date_2 + "]").trigger('click');
            }
            else if (new_date_1 < new_date_2){
                $('.calendar').pignoseCalendar('set', date_2);
                while(!$("[data-date=" + date_1 + "]").length){
                    $('.pignose-calendar-top-prev').trigger('click');
                }
                $("[data-date=" + date_1 + "]").trigger('click');
            }
            else{
                $('.calendar').pignoseCalendar('set', date_2);
            }
        }
        var first_click = 1;
        var today = new Date();
        var elements = [today.getFullYear(),("0"+(parseInt(today.getMonth(), 10)+1).toString()).substr(-2),("0"+today.getDate()).substr(-2)];
        var cday = elements.join('-');
        if (checkbox.is(':checked')) {
            hidden.hide();
            period.show();
        } else {
            hidden.show();
            period.hide();
        }
        checkbox.change(function (){
            if (checkbox.is(':checked')) {
                hidden.hide();
//                if (!$('.date_begin').val()){
//                    var current_date_3 = $("[data-date=" + cday + "]");
//                }
                if($('.date_end').val() != $('.date_begin').val()){
                    $('.calendar').pignoseCalendar('set', $('.date_begin').val());
//                    $("[data-date=" + $('.date_end').val() + "]").trigger('click');
                    $('.date_end').val($('.date_begin').val());
                }
                period.show();
            }
            else{
                hidden.show();
                period.hide();
            }
        })
        // $('.calendar').pignoseCalendar('settings', {
        //     lang: 'fr',
        // });
        $('.date_begin').change(function() {
            $('#error-date-empty').hide();
            //calendar
            if (!$('.date_end').val() && $('.date_begin').val()){
                $('.date_end').val($('.date_begin').val())
            }
            if (checkbox.is(':checked')){
                $('.calendar').pignoseCalendar('set', $('.date_begin').val());
            }
            else{
                set_date($('.date_begin').val(),$('.date_end').val());
            }

        })
        $('.date_end').change(function() {
            var end_old = $('.date_end_2').val();
            var end_new = $('.date_end').val();
            if ($('.date_end').val()){
                $('.date_end_2').val($('.date_end').val());
            }
            if(!$('.date_begin').val() && $('.date_end').val()){
                $('.date_begin').val($('.date_end').val());
                set_date($('.date_begin').val(),$('.date_end').val());
            }
            if(!($('.date_end').val()) && $('.date_begin').val()){
                $('.date_end_2').val(('.date_end_2').defaultValue)
                set_date($('.date_begin').val(),$('.date_end').val());
            }
            //calendar
            var date_end_1 = $('.date_end').val()
            if(!checkbox.is(":checked") && date_end_1 != $('.date_begin').val()){
                set_date($('.date_begin').val(),$('.date_end').val());
            }
        })
        $('.calendar').pignoseCalendar({
            multiple: true,
            lang: 'fr',
            next: function(info, context) {
                var current_date_11 = $("[data-date=" + cday + "]");
                if(current_date_11.hasClass('pignose-calendar-unit-active') && !$('.date_begin').val() && !$('.date_end').val()){
                    current_date_11.trigger('click');
                }
            },
            prev: function(info, context) {
                var current_date_12 = $("[data-date=" + cday + "]");
                if(current_date_12.hasClass('pignose-calendar-unit-active') && !$('.date_begin').val() && !$('.date_end').val()){
                    current_date_12.trigger('click');
                }
            },
            select: function(date, context) {
                var $element = context.element;
                var $calendar = context.calendar;
                var date_begin = $('.date_begin').val();
                var current_date = $("[data-date=" + cday + "]");
                if (date[0] !== null && date[0].format('YYYY-MM-DD') !== cday && date[0].format('YYYY-MM-DD') != $('.date_begin').val()){
                    $('.date_begin').val(date[0].format('YYYY-MM-DD'));
                }
                if (date[1] !== null) {
                    if (checkbox.is(':checked')) {
                        checkbox.trigger('click');
                    }
                }
                if (date[0] !== null && date[1] !== null){
                    $('.date_begin').val(date[0].format('YYYY-MM-DD'));
                    $('.date_end').val(date[1].format('YYYY-MM-DD'));
                    $('.date_end_2').val(date[1].format('YYYY-MM-DD'));
                }
                if (date[0] === null && date[1] !== null){
                    $('.date_begin').val(date[1].format('YYYY-MM-DD'));
                    $('.date_end').val(date[1].format('YYYY-MM-DD'));
                    $('.date_end_2').val(date[1].format('YYYY-MM-DD'));
                }
                if (date[0] !== null && date[1] === null){
                    $('.date_begin').val(date[0].format('YYYY-MM-DD'));
                    $('.date_end').val(date[0].format('YYYY-MM-DD'));
                    $('.date_end_2').val(date[0].format('YYYY-MM-DD'));
                }
                if (first_click == 1 && date[1] !== null && date[1] === null){
                    $('.date_begin').val(date[1].format('YYYY-MM-DD'));
                    $('.date_end').val(date[1].format('YYYY-MM-DD'));
                    $('.date_end_2').val(date[1].format('YYYY-MM-DD'));
                }

                if (date[0] === null && date[1] == null) {
                    $('.date_end').val($('.date_end').defaultValue);
                    $('.date_begin').val($('.date_begin').defaultValue);
                }

                if (date[0] === date[1] && date[0] !== null){
                    $("[data-date=" + date[0].format('YYYY-MM-DD') + "]").trigger('click');
                }
                // ne pas prendre en compte le premier click
                if((!date_begin || (date_begin && date_begin !== cday)) && current_date.hasClass('pignose-calendar-unit-active') && first_click == 1){
                    --first_click;
                    current_date.trigger('click');
                }
            },

        });
        $('#error-leave-type').hide();
        $('button#valid-part-1').on('click', function() {
            $('#sufficient-error').hide();
            $('#overlaps-error').hide();
            $('#error-date-empty').hide();
            if ($('#type-leave').val().length > 3) {
                $('#error-leave-type').show();
            } else {
                $('#error-leave-type').hide();
                $('.bloc_absence_corps.bloc_absence_type_absence').hide();
                $('.bloc_absence_type_absence.titre_bloc_absence_entete').addClass('valider');
                $('.bloc_absence_type_absence.bloc_absence_entete').addClass('valider');
                $('.bloc_absence_corps.bloc_absence_date').show();
                var data_end_2 = $('.date_end').val()
                var data_begin_2 = $('.date_begin').val()
                set_date($('.date_begin').val(),$('.date_end').val());
            }
        })
        $('.titre_bloc_absence_entete.bloc_absence_type_absence').on('click', function() {
            if ($('.bloc_absence_corps.bloc_absence_type_absence').hide()) {
                $('.bloc_absence_corps.bloc_absence_type_absence').show();
            }
        })

        $('#type-leave').change(function() {
            if ($('#error-leave-type').show()) {
                $('#error-leave-type').hide();
            }
        })

        $('#sufficient-error').hide();
        $('#overlaps-error').hide();
        $('.loading_confirm_leave').hide();
        $('#valid-leave-1').on('click', function() {
                $('.loading_confirm_leave').show();
                $('#valid-leave-1').prop('disabled', true);
                $('#sufficient-error').hide();
                $('#overlaps-error').hide();
                if (!$('.date_begin').val()) {
                    $('.loading_confirm_leave').hide();
                    $('#error-date-empty').show();
                    $('#valid-leave-1').prop('disabled', false);
                } else {
                    $.ajax({
                        type: 'POST',
                        url: '/leave/register',
                        data: $('#leave_registration_form').serialize(),
                        dataType: "json",
                    }).done(function(data) {
                        $('.loading_confirm_leave').hide();
                        if (data['url']) {
                            $('#valid-leave-modal').trigger('click');
                            window.location.href = data['url'];
                        } else if (data['sufficient']) {
                            $('#valid-leave-1').prop('disabled', false);
                            $('#sufficient-error').show();
                        } else if (data['overlaps']) {
                            $('#valid-leave-1').prop('disabled', false);
                            $('#overlaps-error').show();
                        }else if (data['not_allowed']) {
                            $('#valid-leave-1').prop('disabled', false);
                            $('#not-allowed-error').show();
                        }else if (data['exceptional_error']) {
                            $('#valid-leave-1').prop('disabled', false);
                            $('#exceptional-error').show();
                        }
                    })
                }
            })
        // **********************

    })

});