'use strict';

angular.module('keen', ['ngSanitize', 'pasvaz.bindonce', 'ui.select2', 'angularFileUpload']).run(['$http', function($http) {

    // Django csrf token for POST, PUT, DELETE
    $http.defaults.xsrfCookieName = 'csrftoken';
    $http.defaults.xsrfHeaderName = 'X-CSRFToken';

}]);
