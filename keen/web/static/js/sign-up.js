
// JS for SignUp page
'use strict';

(function($) {
    angular.module('keen').controller('signUpCtrl', ['$scope', '$timeout', function($scope, $timeout){

        // Initial data:

        $scope.title = {text: 'some title', isEditing: false};
        $scope.permalink = {text: 'some-perma-link', isEditing: false};

        var tempData;
        $scope.startEditing = function(item) {
            tempData = angular.copy(item.text);
            item.isEditing = true;
        };
        $scope.cancelEditing = function(item) {
            $timeout(function() {
                item.text = tempData;
                item.isEditing = false;
            }, 100);
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
            panel: true,
            panelAlpha: true,
            panelMode: 'hsl',
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
                                    $scope.oppa = 'wefwef';
                                    $scope.bannerLogo.image.src = url;
                                    console.log($scope.bannerLogo.image.src);
                                    $scope.bannerLogo.editing = true;
                                    $this.val('');
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
    }]);

})(jQuery);
