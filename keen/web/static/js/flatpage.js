// JS for flatPages
'use strict';


(function($) {
    var hash = window.location.hash;
    if (hash === '#signin') {
        $('#loginModal').modal('show');
    }   


    $('.js-animate-scroll').on('click',function (e) {
        e.preventDefault();
        console.log(this.hash);
        var target = this.hash,
            $target = $(target);

        if(!$target.length){
            return false;
        }

        $('html, body').stop().animate({
            'scrollTop': $target.offset().top
        }, 300, 'swing', function () {
            window.location.hash = target;
        });
    });


})(jQuery);
