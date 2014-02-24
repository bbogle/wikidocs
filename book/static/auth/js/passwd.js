$(function () {
    $("#sendBtn").click(function() {
        $("#passwdForm").attr("action", "/passwd/send");
        $("#passwdForm").submit();
    });
});
