$(function() {
	var
		next = '/dashboard',
		$form = $('#signInForm'),
		$error = $form.find('.alert-error'),
		$fields = $form.find(':input');

	$error.hide();

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
						window.location.href = next;
					} else if (response.error) {
						$error.html(response.error);
						$error.show();
					}
				}
			});
	});

	if (window.location.hash) {
		hash = window.location.hash.trim();
		if (hash != '#') {
			next = hash.substr(1);
		}
		$('#loginModal').modal('show');
	}
});
