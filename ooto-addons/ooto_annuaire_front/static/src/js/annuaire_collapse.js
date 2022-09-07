$(document).ready(function () {
    $('.annuaire_section').each(function (index) {
        $(this).attr("data", index);
        $(this).addClass("id" + index);
    });
    var nbSection = parseInt($(".annuaire_section:last-child").attr('data'), 10);
    for (var i = 0; i <= nbSection; i++) {
        $(".id" + i + " .card-header .annuaire_bloc1").attr("data-target", "#collapse" + i);
        $(".id" + i + " .annuaire_bloc2").attr("id", "collapse" + i);
    }
});