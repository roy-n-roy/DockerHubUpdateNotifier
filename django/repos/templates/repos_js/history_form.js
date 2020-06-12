// for #historyModal {% load i18n %}
var pre_history = function() {
    $.ajax({
        url      : $(this).data('url'),
        type     : 'GET',
        dataType : 'html',
    }).done((data) => {
        $('#hist_body').html(data);
    }).fail((data) => {
        $('#hist_body').html('<p>{% blocktrans %}Failed to get history data.{% endblocktrans %}</p>');
    }).always(() => {
    });
};
