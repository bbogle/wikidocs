$(document).ready(function () {

    $("#comment_btn").click(function() {
        var content = $("#content").val();
        if(!content) {
            apprise("댓글을 입력해 주세요", {verify:false}, function(r) {
                $("#content").focus();
            });
            return false;
        }

        $.post("/book/comment/save", {
            "book_id":$("#book_id").val(),
            "content": content
        }, function(data){
            $(".comments").html(data);
            $("#content").val("");
        }, "html");
    })


    $("#show_toc_btn").click(function() {
        $(".toc").removeClass("hide");
        $("#show_toc_btn").hide();
    });

//    init_toc();
});

$(window).load(function() {
//    init_toc();
});

var TOC_HEIGHT;
function init_toc() {
    var is_mobile = $("#request_mobile").val() == "1";
    if(!is_mobile) {
        $(".toc").show();
    }
    var page_height = get_height(".page");
    var toc_height = get_height(".toc-area");
    TOC_HEIGHT = toc_height;
    if(toc_height>=480) {
        if(page_height-120 <= 480) {
            $(".toc-area").css("height", (page_height-120)+"px");
            $(".toc-open").show();
            $(".toc-area").niceScroll({"cursorcolor":"#888"});
        }else if(toc_height > 480) {
            $(".toc-area").css("height", "480px");
            $(".toc-open").show();
            $(".toc-area").niceScroll({"cursorcolor":"#888"});
        }
    }

    if(page_height > 480+300) {
        $(".toc-ads").show();
    }
}
function open_toc() {
    $(".toc-area").css("overflow-y", "visible");
    $(".toc-area").css("height", TOC_HEIGHT+"px");
    $(".toc-open").hide();
}

function get_height(element) {
    var _height = $(element).css("height");
    return parseInt(_height.split("px")[0]);
}

function remove_comment(comment_id) {
    apprise("정말로 삭제하시겠습니까?", {verify:true}, function(r) {
        if(r) {
            $.post("/book/comment/remove", {
                "comment_id": comment_id
            }, function(data){
                $(".comments").html(data);
            }, "html");
        }
    });
}

function show_comments() {
    $(".pages").css("display", "none");
    $(".comments").css("display", "block");
}

function show_pages() {
    $(".pages").css("display", "block");
    $(".comments").css("display", "none");
}
