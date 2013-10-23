jQuery(function() {

    $("#content").on("change", "select[name='subarticle']", function(event) {
        var target = event.currentTarget;
        var action = $(target).closest("#subarticle").attr('data-ajax-target');
        var token = $(target).closest('#content-core').find('input[name="_authenticator"]').val();
        var uuid = $(target).val();

        var data = {
            '_authenticator': token,
            'uuid': uuid,
        };

        $.post(action, data, function(data) {
            var target = $("#quantity > input");
            target.attr('size', data['size']);
            target.attr('max', data['maximum']);
        }, 'json');
        return false;
    });

});
