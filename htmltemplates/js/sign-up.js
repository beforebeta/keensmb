
// JS for SignUp page
'use strict';

(function($) {

    $('.js-editable-section').on('focus', '.js-editable-trigger', function () {
        $(this).closest('.js-editable-section').addClass('editing');
    }).on('blur', '.js-editable-trigger', function () {
        $(this).closest('.js-editable-section').removeClass('editing');
    });

    $('.js-upload-banner-logo').on('click', function(e) {
        $('#upload-banner-logo').trigger('click');
    });

    $('#upload-banner-logo').on('change', function() {
        var f = this.files[0],
            fileData = f,
            fileName = f.name,
            fileSize = f.size;

        if (this.files && fileData) {
            if (f.type.match('image.*')) {
                var readerUrl = new FileReader();
                readerUrl.onload = function (e) {
                    $('#banner-preview').attr('src', e.target.result);

                    watchOnDrag();
                };
                readerUrl.readAsDataURL(fileData);
            } else {
                // $('#banner-preview').attr('src', e.target.result).fadeIn();
            }
        }
    });

    var watchOnDrag = function() {
        var $banner = $('#banner-preview'),
            imgWidth = $banner.width(),
            imgHeight = $banner.height(),
            imgRatio = imgWidth / imgHeight,
            $container = $('.banner-logo'),
            contWidth = $container.width(),
            contHeight = $container.height(),
            contRatio = contWidth / contHeight;

        if (imgWidth < contWidth || imgHeight < contHeight) {
            console.warn('Too SMALL!!!!');
            return false;
        } else {
            $banner.addClass('in');

            var canvas = $('#canvas-banner-logo')[0],
                ctx = canvas.getContext('2d');

                console.log($('img#banner-preview'));
                ctx.drawImage($('img#banner-preview')[0], 0, 0, contWidth, contHeight);
        }


        var y1 = $('.banner-logo').height(),
            x1 = $('.banner-logo').width(),
            y2 = $('#banner-preview').height(),
            x2 = $('#banner-preview').width();



        $('#banner-preview').draggable({
            scroll: false,
            // axis: 'y',
            drag: function(event, ui) {
                if(ui.position.top >= 0) {
                    ui.position.top = 0;
                } else if( ui.position.top <= y1 - y2) {
                    ui.position.top = y1 - y2;
                }

                if( ui.position.left >= 0) {
                    ui.position.left = 0;
                } else if ( ui.position.left <= x1 - x2) {
                    ui.position.left = x1 - x2;
                }
            },
            stop: function(event, ui) {
                //####
            }
        });
    };

})(jQuery);
