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
                clearCustomers = true;
                customerService.resetCounter();
                $scope.loadMoreCustomers();
            }

            customerService.getClientData().then(function(data) {
                var customerFields = data.data.customer_fields;

                var fieldsMap = {};
                _.each(customerFields, function(item) {
                    fieldsMap[item.name] = item.title;
                });

                $scope.fieldsMap = fieldsMap;
            });

            customerService.getCustomersFields().then(function(data) {
                var availableFields = data.data.available_customer_fields;
                console.table(availableFields)

                $scope.availableFields = availableFields;
                $scope.customerFields = data.data.display_customer_fields;

                // var arr = ['first_name', 'last_name', 'email'];

                $scope.loadMoreCustomers();
            });

            $scope.loadingDisabled = false;

            $scope.customers = [];
            $scope.searchParam = '';
            // TODO: hardcoded
            // var fields = ['first_name','last_name','email', 'age', 'gender'];

            $scope.sortBy = function(name) {
                $scope.activeSort = name;

                if ($scope.sortParam === name) {
                    $scope.sortParam = '-' + name;
                } else {
                    $scope.sortParam = name;
                }
                resetList();
            };
            $scope.loadMoreCustomers = function() {
                if (!$scope.customerFields) {return false};
                customerService.getClientCustomers($scope.customerFields, $scope.searchParam, $scope.sortParam).then(function(data) {
                    console.log('more: ', data.data);
                    var customers = data.data.customers;

                    // TODO hardcoded limit
                    if (customers.length < 50) {
                        $scope.loadingDisabled = true;
                    }

                    if (!clearCustomers) {
                        $scope.customers = $scope.customers.concat(customers);
                    } else {
                        scrollToTop();
                        $scope.customers = customers;
                        clearCustomers = false;
                    }

                    initCheckbox();
                });
            };

            var updateFields = function() {
                customerService.putCustomersFields($scope.customerFields).then(function(data) {
                    $scope.customerFields = data.data.display_customer_fields;
                    resetList();
                });
            };

            $scope.addField = function(name) {
                if (!$scope.checkField(name)) {
                    $scope.customerFields.push(name);
                    updateFields();
                }
            };
            $scope.removeField = function(name) {
                if ($scope.checkField(name)) {
                    $scope.customerFields = _.without($scope.customerFields, name);
                    updateFields();
                }
            };

            $scope.checkField = function(name) {
                return _.contains($scope.customerFields, name);
            };

            var scrollToTop = function() {
                $(window).scrollTop(0);
            };

            var checkItemActions = function() {
                var $customersTable = $('.customers-list'),
                    checkboxes = $customersTable.find(':checkbox'),
                    checkedAny = (checkboxes.filter(':checked').length !== 0);

                $('.js-item-selected')[checkedAny ? 'slideDown' : 'slideUp'](200);
                $('.customers-list .customers-table')[checkedAny ? 'addClass' : 'removeClass']('space-top');
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

            // Table: Toggle all checkboxes
            var toggleAllListCheckboxes = function() {
                var ch = $(this).find(':checkbox').prop('checked');
                $('.customers-list').find('tbody :checkbox').checkbox(ch ? 'check' : 'uncheck');
                checkItemActions();
            };

            // Table: Add class row selected
            $(document).on('click', '.table .toggle-all-customers', toggleAllListCheckboxes);
            $(document).on('toggle', '.customers-table :checkbox', checkItemActions);
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
                    return $http({
                        url: '/api/client/'+clientSlug+'/customer_fields',
                        method: 'PUT',
                        data: {display_customer_fields: fields}
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
