/**
 * Created by howie on 15/03/2017.
 */

$(document).ready(function () {
    $(".item").hover(function () {
        $(this).children(".hover-show").css("display", "block");
    }, function () {
        $(this).children(".hover-show").css("display", "none");
    })

});

