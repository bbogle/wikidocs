$(document).ready(function () {
    /*
    var info_tab = $.cookie('info_tab');
    if(info_tab) {
        $('#info_tab a[href='+info_tab+']').tab('show');
    }
    $("#info_tab a").click(function() {
        $.cookie('info_tab', $(this).attr("href"));
    });
    */

    var total_count = $("#total_count").val();
    var current_page_index = $("#current_page").val()-1;
    $("#pagination").pagination(total_count, {
		callback:handlePaginationClick,
		current_page:current_page_index,
		items_per_page:$("#per_page").val(),
		num_display_entries:5,
		num_edge_entries:1,
		prev_text: "이전",
		next_text: "다음"
	});
});


function handlePaginationClick(new_page_index, pagination_container) {
    var nextpage = new_page_index+1;
    $("#hiddenForm #page").val(nextpage);
    $("#hiddenForm").submit();
    return false;
}