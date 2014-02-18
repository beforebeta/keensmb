/*global FileAPI*/

'use strict';

angular.module('keen')
    .controller('importCsvCtrl', ['$scope', '$timeout', '$upload', '$http', 'importCsv', function($scope, $timeout, $upload, $http, importCsv){
        var imScope = this;

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

        imScope.activeReqId = 0;
        imScope.uploadFile = function() {
            if (selectedFile) {
                imScope.isWaiting = true;
                importCsv.uploadFile(selectedFile).then(function(data) {
                    imScope.isWaiting = false;
                    imScope.fileSelected.uploaded = true;

                    console.log(data);

                    imScope.activeReqId = data.import_requiest_id;

                    imScope.importFields = data.import_fields;
                });
            }
        };

        imScope.removeFile = function() {
            selectedFile = undefined;
            imScope.fileSelected = {};
        };

        imScope.uploadImportFields = function() {
            imScope.activeStep = 3;
            imScope.importStatus = 'uploading';
            imScope.isWaiting = true;

            importCsv.uploadImportFields(imScope.importFields, imScope.activeReqId).then(function(data) {
                imScope.isWaiting = false;
                imScope.importFieldsUploaded = true;

                imScope.importStatus = 'Success!';
                console.log(data);

                $timeout(function() {
                    $http({
                        method: 'GET',
                        url: '/api/client/default_client/customers/import/'+imScope.activeReqId
                    }).then(function(res) {
                        imScope.isWaiting = false;
                        console.log('res: ', res);
                    });
                }, 1000);

            });
        };
        imScope.resetForm = function() {
            $('#ModalCsvImport').modal('hide');
            $timeout(function() {init();}, 1000);
        };

    }]);
