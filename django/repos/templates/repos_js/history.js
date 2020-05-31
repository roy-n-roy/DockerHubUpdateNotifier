// for #historyModal {% load i18n %}
var pre_history = function() {
    $('#hist_name').text($(this).data('title'));
    $.ajax({
        url      : $(this).data('url'),
        type     : 'GET',
        dataType : 'json',
    }).done((data) => {
        var list = $('#hist_body').html('<ul class="="list-group"">');
        if (data.length > 0) {
            for (var i in data) {
                list.append('<li class="list-group-item">' + data[i].update + '</li>');
            };
        } else {
            list.append('<li class="list-group-item">{% blocktrans %}No history data.{% endblocktrans %}</li>');
        };
    }).fail((data) => {
        $('#hist_body').text('<p>{% blocktrans %}Failed to get history data.{% endblocktrans %}</p>');
    }).always(() => {
        //$('#in_process_label').remove();
    });
};
