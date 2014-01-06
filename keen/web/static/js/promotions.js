(function ($) {

    $(function () {
        try {
            filepicker.setKey('AlEC17z10RIuLOpyhK2n2z');
        } catch (e) {
        }

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
                    //{"url":"https://www.filepicker.io/api/file/wrHrsBmdSzu1UsZ93GRo","filename":"13DIG001_LandingPage_Lunch%5b2%5d.jpg","mimetype":"image/jpeg","size":633510,"key":"6EycNbgRDy580JsRAB3y_13DIG001_LandingPage_Lunch%5b2%5d.jpg","container":"keensmb_uploads","isWriteable":true}
                    //console.log(JSON.stringify(blob));
                },
                function (FPError) {
                    console.log(FPError);
                }
            );
        });
    });

})(jQuery);