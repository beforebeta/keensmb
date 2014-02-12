/*global FileAPI*/

'use strict';

angular.module('keen')
    .controller('importCsvCtrl', ['$scope', '$timeout', '$upload', 'customerListService', function($scope, $timeout, $upload, customerService){
        var imScope = this,
            clientSlug = customerService.clientSlug;

        $scope.globalAlert = false;
        var notify = function(text) {
            $timeout(function() {
                $scope.alertText = text;
                $scope.globalAlert = true;
            });
        };

        imScope.importFileChanged = function(e) {
            console.log(e);
        };

        imScope.onFileSelect = function($files) {
            var formData = new FormData($('#import-form')[0]);
            $.ajax({
                url: '/api/client/'+clientSlug+'/customers/import',  //Server script to process data
                type: 'POST',
                // xhr: function() {  // Custom XMLHttpRequest
                //     var myXhr = $.ajaxSettings.xhr();
                //     if(myXhr.upload){ // Check if upload property exists
                //         myXhr.upload.addEventListener('progress',progressHandlingFunction, false); // For handling the progress of the upload
                //     }
                //     return myXhr;
                // },
                //Ajax events
                // beforeSend: beforeSendHandler,
                success: function(data) {
                    console.log(data);
                },
                // error: errorHandler,
                // Form data
                data: formData,
                //Options to tell jQuery not to process data or worry about content-type.
                cache: false,
                contentType: false,
                processData: false
            });


            var file = $files[0];
            $upload.upload({
                url: '/api/client/'+clientSlug+'/customers/import',
                method: 'POST',
                // headers: {'headerKey': 'headerValue'},
                // withCredential: true,
                // data: {myObj: $scope.myModelObj},
                file: file,
                // file: $files, //upload multiple files, this feature only works in HTML5 FromData browsers
                /* set file formData name for 'Content-Desposition' header. Default: 'file' */
                //fileFormDataName: myFile, //OR for HTML5 multiple upload only a list: ['name1', 'name2', ...]
                //formDataAppender: function(formData, key, val){} //#40#issuecomment-28612000
            }).progress(function(evt) {
                console.log('percent: ' + parseInt(100.0 * evt.loaded / evt.total));
            }).success(function(data, status, headers, config) {
                console.log(data);
            });
        };
        // FileAPI.event.on(el, 'change', function (evt){
        //     var files = FileAPI.getFiles(evt);

            // var xhr = FileAPI.upload({
            //     url: '/api/client/'+clientSlug+'/customers/import',
            //     files: { file: files[0] },
            //     complete: function (err, xhr){
            //         if( !err ){
            //             var result = xhr.responseText;
            //             console.log(result);
            //         } else {
            //             console.error(err);
            //         }
            //     }
            // });
        // });

    }]);
