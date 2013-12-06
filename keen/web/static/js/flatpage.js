// JS for flatPages
'use strict';


(function($) {
    var hash = window.location.hash;
    if (hash === '#signin') {
        $('#loginModal').modal('show');
    }
})(jQuery);
