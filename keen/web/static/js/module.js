'use strict';

angular.module('keen', ['ngSanitize']).run(['$http', function($http) {

    // Django csrf token for POST, PUT, DELETE
    $http.defaults.xsrfCookieName = 'csrftoken';
    $http.defaults.xsrfHeaderName = 'X-CSRFToken';

}]);
