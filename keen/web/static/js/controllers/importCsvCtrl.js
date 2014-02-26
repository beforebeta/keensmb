'use strict';

angular.module('keen')
    .controller('importCsvCtrl', ['$scope', '$timeout', 'importCsv', 'customerListService', function($scope, $timeout, importCsv, customerService){
        var imScope = this;

        function init() {
            imScope.isWaiting = false;
            imScope.fileSelected = {
                uploadedPercent: 0
            };
            imScope.activeStep = 1;
            imScope.firstIsHeader = false;
            setAvailableFields();
            stopCheckingStatus = true;
        }

        imScope.select2Options = {
            containerCssClass: 'choose-field-container',
            dropdownCssClass: 'choose-field-dropdown',
            allowClear: true
        };

        function setAvailableFields() {
            customerService.getCustomersFields().then(function(res) {

                imScope.availableFields = _.map(res.data.available_customer_fields, function(field) {
                    return {
                        fieldTitle: field.title,
                        fieldName: field.name,
                        selected: false
                    };
                });

                imScope.requiredFields = _.chain(res.data.available_customer_fields)
                    .filter(function(field) {return field.required;})
                    .pluck('name')
                    .value();
            });
        }

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
                    console.log(data);
                    imScope.isWaiting = false;
                    imScope.fileSelected.uploaded = true;
                    imScope.fileSelected.uploadedPercent = 100;
                    imScope.activeReqId = data.import_requiest_id;

                    imScope.importFields = _.map(data.columns, function(column, i) {

                        return {
                            columnName: column,
                            sampleData: data.sample_data[i],
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
            // map -> returns destination values
            var fieldsColumns = _.pluck(imScope.importFields, 'destination');

            var filter = _.filter(imScope.requiredFields, function(field) {
                return !_.contains(fieldsColumns, field);
            });

            if (filter.length) {
                imScope.requiredTitles = true;
                return false;
            } else {
                imScope.requiredTitles = false;

                imScope.activeStep = 3;
                imScope.importStatus = {
                    status: 'uploading'
                };
                imScope.isWaiting = true;

                importCsv.uploadImportFields(fieldsColumns, imScope.activeReqId, imScope.firstIsHeader)
                    .then(function(data) {
                        imScope.importFieldsUploaded = true;

                        // imScope.importStatus = 'in_progress';

                        stopCheckingStatus = false;
                        getStatus();
                    });
            }

        };

        var stopCheckingStatus = false;
        var getStatus = function() {
            if (stopCheckingStatus) {return false;}

            importCsv.getStatus(imScope.activeReqId).then(function(res) {
                imScope.importStatus = res.data;

                if (res.data.status !== 'complete') {
                    $timeout(function() {
                        getStatus();
                    }, 1000);
                } else {
                    imScope.isWaiting = false;
                }
            });
        };

        imScope.resetForm = function() {
            $('#ModalCsvImport').modal('hide');
            $timeout(function() {init();}, 1000);
        };

        init();
    }]);
