'use strict';

angular.module('keen', ['ngTable', 'infinite-scroll']).run(['$http', function($http) {

    // Django csrf token for POST
    $http.defaults.xsrfCookieName = 'csrftoken';
    $http.defaults.xsrfHeaderName = 'X-CSRFToken';

}]);
