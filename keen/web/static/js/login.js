$(function() {
	var
		$form = $('#signInForm'),
		$error = $form.find('.alert-error'),
		$fields = $form.find(':input');

	$form.on('submit', function(event) {
		event && event.preventDefault();
		// serialize form BEFORE disabling all inputs
		var data = $form.serialize();
		$error.hide();
		$fields.prop('disabled', true);
		$.post($form.attr('action'), data)
			.always(function() {
				$fields.prop('disabled', false);
			})
			.fail(function(response) {
				if (response.status == 403) {
					// most likely caused by expired CSRF token
					window.location.reload(true);
				}
			})
			.done(function(response) {
				if (response) {
					if (response.success) {
						window.location.reload(true);
					} else if (response.error) {
						$error.html(response.error);
						$error.show();
					}
				}
			});
	});

	$error.hide();
	$('#loginModal').modal('show');
});
