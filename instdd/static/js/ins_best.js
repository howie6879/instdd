/**
 * Created by howie on 28/04/2017.
 */
$(document).ready(function () {
    var username = $("#username").val();
    if (username == "") {
        window.location.href = "/2016";
    } else {
        data = {'username': username};
        $.ajax({
            type: "post",
            contentType: "application/json",
            url: "/ajax_ins_best",
            data: data,
            dataType: 'json',
            success: function (data) {
                if (data.status == 1) {
                    // 获取成功
                    $('.show_info').remove();
                    $('#best_nine').css("display", "block");
                    $('#des-info').text('在2016年，' + username + "共获得" + data.all_likes + "个赞，" + "po图" + data.post_nums + "次");
                    $('#best_nine_href').attr('href', data.best_nine_name);
                    $('#best_nine_img').attr('src', data.best_nine_name);
                    console.log(data)
                }
                if (data.status == 0) {
                    // 获取失败 0
                    $('.show_info').remove();
                    $('#des-info').text(data.msg);
                }
                if (data.status == -1) {
                    // 获取失败 -1
                    $('.show_info').remove();
                    $('#des-info').text(data.msg);
                }
                if (data.status == -2) {
                    // 获取失败 -1 网络原因
                    $('.show_info').remove();
                    $('#des-info').text(data.msg);
                }
                if (data.status == -3) {
                    // 获取失败 -1 生成图片失败
                    $('.show_info').remove();
                    $('#des-info').text(username + data.msg);
                }
            }
        });
    }
});