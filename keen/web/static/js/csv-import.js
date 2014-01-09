// JS for profiles page
'use strict';

(function($) {
    $('#popup-ulpoad-csvfile').on('change', function(e){

        var files = FileAPI.getFiles(e),
            file = files[0],
            fileName = file.name,
            fileSize = file.size;

        $('.added-file span').text(fileName);
        $('.added-file strong').text('(' + fileSize + ')');

        if(999999 >= fileSize){
            $('.added-file strong').text(Math.round(fileSize / 1000) + 'KB');
        }
        else if (fileSize > 999999) {
            $('.added-file strong').text(Math.round(fileSize / 1000000) + 'MB');
        }

        $('.js-close').on('click', function() {
            $('.added-file span').empty();
            $('.added-file strong').empty();

            $('.added-file').hide();
        });

        if($('.added-file span').text() !== undefined){
            $('.added-file').show();
        }
    });
})(jQuery);
