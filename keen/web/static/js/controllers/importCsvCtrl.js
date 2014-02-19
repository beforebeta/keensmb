/*global FileAPI*/

'use strict';

angular.module('keen')
    .controller('importCsvCtrl', ['$scope', '$timeout', '$upload', '$http', 'importCsv', 'customerListService', function($scope, $timeout, $upload, $http, importCsv, customerService){
        var imScope = this;

        function init() {
            imScope.isWaiting = false;
            imScope.fileSelected = {
                uploadedPercent: 0
            };
            imScope.activeStep = 1;
        }
        init();

        customerService.getCustomersFields().then(function(res) {
            var availableFields = _.map(res.data.available_customer_fields, function(field) {
                return {
                    fieldTitle: field.title,
                    fieldName: field.name,
                    selected: false
                };
            });
            imScope.availableFields = availableFields;
            // imScope.availableFields = res.data.available_customer_fields;
        });

        imScope.selectField = function() {
            var selectedFields = _.chain(imScope.importFields)
                .filter(function(field) {return field.destination;})
                .map(function(field) {return field.destination;})
                .value();

            _.each(imScope.availableFields, function(item) {
                item.selected = _.contains(selectedFields, item.fieldName) ? true : false;
            });
        };

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

        var incrUploadedPercent = function() {
            if (imScope.fileSelected.uploaded) {return false;}

            $timeout(function() {
                var per = imScope.fileSelected.uploadedPercent;

                if (per === 0) {
                    imScope.fileSelected.uploadedPercent = 10;
                } else {
                    imScope.fileSelected.uploadedPercent = per+Math.floor((100-per)/10);
                }

                incrUploadedPercent();
            }, 300);
        };
        imScope.activeReqId = 0;
        imScope.uploadFile = function() {
            if (selectedFile) {
                imScope.isWaiting = true;

                imScope.fileSelected.uploadedPercent = 1;
                incrUploadedPercent();
                importCsv.uploadFile(selectedFile).then(function(data) {
                    imScope.isWaiting = false;
                    imScope.fileSelected.uploaded = true;
                    imScope.fileSelected.uploadedPercent = 100;
                    imScope.activeReqId = data.import_requiest_id;

                    // console.log(data);
                    imScope.importFields = _.map(data.columns, function(column) {
                        return {
                            columnName: column,
                            destination: ''
                        };
                    });
                });
            }
        };

        // For testing 2 step:
        // imScope.importFields = _.map(["Full Name","First Name","Last Name","Middle Name","DOB","Email","Phone Number","Zip","Source","Parallax"], function(column) {
        //     return {
        //         columnName: column,
        //         destination: ''
        //     };
        // });
        // imScope.activeStep = 2;


        imScope.removeFile = function() {
            selectedFile = undefined;
            imScope.fileSelected = {};
        };

        imScope.uploadImportFields = function() {
            imScope.activeStep = 3;
            imScope.importStatus = 'uploading';
            imScope.isWaiting = true;

            // map -> returns destination values
            var fieldsColumns = _.pluck(imScope.importFields, 'destination');

            importCsv.uploadImportFields(fieldsColumns, imScope.activeReqId, imScope.firstIsHeader)
                .then(function(data) {
                    imScope.isWaiting = false;
                    imScope.importFieldsUploaded = true;

                    imScope.importStatus = 'in_progress';

                    n = 0;
                    getStatus();
                });
        };

        var n = 0;
        var getStatus = function() {
            // check 10 sec only;
            if (n >= 10) {return false;}
            n += 1;

            importCsv.getStatus(imScope.activeReqId).then(function(res) {
                imScope.importStatus = res.data.status;

                if (res.data.status !== 'done') {
                    $timeout(function() {
                        getStatus();
                    }, 1000);
                }
            });
        };

        imScope.resetForm = function() {
            $('#ModalCsvImport').modal('hide');
            $timeout(function() {init();}, 1000);
        };

    }]);
