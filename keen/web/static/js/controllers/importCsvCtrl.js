/*global FileAPI*/

'use strict';

angular.module('keen')
    .controller('importCsvCtrl', ['$scope', '$timeout', '$upload', '$http', 'importCsv', 'customerListService', function($scope, $timeout, $upload, $http, importCsv, customerService){
        var imScope = this;

        function init() {
            imScope.isWaiting = false;
            imScope.fileSelected = {};
            imScope.activeStep = 1;
        }
        init();

        customerService.getCustomersFields().then(function(res) {
            var availableFields = _.map(res.data.available_customer_fields, function(field) {
                return {
                    fieldName: field.title,
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

        imScope.activeReqId = 0;
        imScope.uploadFile = function() {
            if (selectedFile) {
                imScope.isWaiting = true;
                importCsv.uploadFile(selectedFile).then(function(data) {
                    imScope.isWaiting = false;
                    imScope.fileSelected.uploaded = true;

                    console.log(data);

                    imScope.activeReqId = data.import_requiest_id;

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

            importCsv.uploadImportFields(imScope.importFields, imScope.activeReqId, imScope.firstIsHeader)
                .then(function(data) {
                    imScope.isWaiting = false;
                    imScope.importFieldsUploaded = true;

                    imScope.importStatus = 'in_progress';

                    getStatus();
                });
        };

        var n = 0;
        var getStatus = function() {
            // check 10 sec only;
            if (n >= 10) {return false;}
            n += 1;

            $http({
                method: 'GET',
                url: '/api/client/default_client/customers/import/'+imScope.activeReqId
            }).then(function(res) {
                imScope.importStatus = res.data.status;

                if (res.data.status !== 'done') {
                    $timeout(function() {
                        getStatus();
                    }, 1000);
                }
                console.log('res: ', res);
            });
        };

        imScope.resetForm = function() {
            $('#ModalCsvImport').modal('hide');
            $timeout(function() {init();}, 1000);
        };

    }]);
