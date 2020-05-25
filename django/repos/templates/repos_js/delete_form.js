// for #deleteModal
var pre_delete = function() {
    $('#del_name').text($(this).data('title'));
    $('#del_form').attr('action', $(this).data('url'));
};
