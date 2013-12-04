// JS for Customers list page

'use strict';

(function($) {
    angular.module('keen')
        .controller('customersCtrl', ['$scope', '$timeout', 'customerService', 'ngTableParams', function($scope, $timeout, customerService, ngTableParams){

            $scope.submitSearch = function() {
                resetList();
            };

            var clearCustomers = false;
            function resetList() {
                console.log('reset');
                // $scope.customers = [];
                clearCustomers = true;
                customerService.resetCounter();
                $scope.loadMoreCustomers();
            }

            customerService.getClientData().then(function(data) {
                var customerFields = data.data.customer_fields;

                $scope.customerFields = [
                    {name: 'first_name', title: 'First Name'},
                    {name: 'last_name', title: 'Last Name'},
                    {name: 'email', title: 'Email Address'},
                    {name: 'age', title: 'Age'},
                    {name: 'gender', title: 'Gender'},
                ];

            });

            customerService.getCustomersFields().then(function(data) {
                var availableFields = data.data.available_customer_fields;

                console.log('availableFields: ', availableFields);

                $scope.availableFields = availableFields;

                // availableFields.length = 3;
                var arr = [];

                angular.forEach(availableFields, function(field, i) {
                    arr.push(field.name);
                });

                arr.length = 3;

                // customerService.putCustomersFields(arr).then(function(data) {
                //     console.log('put: ', data);
                // });
            });

            $scope.loadingDisabled = false;

            $scope.customers = [];
            $scope.searchParam = '';
            // TODO: hardcoded
            var fields = ['first_name','last_name','email', 'age', 'gender'];

            $scope.sortBy = function(name) {
                $scope.activeSort = name;

                if ($scope.sortParam == name) {
                    $scope.sortParam = '-' + name;
                } else {
                    $scope.sortParam = name;
                }
                resetList();
            };
            $scope.loadMoreCustomers = function() {
                console.log('se ', $scope.searchParam)

                customerService.getClientCustomers(fields, $scope.searchParam, $scope.sortParam).then(function(data) {
                    console.log('more: ', data.data);
                    var customers = data.data.customers;

                    // TODO hardcoded limit
                    if (customers.length < 50) {
                        $scope.loadingDisabled = true;
                    }

                    if (!clearCustomers) {
                        $scope.customers = $scope.customers.concat(customers);
                    } else {
                        $scope.customers = customers;
                        clearCustomers = false;
                    }

                    initCheckbox();
                });
            };

            var checkItemActions = function() {
                var $customersTable = $('#customers-table'),
                    checkboxes = $customersTable.find(':checkbox'),
                    checkedAny = (checkboxes.filter(':checked').length !== 0);

                $('.js-item-selected')[checkedAny ? 'slideDown' : 'slideUp'](200);
            };

            var deleteCustomer = function() {

                // do ajax call here, with callback:

                $('.js-customer-deleted-name').text('John Smith');
                $('.customer-deleted-alert').show().addClass('in');
            };

            var closeGlobalAlert = function(e) {
                e.preventDefault();
                var $alertBlock = $(this).closest('.global-alert');
                $alertBlock.removeClass('in').hide();
            };

            var initCheckbox =  function () {
                setTimeout(function() {
                    $('[data-toggle="checkbox"]').each(function () {
                        var $checkbox = $(this);
                        $checkbox.checkbox();
                    });
                }, 100);
            };


            // Table: Add class row selected
            $(document).on('toggle', '#customers-table :checkbox', checkItemActions);
            $(document).on('click', '.js-delete-customer', deleteCustomer);
            $(document).on('click', '.global-alert .close', closeGlobalAlert);

        }]).factory('customerService', ['$http', function($http) {

            window.$http = $http;

            var clientSlug = $('#clientSlug').text(),
                // TODO: fix
                currentOffset = -50,
                limit = 50;

            return {
                getClientData: function() {
                    return $http({
                        url: '/api/client/'+clientSlug,
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
                    var fieldsString = fields.join(',');

                    return $http({
                        url: '/api/client/'+clientSlug+'/customer_fields',
                        method: 'PUT',
                        data: {display_customer_fields: fieldsString}
                    });
                },
                getClientCustomers: function(fields, search, sort) {
                    currentOffset += limit;

                    var params = {
                        fields: fields.join(','),
                        limit: limit,
                        offset: currentOffset
                    };

                    if (search) {
                        params.search = search;
                        params.offset = 0;
                    }

                    if (sort) {
                        params.order = sort;
                        params.offset = 0;
                    }

                    return $http({
                        url: '/api/client/'+clientSlug+'/customers',
                        method: 'GET',
                        params: params,
                        cache: true
                    });
                },
                resetCounter: function() {
                    currentOffset = -50;
                }
            };
        }]);

})(jQuery);
