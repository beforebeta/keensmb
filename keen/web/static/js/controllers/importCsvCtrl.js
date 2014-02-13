/*global FileAPI*/

'use strict';

angular.module('keen')
    .controller('importCsvCtrl', ['$scope', '$timeout', '$upload', '$http', 'customerListService', function($scope, $timeout, $upload, $http, customerService){
        var imScope = this,
            clientSlug = customerService.clientSlug;

        function init() {
            imScope.isWaiting = false;
            imScope.fileSelected = {};
            imScope.activeStep = 1;
        }
        init();

        $scope.globalAlert = false;
        var notify = function(text) {
            $timeout(function() {
                $scope.alertText = text;
                $scope.globalAlert = true;
            });
        };


        var selectedFile;
        imScope.onFileSelect = function($files) {
            var file = $files[0];

            if (file.type !== 'text/csv') {
                alert('wrong file type');
                return false;
            }

            var fileSize = (999999 >= file.size) ? Math.round(file.size / 1000) + ' KB' : Math.round(file.size / 100000)/10 + ' MB';
            imScope.fileSelected.size = fileSize;
            imScope.fileSelected.name = file.name;
            selectedFile = file;
        };

        imScope.uploadFile = function() {
            if (selectedFile) {
                imScope.isWaiting = true;
                $upload.upload({
                    url: '/api/client/'+clientSlug+'/customers/import',
                    method: 'POST',
                    // headers: {'headerKey': 'headerValue'},
                    // withCredential: true,
                    // data: {myObj: $scope.myModelObj},
                    file: selectedFile,
                    // file: $files, //upload multiple files, this feature only works in HTML5 FromData browsers
                    /* set file formData name for 'Content-Desposition' header. Default: 'file' */
                    //fileFormDataName: myFile, //OR for HTML5 multiple upload only a list: ['name1', 'name2', ...]
                    //formDataAppender: function(formData, key, val){} //#40#issuecomment-28612000
                }).progress(function(evt) {
                    // console.log('percent: ' + parseInt(100.0 * evt.loaded / evt.total));
                }).success(function(data, status, headers, config) {
                    console.log(data);

                    var reqId = data.import_requiest_id;
                    imScope.fileSelected.uploaded = true;

                    $timeout(function() {
                        $http({
                            method: 'GET',
                            url: '/api/client/'+ clientSlug +'/customers/import/'+reqId
                        }).then(function(res) {
                            imScope.isWaiting = false;
                            console.log('res: ', res);
                        });
                    }, 1000);
                });
            }
        };

        imScope.removeFile = function() {
            selectedFile = undefined;
            imScope.fileSelected = {};
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
