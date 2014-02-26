/* global filepicker, keen */
(function ($) {
    'use strict';

    if (window.filepicker) {filepicker.setKey('AlEC17z10RIuLOpyhK2n2z');}

    var preview_promotion = function($button) {
        var $this = $button;
        var location = $this.attr('data-location');
        var $modal = $($this.attr('data-target'));
        var $iframe = $($this.attr('data-target') + " iframe");
        var $modal_title = $($this.attr('data-target') + " h4.modal-title");
        $modal_title.text($this.attr("data-title"));
        $iframe.attr("src",location);
        $modal.modal({show:true});
    };

    var hash = window.location.hash;
    if (hash === '#preview') {
        preview_promotion($("#promotionPreviewTrigger"));
    }

    $('.previewPromotionBtn').click(function(){
        preview_promotion($(this));
    });

    // delete and approve
    $('.objIdTransferToModal').click(function(){
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
    var $sectionWrap = $('.promsection-segment-wrapper'),
        $defaultBanner = $('.promotion-narrow-field');

    if ($sectionWrap.length) {

        // select all options
        $sectionWrap.find('option').prop('selected', true);

        // generate menu items
        $sectionWrap.find('.section-default').each(function(i, item) {

            var $item = $(item),
                innerText =  $item.find('.kn-section-header span').text(),
                data =  $item.data('section-name'),
                $itemInList = $('.promotion-scroll-menu').prev('li').clone();

            $itemInList
                .attr('data-item', data)
                .text(innerText)
                .appendTo($('.promotion-scroll-menu'))
                .show();
        });

        // click on menu item handler
        $('.js-prom-mock-item').on('click', function() {
            var $this = $(this),
                itemData = $this.data('item');

            if(!$this.hasClass('active')) {

                $this.addClass('active');

                $('.section-default[data-section-name="'+itemData+'"]').show();

                if ($defaultBanner.is(':visible')) {
                    $defaultBanner.hide();
                    // deselect all options
                    $sectionWrap.find('option').prop('selected', false);
                }

                // reinitialize select2
                $('.section-default').find('select').select2();

                updateTargetCustomers();
            }

        });

        // close options
        $sectionWrap.on('click', '.promotion-icon-close-height', function(){

            var $thisSection = $(this).closest('.section-default'),
                itemName = $thisSection.data('section-name');

            $('.js-prom-mock-item.active[data-item='+itemName+']').removeClass('active');

            $thisSection.hide();
            $thisSection.find('select').val('');

            if(!$sectionWrap.children('.section-default:visible').length){
                $defaultBanner.show();
                $sectionWrap.find('option').prop('selected', true);
            }

            updateTargetCustomers();
        });

        var $targetCounter = $('.js-target-count');
        var updateTargetCustomers = function() {
            var selectedNum = $sectionWrap.children('.section-default:visible').length;
            $targetCounter.text(selectedNum);
        };
    }


})(jQuery);
