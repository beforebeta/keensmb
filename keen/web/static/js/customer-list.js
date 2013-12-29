// JS for Customers list page

'use strict';

(function($) {
    angular.module('keen')
        .controller('customersCtrl', ['$scope', '$timeout', 'customerService', function($scope, $timeout, customerService){

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

            var customersToDelete = [],
                $toggleAllCheckbox = $('.tables-wrapper .toggle-all-customers :checkbox'),
                $itemActionsBlock = $('.js-item-selected');

            var checkItemActions = function() {
                var $customersTable = $customersList,
                    $checkboxes = $customersTable.find(':checkbox'),
                    $checked = $checkboxes.filter(':checked'),
                    checkedAny = ($checked.length !== 0);

                customersToDelete = [];
                $tablesWrapper.find('.selected-row').removeClass('selected-row');
                $checked.each(function(i, item) {
                    var customerId = $(item).closest('tr').data('id');
                    customersToDelete.push(customerId);
                    $tablesWrapper.find('tr[data-id='+customerId+']').addClass('selected-row');
                });

                $itemActionsBlock[checkedAny ? 'slideDown' : 'slideUp'](200);
                $toggleAllCheckbox.checkbox(checkedAny ? 'check' : 'uncheck');
            };

            var deleteCustomer = function() {

                _.each(customersToDelete, function(id, i) {
                    customerService.deleteCustomer(id).then(function(data) {
                        if (data.status === 200) {
                            var $targetBlock = $('[data-id='+id+']');
                            $targetBlock.remove();

                            if (i === customersToDelete.length-1) {
                                checkItemActions();
                                notify('Customers removed');
                            }
                        }
                    });
                });
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
                    checkItemActions();
                }, 100);
            };

            // Table: Toggle all checkboxes
            var toggleAllListCheckboxes = function() {
                var ch = $(this).find(':checkbox').prop('checked');
                $customersList.find('tbody :checkbox').checkbox(ch ? 'check' : 'uncheck');
                checkItemActions();
            };

            var $tablesWrapper = $('.tables-wrapper'),
                $scrollFlex = $('.js-list-flexible'),
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

            // Table: Add class row selected
            $doc.on('click', '.tables-wrapper .toggle-all-customers', toggleAllListCheckboxes);
            $doc.on('toggle', '.customers-list :checkbox', checkItemActions);
            $doc.on('click', '.js-delete-customer', deleteCustomer);
            $doc.on('click', '.global-alert .close', closeGlobalAlert);
            $scrollFlex.on('scroll', scrollFlexList);
            $win.on('resize', lazyCheckTableSize);
            // $scrollFixed.on('scroll', scrollFixedList);

        }]).factory('customerService', ['$http','$q','$timeout', function($http, $q, $timeout) {

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
