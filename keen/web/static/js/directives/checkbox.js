'use strict';

angular.module('keen')
    .directive('checkboxik', [function(){
        // Runs during compile
        return {
            // priority: 0,
            link: function(scope, elm, attrs) {
                var content = angular.element('<label for="'+attrs.id+'">'+attrs.checkboxik+'</label>');
                content.insertAfter(elm);
            }
        };
    }]);
