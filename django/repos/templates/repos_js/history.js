// for #historyModal {% load i18n %}
var pre_history = function() {
    $('#hist_name').text($(this).data('title'));
    $.ajax({
        url      : $(this).data('url'),
        type     : 'GET',
        dataType : 'html',
    }).done((data) => {
        $('#hist_body').html(data);
    }).fail((data) => {
        $('#hist_body').text('<p>{% blocktrans %}Failed to get history data.{% endblocktrans %}</p>');
    }).always(() => {
    });
};
