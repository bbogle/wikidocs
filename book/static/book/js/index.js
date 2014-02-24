$(document).ready(function () {
    $("#book-tab li").click(function() {
        var library = $(this).attr("book");
        load_tab((library));
    });
    select_tab($("#tab_name").val());
});

function select_tab(tabname) {
    $("#book-tab li").removeClass("active");
    $("#book-tab li").each(function() {
        if($(this).attr("book") == tabname) {
            $(this).addClass("active");
        }
    });
}

function load_tab(tab) {
    select_tab(tab);

    $.post("/tab/"+tab, {
    }, function(data){
        $("#books").html(data);
    }, "html");
}