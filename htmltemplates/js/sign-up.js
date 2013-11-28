
// JS for SignUp page
'use strict';

(function($) {

    $('.instructions-wrap').on('selectstart, dragstart', function(e) {
        e.preventdefault();
    });

    $('.js-editable-section').on('focus', '.js-editable-trigger', function () {
        $(this).closest('.js-editable-section').addClass('editing');
    }).on('blur', '.js-editable-trigger', function () {
        $(this).closest('.js-editable-section').removeClass('editing');
    });

    $('#color-picker-anchor').chromoselector({
        panel: true,
        panelAlpha: true,
        panelMode: 'hsl',
        target: '.color-picker-wrapper',
        update: function () {
            console.log($(this).chromoselector('getColor').getHexString())
            // Show a preview in the background of the input element
            $('.background-image').css(
                'background-color',
                $(this).chromoselector('getColor').getHexString()
            );
        }
    });

    $('.js-upload-banner').on('change', function(evt) {

        var files = FileAPI.getFiles(evt), // Retrieve file list
            $container = $(this).closest('.js-image-container'),
            $imgEl = $container.find('.js-banner-preview'),
            contWidth = $container.width(),
            contHeight = $container.height();

        console.log('files: ', files);

        FileAPI.filterFiles(files, function (file, info){
            if( /^image/.test(file.type) ){
                if (info.width >= contWidth && info.height >= contHeight) {
                    return true;
                } else {
                    alert('too small');
                }
            }
            // return  false;
        }, function (files, rejected){
            console.log(files.length);
            if( files.length ){
                var file = files[0];
                FileAPI.Image(file).resize(contWidth, contHeight, 'min').get(function (err, img){

                    FileAPI.readAsDataURL(img, function (evt){
                        if( evt.type == 'load' ){
                            // Success
                            var dataURL = evt.result;
                            var url = img.toDataURL(file.type);

                            $imgEl.attr('src', dataURL).addClass('in');
                            $container.addClass('image-loaded');

                            var y1 = contHeight,
                                x1 = contWidth,
                                y2 = img.height,
                                x2 = img.width;

                            $imgEl.draggable({
                                scroll: false,
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
                        } else if( evt.type =='progress' ){
                            var pr = evt.loaded/evt.total * 100;
                        } else {
                            console.log('error');
                            // Error
                        }
                    });

                });

            }
        });
    });

    var watchOnDrag = function() {
    };

})(jQuery);
