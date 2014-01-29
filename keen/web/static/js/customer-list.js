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

            // var $fixedTop = $scrollFlex.children('.customers-table');
            var scrollFixedList = function() {
                var scrollTop = $scrollFixed.scrollTop();
                $scrollFlex.scrollTop(scrollTop);
                // $fixedTop.css('margin-top', -scrollTop);

                lazyScrollList();
            };

            // var $flexTop = $scrollFixed.children('.customers-table');
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

            $doc.on('click', '.global-alert .close', closeGlobalAlert);
            $win.on('resize', lazyCheckTableSize);

            $scrollFlex.hover(
                function() {$scrollFlex.on('scroll', scrollFlexList);},
                function() {$scrollFlex.off('scroll', scrollFlexList);}
            );

            $scrollFixed.hover(
                function() {$scrollFixed.on('scroll', scrollFixedList);},
                function() {$scrollFixed.off('scroll', scrollFixedList);}
            );

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
        }]).directive('checkboxik', [function(){
            // Runs during compile
            return {
                // priority: 0,
                link: function(scope, elm, attrs) {
                    var content = angular.element('<label for="'+attrs.id+'">'+attrs.checkboxik+'</label>');
                    content.insertAfter(elm);
                }
            };
        }]);

})(jQuery);
