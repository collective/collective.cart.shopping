jQuery(function() {

    $("#add-to-cart").on("change", "select[name='subarticle']", function(event) {
        var target = event.currentTarget;
        var action = $(target).closest("#subarticle").attr('data-ajax-target');
        var token = $(target).closest("#content-core").find('input[name="_authenticator"]').val();
        var uuid = $(target).val();

        var data = {
            '_authenticator': token,
            'uuid': uuid,
        };

        $.post(action, data, function(data) {
            var targ = $(target).closest("#add-to-cart").find('#quantity > input');
            targ.attr('max', data['maximum']);
            targ.attr('maxlength', data['size']);
            targ.attr('size', data['size']);
        }, 'json');
        return false;
    });

});
