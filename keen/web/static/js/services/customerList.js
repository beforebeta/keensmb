'use strict';

angular.module('keen')
    .factory('customerListService', ['$http','$q','$timeout', function($http, $q, $timeout) {

        var clientSlug = $('#clientSlug').text(),
            itemsNumber = 50,
            currentOffset = -itemsNumber;

        return {
            clientSlug: clientSlug || '',
            limitData: itemsNumber,
            getClientData: function() {
                return $http({
                    url: '/api/client/current',
                    method: 'GET',
                    cache: true
                });
            },
            getCustomersFields: function() {
                return $http({
                    url: '/api/client/'+clientSlug+'/customer_fields',
                    method: 'GET',
                    cache: true
                });
            },
            putCustomersFields: function(fields) {
                return $http({
                    url: '/api/client/'+clientSlug+'/customer_fields',
                    method: 'PUT',
                    data: {display_customer_fields: fields}
                });
            },
            deleteCustomer: function(id) {
                return $http({
                    url: '/api/client/'+clientSlug+'/customer/'+id,
                    method: 'DELETE'
                });
            },
            getClientCustomers: function(fields, search, sort) {
                currentOffset += this.limitData;

                var params = {
                    fields: fields.join(','),
                    limit: this.limitData,
                    offset: currentOffset
                };

                if (search) {params.search = search;}
                if (sort) {params.order = sort;}

                return $http({
                    url: '/api/client/'+clientSlug+'/customers',
                    method: 'GET',
                    params: params,
                    cache: true
                });
            },
            resetCounter: function() {
                currentOffset = -this.limitData;
            },
            enrichCustomersData: function(customers) {
                return $http({
                    url: '/api/client/' + clientSlug + '/enrich',
                    method: 'POST',
                    data: {
                        customers: customers
                    }
                });
            }
        };
    }]);
