$(document).ready(function () {
//    $("pre").addClass("prettyprint");
//    prettyPrint();

    $("#show_toc_btn").click(function () {
        $(".toc").removeClass("hide");
        $("#show_toc_btn").hide();
    });

    $("#feedback_btn").click(function () {

        var page_id = $("#page_id").val();
        var email = $("#email").val();
        var feedback = $("#feedback").val();

        if (!email) {
            apprise("답장받을 이메일을 입력하세요.", {}, function () {
                $("#email").focus();
            });
            return;
        }

        if (!validateEmail(email)) {
            apprise("이메일을 정확하게 입력 해 주세요.", {}, function () {
                $("#email").focus();
            });
            return;
        }

        if (!feedback) {
            apprise("피드백을 입력하세요.", {}, function () {
                $("#feedback").focus();
            });
            return;
        }

        $.post("/feedback", {
            "page_id": page_id,
            "email": email,
            "feedback": feedback
        }, function (data) {
            apprise("피드백을 남겨주셔서 감사합니다.", {}, function () {
                $('#myModal').modal('hide');
            });
        }, "html");

    });

    $("#comment_btn").click(function () {
        var content = $("#content").val();
        if (!content) {
            apprise("댓글을 입력해 주세요", {verify: false}, function (r) {
                $("#content").focus();
            });
            return false;
        }

        $.post("/page/comment/save", {
            "page_id": $("#page_id").val(),
            "content": content
        }, function (data) {
            $(".comments").html(data);
            $("#content").val("");
        }, "html");
    });

    $('a[href="#top"]').click(function () {
        $('html,body').animate({ scrollTop: $("body").offset().top},
            {duration: 'normal', easing: 'swing'});
        return false;
    });
});

$(window).load(function () {
    if (!TOC_HEIGHT) {
//        init_toc();
    }
});

function touch_toc() {
    if ($(".page img").length == 0) {
        init_toc();
    }
}

var TOC_HEIGHT;
function init_toc() {
    var is_mobile = $("#request_mobile").val() == "1";
    if (!is_mobile) {
        $(".toc").show();
    }
    var selected_toc_li_top = $(".selected_toc_li").offset().top;
    var page_height = get_height(".page");
    var toc_height = get_height(".toc-area");
    TOC_HEIGHT = toc_height;

//    console.log("page_height:"+page_height);

    if (toc_height >= 480) {
        if (page_height - 145 <= 480) {
            $(".toc-area").css("height", (page_height - 145) + "px");
            $(".toc-open").show();
            $(".toc-area").niceScroll({"cursorcolor": "#888"});
            $(".toc-area").scrollTop(selected_toc_li_top - 200);
        } else if (toc_height > 480) {
            $(".toc-area").css("height", "480px");
            $(".toc-open").show();
            $(".toc-area").niceScroll({"cursorcolor": "#888"});
            $(".toc-area").scrollTop(selected_toc_li_top - 200);
        }
    }

    if (page_height > 480 + 300) {
        $(".toc-ads").show();
    }
}
function open_toc() {
    $(".toc-area").css("overflow-y", "visible");
    $(".toc-area").css("height", TOC_HEIGHT + "px");
    $(".toc-open").hide();
}
function get_height(element) {
    var _height = $(element).css("height");
    return parseInt(_height.split("px")[0]);
}

function remove_comment(comment_id) {
    apprise("정말로 삭제하시겠습니까?", {verify: true}, function (r) {
        if (r) {
            $.post("/page/comment/remove", {
                "comment_id": comment_id
            }, function (data) {
                $(".comments").html(data);
            }, "html");
        }
    });
}

function show_comments() {
//    var display = $(".user_comments").css("display");
//    if (display == "none") {
//        $(".user_comments").css("display", "block");
//    }else {
//        $(".user_comments").css("display", "none");
//    }
}