// for #editModal {% load i18n %}
var set_tags = function(owner, name, page, current) {
    if (name) {
        var url = "{% url 'repos:tags' owner='_owner_' name='_name_' page=0%}"
            .replace(/_owner_/g, owner).replace(/_name_/g, name).replace(/0/g, page);
        $.ajax({
            url      : url,
            type     : 'GET',
            dataType : 'json',
        }).done((data) => {
            var owner = $('#edit_form input[name="owner"]').val();
            owner = owner === '' ? 'library' : owner;
            if (owner === data.owner && $('#edit_form input[name="name"]').val() === data.name) {
                parent = $('#edit_form select[name="tag"]');
                for (var i in data.tags) {
                    if (data.tags[i] === current) {
                        parent.append($('<option>').val(data.tags[i]).html(data.tags[i]).attr('selected', ''));
                    } else {
                        parent.append($('<option>').val(data.tags[i]).html(data.tags[i]));
                    }
                };
                if (data.next) {
                    set_tags(owner, name, data.next, current);
                }
            }
        }).fail((data) => {
            parent = $('#edit_form select[name="tag"]');
            parent.children().remove();
            parent.append('<option value="latest" selected>latest</option>');
            $("#edit_form .modal-body").prepend(
                '<div id="form_alert" class="alert alert-warning alert-dismissible" role="alert">' +
                    '<button type="button" class="close" data-dismiss="alert" aria-label="Close">' +
                        '<span aria-hidden="true">&times;</span>' +
                    '</button>' +
                    '<span>{% blocktrans %}Failed to get tags for ' + (owner === 'library' ? '' : owner + '/') + name + '{% endblocktrans %}</span>' +
                '</div>'
            );
        }).always(() => {
            $('#in_process_label').remove();
        });
    }
};
var pre_edit = function() {
    var label = $(this).data('type') === 'update' ? '{% blocktrans %}Update{% endblocktrans %}' : '{% blocktrans %}Add{% endblocktrans %}';
    $('#edit_submit').text(label);
    $('#editModalLabel').text(label + ($(this).data('title') === '' ? '' : ' : ' + $(this).data('title')));
    $('#edit_name').text($(this).data('name'));
    $('#edit_form').attr('action', $(this).data('url'));
    $('#edit_form input[name="owner"]').val($(this).data('owner') === 'library' ? '' : $(this).data('owner'));
    $('#edit_form input[name="name"]').val($(this).data('name'));
    $('#edit_form select[name="tag"]').val($(this).data('tag'));
    $("#form_alert").remove();
    $('#edit_form select[name="tag"]').children().remove();
    $('#edit_form input[name="name"]').focus();
    set_tags($(this).data('owner'), $(this).data('name'), 1, $(this).data('tag'));
};
$("#edit_submit").click((e) => {
    var owner = $('#edit_form input[name="owner"]').val();
    owner = owner === '' ? 'library' : owner;
    var name = $('#edit_form input[name="name"]').val();
    var tag = $('#edit_form select[name="tag"]').val();
    var url = "{% url 'repos:check' owner='_owner_' name='_name_' tag='_tag_' %}"
        .replace(/_owner_/g, owner).replace(/_name_/g, name).replace(/_tag_/g, tag);
    $.ajax({
        url      : url,
        type     : 'GET',
        dataType : 'json',
    }).done(() => {
        $('#edit_form input[name="owner"]').val((idx, val) => {
            return val === '' ? 'library' : val;
        });
        $('#edit_form').off("submit");
        $('#edit_form').submit();
    }).fail((data) => {
        $("#form_alert").remove();
        $("#edit_form .modal-body").prepend(
            '<div id="form_alert" class="alert alert-warning alert-dismissible" role="alert">' +
                '<button type="button" class="close" data-dismiss="alert" aria-label="Close">' +
                    '<span aria-hidden="true">&times;</span>' +
                '</button>' +
                '<span>{% blocktrans %}' + (owner === 'library' ? '' : owner + '/') + name + ':' + tag + ' could not be found on Docker Hub.{% endblocktrans %}</span>' +
            '</div>'
        );
    });
    return e.preventDefault();
});
$('#edit_form input').on('change', (e) => {
    var owner = $('#edit_form input[name="owner"]').val();
    owner = owner === '' ? 'library' : owner;
    var name = $('#edit_form input[name="name"]').val();
    $('#edit_form select[name="tag"]').children().remove();
    $('#edit_form select[name="tag"]').append('<option id="in_process_label" value="" selected>{% blocktrans %}Retrieving data...{% endblocktrans %}</option>');
    set_tags(owner, name, 1, '');
});
$('#editModal').on('shown.bs.modal', () => {
    $('#edit_form input[name="name"]').focus();
});
