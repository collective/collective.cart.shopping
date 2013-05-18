jq(function() {
    jq('form').click(function(event) {
        jq(this).data('clicked', jq(event.target));
    });
    jq('form').submit(wait_processing);
});

function wait_processing() {
    if (jq(this).data('clicked').is(jq('button[name="form.buttons.CheckOut"]'))) {
        jq('#processing_message').css('display', 'block');
        jq('button').attr("disabled");
    }
}
