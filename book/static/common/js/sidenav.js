$(function() {

    $(".bs-sidenav > li > a").click(function() {
        $(".bs-sidenav > li").each(function() {
            $(this).removeClass("active");
        });
        $(this).parent().addClass("active");
    });

});