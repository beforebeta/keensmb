// JS for flatPages
'use strict';


(function($) {
    var hash = window.location.hash;
    if (hash === '#signin') {
        $('#loginModal').modal('show');
    };


    $('#topbar .main-navigation ul li a').on('click',function (e) {
	    e.preventDefault();

	    var target = this.hash,
	    $target = $(target);

	    $('html, body').stop().animate({
	        'scrollTop': $target.offset().top
	    }, 900, 'swing', function () {
	        window.location.hash = target;
	    });
	});


})(jQuery);

