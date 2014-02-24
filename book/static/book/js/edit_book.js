$(document).ready(function () {

    $("button").click(function() {
        return false;
    });

    $("#show_toc_btn").click(function() {
        $(".toc").removeClass("hide");
        $("#show_toc_btn").hide();
    });

    $("#book_modify_btn").click(function() {
        $("#action").val("modify");
        $("#book_form").submit();
    });

    $("#book_add_btn").click(function() {
        if(!$("#subject").val()) {
            apprise("책 제목을 입력하세요", {}, function(r) {
                $("#subject").focus();
            });
            return;
        }

//        if(!$("#image").val()) {
//            apprise("책 이미지를 선택하세요");
//            return;
//        }

        $("#action").val("add");
        $("#book_form").submit();
    });

    $("#book_delete_btn").click(function() {
        var msg = [];
        msg.push('<div class="alert alert-danger">');
        msg.push(' <strong>책이 삭제됩니다.</strong><br />');
        msg.push(' 정말로 삭제하시겠습니까?');
        msg.push('</div>');
        msg.push('<span class="muted">※ 삭제 후 관리메뉴에서 복구 가능합니다.</span>');

        apprise(msg.join(''), {'verify':true}, function(r) {
            if(r) {
                $("#action").val("delete");
                $("#book_form").submit();
            }
         });
    });

    $('.markdown_editor').griffinEditor({autoSize: false});
    $(".markdown_tooltip").tooltip({
        'selector': '',
        'placement': 'bottom'
    });

    $("#search_user_btn").click(function() {
        var kw = $("#search_user").val();
        $.post("/edit/book/user", {
            "kw":kw
        }, function(data){
            $("#search_result").html(data);
            $("#search_result").show();
        }, "html");
    });

    $(".alert-info").fadeOut(2000);

    $(".closePreview").on("click", function() {
       $('#markdownPreview').modal('hide');
    });

    $('#markdownPreview').on('show.bs.modal', function () {
        $(this).find('.modal-content').css({
            width:'800px',
            marginLeft: '-100px'
        });
    });

});

$(window).load(function() {
    init_toc();
});

var TOC_HEIGHT;
function init_toc() {
    var is_mobile = $("#request_mobile").val() == "1";
    if(!is_mobile) {
        $("#_toc").show();
    }
    var page_height = get_height(".page");
    var toc_height = get_height("#edit_toc_box");
    TOC_HEIGHT = toc_height;
    if (toc_height > (page_height-108)) {
        $("#edit_toc_box").css("height", (page_height-108)+"px");
        $("#edit_toc_box").niceScroll({"cursorcolor":"#888"});
    }
}

function get_height(element) {
    var _height = $(element).css("height");
    return parseInt(_height.split("px")[0]);
}

function user_add(user_id) {
    $.post("/edit/book/user/add", {
        "book_id": $("#book_id").val(),
        "user_id": user_id
    }, function(data){
        $("#book_authors").html(data);
    }, "html");
}

function user_del(user_id) {
    apprise("공동저자를 취소하시겠습니까?", {'verify':true}, function(r) {
        if(r) {
            $.post("/edit/book/user/del", {
                "book_id": $("#book_id").val(),
                "user_id": user_id
            }, function(data){
                $("#book_authors").html(data);
            }, "html");
        }
     });
}

function preview() {
    var preview_content = $("#content").val();
    $.post("/edit/preview", {
        "preview_content": preview_content
    }, function(data){
        $("#markdown_preview_content").html(data);
        $('#markdownPreview').modal('show');
    }, "html");
}

function fullscreen() {
    $('#content').fullScreen({
        'background': '#111',
        'max-width':"200px",
        'callback': function (isFullScreen) {
        }
    });
}