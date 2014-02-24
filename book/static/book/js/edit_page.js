$(document).ready(function () {

    $("button").click(function () {
        return false;
    });

    $("#show_toc_btn").click(function () {
        $(".toc").removeClass("hide");
        $("#show_toc_btn").hide();
    });

    $("#page_modify_btn").click(function () {
        var open_yn = $('input[name=open_yn]:checked', '#page_form').val();

        $('#page_form').block({
            message: '페이지를 저장합니다...'
        });

        $.post("/edit/page/save", {
            "action": "modify",
            "page_id": $("#page_id").val(),
            "subject": $("#subject").val(),
            "content": $("#content").val(),
            "open_yn": open_yn,
            "parent": $("#parent").val()
        }, function (json) {
            var myUnblock = function () {
                $('#page_form').unblock();
                if (!json.success) {
                    location.reload();
                } else {
                    $(".alert-danger").hide();
                }
            }
            setTimeout(myUnblock, 1000);

        }, "json");
    });

    $("#page_add_btn").click(function () {
        $("#action").val("add");
        $("#page_form").submit();
    });

    $("#page_delete_btn").click(function () {
        apprise('정말로 삭제하시겠습니까?', {'verify': true}, function (r) {
            if (r) {
                $("#action").val("delete");
                $("#page_form").submit();
            }
        });
    });

    $('.markdown_editor').griffinEditor({autoSize: false});
    $(".markdown_tooltip").tooltip({
        'selector': '',
        'placement': 'bottom'
    });

    $(".alert-message").fadeOut(2000);

    var uploader = new qq.FileUploader({
        action: "/edit/page/image/upload",
        element: $('#file-uploader')[0],
        multiple: false,
        onComplete: function (id, fileName, responseJSON) {
            if (responseJSON.success) {
                $("#page-images").html(responseJSON.html);
            }
        },
        onAllComplete: function (uploads) {
            // uploads is an array of maps
            // the maps look like this: { file: FileObject, response: JSONServerResponse }
            // alert( "All complete!" ) ;
        },

        onSubmit: function () {
            uploader.setParams({
                'image_size': $("#image_size").val(),
                'page_id': $("#page_id").val()
            });
        },

        allowedExtensions: ['jpg', 'jpeg', 'png', 'gif'],
        template: $("#file-uploader-template").html(),

        params: {
//          'page_id': $("#page_id").val()
        }
    });

//    var image_size = 0;
//    var image_slider = $("#image_size_slider").slider({
//        value:0,
//        max: 1000,
//        step: 50
//    }).on('slideStop', function(ev) {
//        image_size = ev.value;
//    });

    $(".closePreview").on("click", function () {
        $('#markdownPreview').modal('hide');
    });

    $('#markdownPreview').on('show.bs.modal', function () {
        $(this).find('.modal-content').css({
            width: '800px',
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
    var selected_toc_li_top = $(".selected_toc_li").offset().top;
    var page_height = get_height(".page");
    var toc_height = get_height("#edit_toc_box");
    TOC_HEIGHT = toc_height;
    if (toc_height > (page_height-108)) {
        $("#edit_toc_box").css("height", (page_height-108)+"px");
        $("#edit_toc_box").niceScroll({"cursorcolor":"#888"});
        $("#edit_toc_box").scrollTop(selected_toc_li_top-200);
    }
}

function get_height(element) {
    var _height = $(element).css("height");
    return parseInt(_height.split("px")[0]);
}


function remove_image(page_image_id) {
    apprise("이미지를 삭제하시겠습니까?", {'verify': true}, function (r) {
        if (r) {
            $.post("/edit/page/image/del", {
                "page_image_id": page_image_id
            }, function (data) {
                $("#page-images").html(data);
            }, "html");
        }
    });
}

function apply_image(page_image_id) {
    var image_url = $("#pageimage_" + page_image_id).prop("href");
    var data = $('#content').val();
    var image_markdown = "\n\n![](" + image_url + ")";
    $('#content').focus().val('').val(data + image_markdown);
    $('#content').scrollTop($('#content')[0].scrollHeight);
}

function preview() {
    var preview_content = $("#content").val();
    $.post("/edit/preview", {
        "preview_content": preview_content
    }, function (data) {
        $("#markdown_preview_content").html(data);
        $('#markdownPreview').modal('show');
    }, "html");
}

function fullscreen() {
    $('#content').fullScreen({
        'background': '#111',
        'callback': function (isFullScreen) {
        }
    });
}