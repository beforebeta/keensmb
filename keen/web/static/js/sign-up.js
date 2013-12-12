
// JS for SignUp page
'use strict';

(function($) {
    angular.module('keen').controller('signUpCtrl', ['$scope', '$timeout', 'signUpFormService', function($scope, $timeout, suService){

        suService.getClienImages().then(function(data) {
            console.log(data);
        });

        // Initial data:

        $scope.title = {text: 'some title', isEditing: false};
        $scope.permalink = {text: 'some-perma-link', isEditing: false};
        var tempData;
        $scope.startEditing = function(item) {
            tempData = angular.copy(item.text);
            item.isEditing = true;
        };
        $scope.cancelEditing = function(item) {
            item.text = tempData;
            item.isEditing = false;
        };
        $scope.saveEditing = function(item) {
            item.isEditing = false;
        };

        var lastBannerLogo = {
            image: {
                src: '',
                // src: 'http://static.freepik.com/free-photo/fantasy-banner_8479.jpg',
                top: 0,
                left: 0
            },
            uploaded: false,
            reposition: false,
            editing: false,
        };

        $scope.bannerLogo = angular.copy(lastBannerLogo);
        $scope.saveEditingBanner = function() {
            stopEditingBanner();
            lastBannerLogo = angular.copy($scope.bannerLogo);
        };
        $scope.cancelEditingBanner = function() {
            stopEditingBanner();
            $scope.bannerLogo = angular.copy(lastBannerLogo);
        };
        function startEditingBanner() {
            $scope.bannerLogo.editing = true;
            $('.banner-logo .js-banner-preview').draggable('enable');
        }
        function stopEditingBanner() {
            $scope.bannerLogo.editing = false;
            $('.banner-logo .js-banner-preview').draggable('disable');
        }

        $scope.bgImage = {
            uploaded: false,
            reposition: false
        };


        $('.instructions-wrap').on('selectstart, dragstart', function(e) {
            e.preventdefault();
        });

        $('.js-editable-section').on('focus', '.js-editable-trigger', function () {
            $(this).closest('.js-editable-section').addClass('editing');
        }).on('blur', '.js-editable-trigger', function () {
            $(this).closest('.js-editable-section').removeClass('editing');
        });

        $('#color-picker-anchor').chromoselector({
            // panel: true,
            // panelAlpha: true,
            // panelMode: 'hsl',
            target: '.color-picker-wrapper',
            update: function () {
                // Show a preview in the background of the input element
                $('.background-image').css(
                    'background-color',
                    $(this).chromoselector('getColor').getHexString()
                );
            }
        });

        $('.js-upload-banner').on('change', function(evt) {

            var $this = $(this),
                files = FileAPI.getFiles(evt), // Retrieve file list
                $container = $this.closest('.js-image-container'),
                $imgEl = $container.find('.js-banner-preview'),
                contWidth = $container.width(),
                contHeight = $container.height();

            FileAPI.filterFiles(files, function (file, info){
                if( /^image/.test(file.type) ){
                    if (info.width >= contWidth && info.height >= contHeight) {
                        return true;
                    } else {
                        alert('too small');
                    }
                }
                return  false;
            }, function (files, rejected){
                if( files.length ){
                    var file = files[0];
                    FileAPI.Image(file).resize(contWidth, contHeight, 'min').get(function (err, img){

                        FileAPI.readAsDataURL(img, function (evt){

                            if( evt.type == 'load' ){
                                // Success
                                var dataURL = evt.result;
                                var url = img.toDataURL(file.type);

                                // $imgEl.attr('src', url).addClass('in');
                                $imgEl.css({top: 0, left: 0});
                                $container.addClass('image-loaded');

                                // Update angular scope
                                $timeout(function() {
                                    $scope.bannerLogo.image.src = url;
                                    $scope.bannerLogo.editing = true;
                                    startEditingBanner();
                                    $this.val('');

                                    var cleanUrl = url.replace(/^data:image\/(png|jpg|jpeg|gif);base64,/, "");
                                    // console.log(cleanUrl);

                                    suService.uploadClientImage(url, file.type).then(function(data) {
                                        console.log('success');
                                        console.log(data.data);
                                    });

                                        // var xhr = FileAPI.upload({
                                        //     url: '/api/client/default_client/images',
                                        //     files: {img: img},
                                        //     headers: {
                                        //         'Content-Type': file.type,
                                        //         'Content-Transfer-Encoding': 'BASE64'
                                        //     },
                                        //     upload: function (xhr, options){
                                        //         console.log('op');
                                        //     }
                                        // });
                                });

                                var y1 = contHeight,
                                    x1 = contWidth,
                                    y2 = img.height,
                                    x2 = img.width;

                                $imgEl.draggable({
                                    scroll: false,
                                    drag: function(event, ui) {
                                        if(ui.position.top >= 0) {
                                            ui.position.top = 0;
                                        } else if( ui.position.top <= y1 - y2) {
                                            ui.position.top = y1 - y2;
                                        }

                                        if( ui.position.left >= 0) {
                                            ui.position.left = 0;
                                        } else if ( ui.position.left <= x1 - x2) {
                                            ui.position.left = x1 - x2;
                                        }
                                    },
                                    stop: function(event, ui) {
                                        //####
                                    }
                                });
                            } else if( evt.type =='progress' ){
                                var pr = evt.loaded/evt.total * 100;
                            } else {
                                console.log('error');
                                // Error
                            }
                        });

                    });

                }
            });
        });
    }]).factory('signUpFormService', ['$http', function($http) {
        console.log('opp');
        window.$http = $http;
        var clientSlug = 'default_client';

        return {
            getClienImages: function() {
                return $http({
                    url: '/api/client/'+clientSlug+'/images',
                    method: 'GET'
                });
            },
            uploadClientImage: function(src, type) {
                return $http({
                    url: '/api/client/'+clientSlug+'/images',
                    method: 'POST',
                    data: {
                        data: src,
                        type: type
                    }
                });
            }
        };
    }]);

})(jQuery);
