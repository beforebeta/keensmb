$(function () {
    'use strict';

    if (window.filepicker) {filepicker.setKey('AlEC17z10RIuLOpyhK2n2z');}

    if (window.tinymce) {
        tinymce.init({
            selector: "textarea.tinymce",
            menubar: false,
            path: false,
            plugins: ['link image save'],
            toolbar: "undo redo | styleselect | bold italic underline | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image"
        });

        if ($('textarea.tinymce').siblings('.tinymce-content').length) {
            var content = $('textarea.tinymce').siblings('.tinymce-content').html();
            setTimeout(function() {
                tinyMCE.activeEditor.setContent(content);
            }, 35);
        }
    }

    var preview_promotion = function($button) {
        var location = $button.attr('data-location'),
            title = $button.attr("data-title"),
            $modal = $($button.attr('data-target')),
            $iframe = $modal.find("iframe"),
            $modal_title = $modal.find("h4.modal-title");

        $modal_title.text(title);
        $iframe.attr("src",location);
        $modal.modal('show');
    };

    var hash = window.location.hash;
    if (hash === '#preview') {
        preview_promotion($("#promotionPreviewTrigger"));
    }

    $('.previewPromotionBtn').click(function(){
        preview_promotion($(this));
    });

    // delete and approve
    $('.objIdTransferToModal').on('click', function(){
        var obj_id = $(this).attr('data-obj_id');
        var target_button_id = $(this).attr("data-targetBtn");
        $(target_button_id).attr('data-obj_id', obj_id);
    });

    $(document).on('click', '#promotionDeleteButton', function(){
        var $this = $(this);
        var obj_id = $this.attr('data-obj_id');
        $.ajax({
            type: "POST",
            url: $this.attr('data-location'),
            data: {"obj_id":obj_id},
            success: function (msg) {
                try{
                    if (msg["success"] == 0) {
                        alert(msg["msg"]);
                    }
                }catch(e){}
                window.location.reload();
            },
            error: function (msg) {
                alert("An error occurred!");
                window.location.reload();
            }
        });
    });

    $(document).on("click", '#promotionApproveButton', function(){
        var $this = $(this);
        var obj_id = $this.attr('data-obj_id');
        $.ajax({
            type: "POST",
            url: $this.attr('data-location'),
            data: {"obj_id":obj_id},
            success: function (msg) {
                $('#promotionApproveModal').modal('hide');
                try{
                    if (msg["success"] == 0) {
                        keen.showMessageModal("Promotion not approved!", msg["msg"]);
                    } else {
                        window.location = '/promotions/upcoming';
                    };
                }catch(e){}
            },
            error: function (msg) {
                keen.showMessageModal("An Error Occurred", "An error occurred while processing ");
            }
        });
    });

    $(document).on('click', '.filePickerUpload', function(){
        var $this = $(this);
        var $preview_image = $('#'+$this.attr('data-preview_image_id'));
        var $input_url = $('#'+$this.attr('data-image_input_id'));
        var conversion_params = $this.attr('data-conversion_params');
        $preview_image.attr('src','');
        $preview_image.hide();
        filepicker.pickAndStore({
                mimetypes: ['image/*'],
                container: 'modal',
                services: ['COMPUTER', 'FACEBOOK', 'GMAIL']
            }, {
                location:"S3"
            },
            function (InkBlobs) {
                var blob = InkBlobs[0];
                var final_url = blob["url"]+conversion_params;
                $preview_image.attr('src', final_url);
                $input_url.val(final_url);
                $preview_image.show();
            },
            function (FPError) {
                console.log(FPError);
            }
        );
    });

    $("input[data-label=later]").change(function () {
        var $send_later = $("input[data-label=later]");
        if($send_later.attr("checked") === "checked") {
            $('#send_later_row').show();
        } else {
            $('#send_later_row').hide();
        }
    });


// 'Target Your Audience' section
    var $sectionWrap = $('.promsection-segment-wrapper');

    $sectionWrap.find('.section-default').each(function() {

        var innerText =  $(this).find('.kn-section-header span').text(),
            data =  $(this).data('section-name'),
            $itemInList = $('.promotion-scroll-menu').prev('li').clone();

        $itemInList.attr('data-item', data);
        $itemInList.text(innerText);
        $itemInList.appendTo($('.promotion-scroll-menu')).show();
    });

    $('.js-prom-mock-item').on('click', function() {
        var $this = $(this),
            itemData = $this.data('item');

        if(!$this.hasClass('active')) {

            $this.addClass('active');

            $('.promotion-narrow-field').hide();
            $('.section-default').find('select').select2();

            $('.section-default').each(function() {

                var sectionData = $(this).data('section-name');

                if(itemData === sectionData) {
                    $(this).show();
                }
            });
        }
    });

    $sectionWrap.on('click', '.promotion-icon-close-height', function(){

        var $thisSection = $(this).closest('.section-default'),
            itemName = $thisSection.data('section-name');

        $('.js-prom-mock-item').each(function() {

            var $this = $(this),
                $dataItem = $this.data('item');

            if($dataItem === itemName) {
                $this.removeClass('active');
            }

        });

        $thisSection.hide();
        $thisSection.find('select').val('');

        if(!$sectionWrap.children('.section-default').length){
            $('.promotion-narrow-field').show();
        }
    });

    // Website promotions:

    if ($('#web-promotion-appearance').length) {

        var $tmplBlock = $('.tmpl-block'),   $bgColor = $('#bg-color'),
            $tmplHeader = $('.tmpl-header'), $headColor = $('#head-color'),
            $tmplText = $('.tmpl-text'),     $textColor = $('#text-color'),
            $tmplButton = $('.tmpl-button'), $btnColor = $('#btn-color');

        var updateColorPreview = function() {
            $tmplBlock.css({'background-color': $bgColor.val()});
            $tmplHeader.css({'color': $headColor.val()});
            $tmplText.css({'color': $textColor.val()});
            $tmplButton.css({'background-color': $btnColor.val()});
        };

        $('.color-pick').each(function(i, item) {
            var $item = $(item),
                $target = $item.parent();

            $item.chromoselector({
                target: $target,
                pickerClass: 'cs-static',
                autoshow: false,
                panel: true,
                panelMode: 'hsl',
                preview: true,
                resizable: false,
                speed: 0,
                create: updateColorPreview,
                update: updateColorPreview,
                hide: function(e) {
                    // dont hide on blur
                    $item.chromoselector('show', 0);
                }
            }).chromoselector('show', 0).chromoselector('resize', 120);
        });


        var createTemplatePlaceholders = function() {
            var mockExample = $('.tmpl-placeholder-mock').html();

            $('.tmpl-placeholder').hide().each(function(i, item) {
                var $item = $(item);
                $item.html(mockExample);

                $item.css({'background-color': $item.data('bg')});
                $item.find('.tmpl-header').css({color: $item.data('head')});
                $item.find('.tmpl-text').css({color: $item.data('txt')});
                $item.find('.tmpl-button').css({'background-color': $item.data('btn')});

                $item.fadeIn();
            });
        };

        var templateClickHandler = function() {
            var $this = $(this),
                bgColor = $this.data('bg'),
                headColor = $this.data('head'),
                textColor = $this.data('txt'),
                btnColor = $this.data('btn');

            $bgColor.val(bgColor).chromoselector('setColor', bgColor);
            $headColor.val(headColor).chromoselector('setColor', headColor);
            $textColor.val(textColor).chromoselector('setColor', textColor);
            $btnColor.val(btnColor).chromoselector('setColor', btnColor);

            updateColorPreview();

            $('.tmpl-placeholder').removeClass('active');
            $this.addClass('active');
        };


        createTemplatePlaceholders();
        $(document).on('click', '.tmpl-placeholder', templateClickHandler);

        if (!$('.tmpl-placeholder.active').length) {$('.tmpl-placeholder').eq(0).trigger('click')}
    }

});
