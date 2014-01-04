// JS for flatPages
'use strict';


(function($) {
    var hash = window.location.hash;
    if (hash === '#signin') {
        $('#loginModal').modal('show');
    }


    $('.js-animate-scroll').on('click',function (e) {
        e.preventDefault();
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

    var topbarHeight = $('#topbar').outerHeight() - 50;
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

//    $('.carousel').carousel({interval: 5000});

    $('#tryFree').on('shown.bs.modal', function () {
        $("#trykeenform input[name='name']").focus();
    });
    $('#loginModal').on('shown.bs.modal', function () {
        $("#signInForm input[name='email']").focus();
    });

    $('.trykeenform').on('submit', function(event) {
        event.preventDefault();

        var $form = $(this),
            $errors = $form.find('.alert-error'),
            data = $form.serialize(),
            $input = $form.find(':input'),
            enable_form = function(state) {
                $form.find(':input').prop('disabled', !state);
            },
            clear_errors = function() {
                $errors.empty().hide();
            },
            add_error = function(error) {
                $errors.show().append($('<div/>').html(error));
            };

        enable_form(false);

        $.post($form.attr('action'), data)
            .always(function() {
                enable_form(true);
                clear_errors();
            })
            .fail(function() {
                add_error('Failed to contact server. Please try again');
                console.log(arguments);
            })
            .done(function(response) {
                if (response.success) {
                    $('#tryFree').modal('hide');
                    $('#tryFreeSuccess').modal('show');
                } else {
                    if (response.errors) {
                        $.map(response.errors, add_error);
                    }
                }
            });
    })
    .find('.alert-error').hide();

    $(".fancybox").fancybox();

    $('input[name="email"]').on('blur', function() {
        if(!$(this).val()) {
            $(this).parent().addClass('has-error');
        }
        else {
            $(this).parent().removeClass('has-error');
        }
    });

})(jQuery);
