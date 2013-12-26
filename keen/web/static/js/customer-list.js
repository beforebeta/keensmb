// JS for Customers list page

'use strict';

(function($) {
    angular.module('keen')
        .controller('customersCtrl', ['$scope', '$timeout', 'customerService', function($scope, $timeout, customerService){

            var notify = function(text) {
                $timeout(function() {
                    $scope.alertText = text;
                    $scope.globalAlert = true;
                });
            };

            customerService.getClientData().then(function(data) {
                var customerFields = data.data.customer_fields,
                    slug = data.data.slug;

                var fieldsMap = {};
                _.each(customerFields, function(item) {
                    fieldsMap[item.name] = {};
                    fieldsMap[item.name].title = item.title;
                    fieldsMap[item.name].width = item.width;
                });

                var optionalFieldsMap = {},
                    optionalFields = _.where(customerFields, {required: false});

                _.each(optionalFields, function(item) {
                    optionalFieldsMap[item.name] = item.title;
                });

                var requiredFieldsMap = {},
                    requiredFieldsList = [],
                    requiredFields = _.where(customerFields, {required: true});

                _.each(requiredFields, function(item) {
                    requiredFieldsMap[item.name] = item.title;
                    requiredFieldsList.push(item.name);
                });

                $scope.fieldsMap = fieldsMap;
                $scope.requiredFieldsList = requiredFieldsList;
                $scope.requiredFieldsMap = requiredFieldsMap;

                $scope.optionalFieldsMap = optionalFieldsMap;

                customerService.clientSlug = slug;

                initCustomersFields();
            });

            $scope.submitSearch = function() {
                resetList();
            };

            var clearCustomers = false;
            function resetList() {
                clearCustomers = true;
                customerService.resetCounter();
                $scope.loadMoreCustomers();
            }

            var tempFields = [];
            var initCustomersFields = function() {
                customerService.getCustomersFields().then(function(data) {
                    var availableFields = data.data.available_customer_fields;

                    var customerFields = data.data.display_customer_fields;
                    $scope.customerFields = customerFields;

                    updateOtionalFieldsList();

                    tempFields = angular.copy(customerFields);

                    $scope.loadMoreCustomers();
                });
            };

            var updateOtionalFieldsList = function() {
                var optionalFieldsList = _.difference($scope.customerFields, $scope.requiredFieldsList);
                $scope.optionalFieldsList = optionalFieldsList;
            };

            $scope.loadingDisabled = false;

            $scope.customers = [];
            $scope.searchParam = '';

            $scope.sortByAs = function(name) {
                if ($scope.sortParam === name) {return false;}

                $scope.activeSort = name;
                $scope.sortParam = name;

                resetList();
            };

            $scope.sortByDes = function(name) {
                if ($scope.sortParam === '-' + name) {return false;}

                $scope.activeSort = name;
                $scope.sortParam = '-' + name;

                resetList();
            };

            $scope.checkActiveSort = function(field) {
                if ($scope.sortParam === '-' + field) {
                    return true;
                }
            };

            $scope.loadMoreCustomers = function() {
                if (!$scope.customerFields) {return false;}

                if ($scope.loadingDisabled) {return false;}

                $scope.loadingDisabled = true;

                customerService.getClientCustomers($scope.customerFields, $scope.searchParam, $scope.sortParam).then(function(data) {
                    var customers = data.data.customers;

                    // TODO hardcoded limit
                    if (customers.length < customerService.limitData) {
                        $scope.loadingDisabled = true;
                    }

                    if (!clearCustomers) {
                        $scope.customers = $scope.customers.concat(customers);
                    } else {
                        scrollToTop();
                        $scope.customers = customers;
                        clearCustomers = false;
                    }

                    $scope.loadingDisabled = false;

                    initCheckbox();
                });
            };

            var updateFields = function() {
                var fields = _.union($scope.customerFields, $scope.requiredFieldsList);
                customerService.putCustomersFields(fields).then(function(data) {
                    $scope.customerFields = data.data.display_customer_fields;
                    updateOtionalFieldsList();
                    resetList();
                    checkItemActions();
                });
            };

            $scope.addField = function(name) {
                if (!$scope.checkField(name)) {
                    tempFields.push(name);
                }
            };
            $scope.removeField = function(name) {
                if ($scope.checkField(name)) {
                    tempFields = _.without(tempFields, name);
                }
            };
            $scope.removeColumn = function(name) {
                $scope.removeField(name);
                $scope.doneAddingFields();
            };
            $scope.doneAddingFields = function() {
                $scope.customerFields = angular.copy(tempFields);
                updateFields();
            };
            $scope.cancelAddingFields = function() {
                tempFields = angular.copy($scope.customerFields);
            };

            $scope.checkField = function(name) {
                return _.contains(tempFields, name);
            };

            var $customersList = $('.customers-list');
            var scrollToTop = function() {
                $customersList.scrollTop(0);
            };

            var customersToDelete = [];
            var checkItemActions = function() {
                console.log('check');
                var $customersTable = $customersList,
                    $checkboxes = $customersTable.find(':checkbox'),
                    $checked = $checkboxes.filter(':checked'),
                    checkedAny = ($checked.length !== 0);

                customersToDelete = [];
                $checked.each(function(i, item) {
                    customersToDelete.push($(item).closest('tr').data('id'));
                });

                $('.js-item-selected')[checkedAny ? 'slideDown' : 'slideUp'](200);
            };

            var deleteCustomer = function() {

                _.each(customersToDelete, function(id) {
                    customerService.deleteCustomer(id).then(function(data) {
                        if (data.status === 200) {
                            var $targetBlock = $('[data-id='+id+']');
                            $targetBlock.fadeOut('fast', function() {
                                $targetBlock.remove();
                            });
                            checkItemActions();

                            notify('Customers removed');
                        }
                    });
                });

                // $('.js-customer-deleted-name').text('John Smith');
                // $('.customer-deleted-alert').show().addClass('in');
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
                $customersList.find('tbody :checkbox').checkbox(ch ? 'check' : 'uncheck');
                checkItemActions();
            };

            var $scrollFlex = $('.js-list-flexible'),
                $scrollFixed = $('.js-list-fixed');

            var scrollList = function() {
                var raw = $scrollFlex[0];

                if (raw.scrollTop + raw.offsetHeight >= raw.scrollHeight - 500) {
                    $timeout(function() {
                        $scope.loadMoreCustomers();
                    });
                }
            };
            var lazyScrollList = _.throttle(scrollList, 200);

            var $fixedTop = $scrollFlex.children('.customers-table');
            var scrollFixedList = function() {
                var scrollTop = $scrollFixed.scrollTop();
                // $scrollFlex.scrollTop(scrollTop);
                // $fixedTop.css('margin-top', -scrollTop);

                // lazyScrollList();
            };
            var $flexTop = $scrollFixed.children('.customers-table');
            var scrollFlexList = function() {
                var scrollTop = $scrollFlex.scrollTop();
                $scrollFixed.scrollTop(scrollTop);
                // $flexTop.css('margin-top', -scrollTop);

                lazyScrollList();
            };

            // Table: Add class row selected
            $(document).on('click', '.table .toggle-all-customers', toggleAllListCheckboxes);
            $(document).on('toggle', '.customers-table :checkbox', checkItemActions);
            $(document).on('click', '.js-delete-customer', deleteCustomer);
            $(document).on('click', '.global-alert .close', closeGlobalAlert);
            $scrollFlex.on('scroll', scrollFlexList);
            // $scrollFixed.on('scroll', scrollFixedList);
            $('.tables-wrapper').on('scroll', function() {
                console.log('scroll');
            });

        }]).factory('customerService', ['$http','$q','$timeout', function($http, $q, $timeout) {

            window.$http = $http;

            var clientSlug = $('#clientSlug').text(),
                itemsNumber = 50,
                currentOffset = -itemsNumber;

            return {
                clientSlug: '',
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
                }
            };
        }]);

})(jQuery);
