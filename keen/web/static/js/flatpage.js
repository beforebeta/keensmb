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
    
    var topbarHeight = $('#topbar').outerHeight();
    var $scrollMenu = $('.scroll-menu');

    $(document).on('scroll', function() {
        if($(this).scrollTop() >= topbarHeight){
            $scrollMenu.fadeIn('fast');
        } else {
            $scrollMenu.fadeOut();
        }
    });


    $('.js-preload-image').each(function(index, item){
        var $item = $(item),
            imgSrc = $item.data('image-bg');
            
        $item.css('background-image', 'url(' + imgSrc + ')');
    });

    $('.carousel').carousel({interval: 5000});

    try{
        $(document).ready(function() {
            $('#tryFree').on('shown.bs.modal', function () {
               $("#trykeenform input[name='name']").focus();
            });
        });
    }catch(e){
        console.log(e);
    }

})(jQuery);
