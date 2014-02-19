'use strict';

angular.module('keen')
    .factory('importCsv', ['$http','$q','$timeout','$upload', function($http, $q, $timeout, $upload) {

        var clientSlug = $('#clientSlug').text();

        return {
            getCustomersFields: function() {
                return $http({
                    url: '/api/client/'+clientSlug+'/customer_fields',
                    method: 'GET',
                    cache: true
                });
            },
            uploadFile: function(file) {
                var defer = $q.defer();

                $upload.upload({
                    url: '/api/client/'+clientSlug+'/customers/import',
                    method: 'POST',
                    file: file,
                })
                // .progress(function(evt) {
                //     console.log('percent: ' + parseInt(100.0 * evt.loaded / evt.total));
                // })
                .success(function(data, status, headers, config) {
                    defer.resolve(data);
                });

                return defer.promise;
            },
            uploadImportFields: function(fields, reqId, skipFirst) {
                var skipFirstRow = skipFirst ? 'yes' : false;

                return $http({
                    url: '/api/client/'+clientSlug+'/customers/import/'+reqId,
                    method: 'PUT',
                    data: {
                        skip_first_row: skipFirstRow,
                        import_fields: fields
                    }
                });
            },
            getStatus: function(reqId) {
                return $http({
                    method: 'GET',
                    url: '/api/client/default_client/customers/import/'+reqId
                });
            }
        };
    }]);
