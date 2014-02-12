'use strict';

angular.module('keen')
    .controller('customerListCtrl', ['$scope', '$timeout', 'customerListService', function($scope, $timeout, customerService){

        $scope.globalAlert = false;
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
            checkTableSize();
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
                // var availableFields = data.data.available_customer_fields;

                var customerFields = data.data.display_customer_fields;
                $scope.customerFields = customerFields;

                updateOptionalFieldsList();

                tempFields = angular.copy(customerFields);

                $scope.loadMoreCustomers();
            });
        };

        var updateOptionalFieldsList = function() {
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
                // var customers = data.data.customers;

                // if (customers.length < customerService.limitData) {
                //     $scope.loadingDisabled = true;
                // }

                var customers = _.map(data.data.customers, function(val) {
                    return {
                        id: val.id,
                        data: val.data
                    };
                });

                if (!clearCustomers) {
                    $scope.customers = $scope.customers.concat(customers);
                } else {
                    scrollToTop();
                    $scope.customers = customers;
                    clearCustomers = false;
                }

                $scope.loadingDisabled = false;

                // initCheckbox();
            });
        };

        var updateFields = function() {
            var fields = _.union($scope.customerFields, $scope.requiredFieldsList);
            customerService.putCustomersFields(fields).then(function(data) {
                $scope.customerFields = data.data.display_customer_fields;
                updateOptionalFieldsList();
                resetList();
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

        var countSelected = function() {
            var customers = angular.copy($scope.customers);
            var selectedNumber = customers.length ? _.where(customers, {selected: true}).length : 0;

            return selectedNumber;
        };

        $scope.customersSelected = countSelected;


        $scope.markAll = function() {
            var state = ($scope.customersSelected() === $scope.customers.length);
            _.each($scope.customers, function(customer) {
                customer.selected = !state;
            });
        };

        $scope.deleteCustomers = function() {
            var selectedCustomers = _.where($scope.customers, {selected: true});

            _.each(selectedCustomers, function(customer, i) {
                customerService.deleteCustomer(customer.id).then(function(data) {
                    if (data.status === 200) {
                        if (i === selectedCustomers.length-1) {
                            customersDeletedSuccess();
                        }

                    } else {
                        notify('Some error occured while deleting customer '+customer.id);
                    }
                });
            });

            var customersDeletedSuccess = function() {
                $scope.customers = _.difference($scope.customers, selectedCustomers);
                notify(selectedCustomers.length + ' selected Customers removed');

                if (!$scope.customers.length) {
                    $scope.loadMoreCustomers();
                } else if ($scope.customers.length < customerService.limitData) {
                    scrollList();
                }
            };
        };

        $scope.enrichCustomersData = function() {
            var $modal = $('#enrichModal'), selectedIDs = _.map(
                _.where($scope.customers, {selected: true}),
                function(customer) {
                    return customer.id;
                });

            customerService.enrichCustomersData(selectedIDs).then(
                function success(response) {
                    // It's not recommended to do any DOM manipulation
                    // in controller but that's the easiest way to make job done.
                    // Beside this will be changed anyway
                    $modal.modal('show');
                },
                function failure(response) {
                }
            );
        };

        var closeGlobalAlert = function(e) {
            e.preventDefault();
            var $alertBlock = $(this).closest('.global-alert');
            $alertBlock.removeClass('in').hide();
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

        var scrollFixedList = function() {
            var scrollTop = $scrollFixed.scrollTop();

            // TODO: bad sulution, but its working... will think about perfomance later
            $scrollFlex.off('scroll', scrollFlexList);
            $scrollFlex.scrollTop(scrollTop);
            $scrollFlex.on('scroll', scrollFlexList);

            lazyScrollList();
        };

        var scrollFlexList = function() {
            var scrollTop = $scrollFlex.scrollTop();

            // TODO: bad sulution, but its working... will think about perfomance later
            $scrollFixed.off('scroll', scrollFixedList);
            $scrollFixed.scrollTop(scrollTop);
            $scrollFixed.on('scroll', scrollFixedList);

            lazyScrollList();
        };

        var $doc = $(document),
            $win = $(window);

        var $customersPageContent = $('.customers-page-content'),
            noContentHeight = $('.kn-nav').outerHeight() + $('.kn-footer').outerHeight(),
            defaultListHeight = $scrollFlex.height(),
            $scrollBlocks = $scrollFlex.add($scrollFixed);

        var checkTableSize = function() {
            var contentHeight = $customersPageContent.outerHeight(),
                contentWrapperHeight = $win.outerHeight() - noContentHeight,
                curentHeight = $scrollFlex.height(),
                diff = contentWrapperHeight - contentHeight;

            var height = curentHeight + diff;
            if (height >= defaultListHeight) {
                $scrollBlocks.height(height);
            }
        };

        var lazyCheckTableSize = _.debounce(checkTableSize, 200);

        $scrollFlex.on('scroll', scrollFlexList);
        $scrollFixed.on('scroll', scrollFixedList);

        $doc.on('click', '.global-alert .close', closeGlobalAlert);
        $win.on('resize', lazyCheckTableSize);

    }])
