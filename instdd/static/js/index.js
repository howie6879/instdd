/**
 * Created by howie on 15/03/2017.
 */

$(document).ready(function () {
    setTimeout('isTop()', 17);
    $('.sub-button').click(function () {
        if ($(".form-url").val() == "") {
            $(".form-url").focus();
        } else {
            $('.sub_url').submit();
        }
    })
});

function isTop() {
    if ($(document).scrollTop() > 40) {
        $('.single_download').show();
        $(".navbar-color-on-scroll").removeClass("navbar-transparent");
    } else {
        $('.single_download').hide();
        $(".navbar-color-on-scroll").addClass("navbar-transparent");
    }
    setTimeout('isTop()', 17);
}

$('.we-button').popover({
    trigger: 'hover',
    html: true,
    content: "<img width='120px' height='120px' src='static/images/ttt.png'><p style='text-align: center'><span>微信关注<strong>图图推</strong></span></p><p style='text-align: center'>下载更方便</p>"
});

$('#contact').popover({
    trigger: 'hover',
    html: true,
    content: "tututui.ttt@gmail.com"
});