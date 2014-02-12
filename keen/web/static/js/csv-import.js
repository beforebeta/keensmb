// /*global FileAPI */
// 'use strict';

// (function($) {
//     var clientSlug = $('#clientSlug').text();

//     var el = $('#popup-ulpoad-csvfile')[0];
//     FileAPI.event.on(el, 'change', function (evt){
//         var files = FileAPI.getFiles(evt);

//         // var xhr = FileAPI.upload({
//         //     url: '/api/client/'+clientSlug+'/customers/import',
//         //     files: { file: files[0] },
//         //     complete: function (err, xhr){
//         //         if( !err ){
//         //             var result = xhr.responseText;
//         //             console.log(result);
//         //         } else {
//         //             console.error(err);
//         //         }
//         //     }
//         // });

//         var formData = new FormData($('#import-form')[0]);
//         $.ajax({
//             url: '/api/client/'+clientSlug+'/customers/import',  //Server script to process data
//             type: 'POST',
//             // xhr: function() {  // Custom XMLHttpRequest
//             //     var myXhr = $.ajaxSettings.xhr();
//             //     if(myXhr.upload){ // Check if upload property exists
//             //         myXhr.upload.addEventListener('progress',progressHandlingFunction, false); // For handling the progress of the upload
//             //     }
//             //     return myXhr;
//             // },
//             //Ajax events
//             // beforeSend: beforeSendHandler,
//             success: function(data) {
//                 console.log(data);
//             },
//             // error: errorHandler,
//             // Form data
//             data: formData,
//             //Options to tell jQuery not to process data or worry about content-type.
//             cache: false,
//             contentType: false,
//             processData: false
//         });
//     });

//     $('#popup-ulpoad-csvfile').on('change', function(e){

//         var files = FileAPI.getFiles(e),
//             file = files[0],
//             fileName = file.name,
//             fileSize = file.size;

//         $('.added-file span').text(fileName);
//         $('.added-file strong').text('(' + fileSize + ')');

//         var size = (999999 >= fileSize) ? Math.round(fileSize / 1000) : Math.round(fileSize / 1000000);
//         $('.added-file strong').text(size + 'KB');

//         $('.js-close').on('click', function() {
//             $('.added-file span').empty();
//             $('.added-file strong').empty();

//             $('.added-file').hide();
//         });

//         if ($('.added-file span').text()){
//             $('.added-file').show();
//         }
//     });
// })(jQuery);
