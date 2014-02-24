$(function () {
    $("#joinBtn").click(function() {
        $("#joinForm").attr("action", "/join");
        $("#joinForm").submit();
    });
});
