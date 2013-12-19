
// JS for SignUp page
'use strict';

(function($) {
    angular.module('keen').controller('signUpCtrl', ['$scope', '$timeout', 'signUpFormService', '$q', function($scope, $timeout, suService, $q){

        // suService.getClienImages().then(function(data) {
        //     console.log(data);
        // });
        // suService.getClientForms().then(function(data) {
        //     console.log(data);
        // });

        // Initial data:

        $scope.title = {text: 'some title', isEditing: false};
        $scope.permalink = {text: 'some-perma-link', isEditing: false};
        $scope.formTitle = {text: 'Header 4 would have max 75 characters', isEditing: false, height: 70};
        $scope.formDescription = {text: 'Description would have max 75 characters', isEditing: false, height: 70};

        $scope.globalAlert = false;
        var notify = function(text) {
            $timeout(function() {
                $scope.alertText = text;
                $scope.globalAlert = true;
            });
        };

        $scope.blurOnEnter = function(e) {
            if (e.keyCode === 13) {
                e.preventDefault();

                $timeout(function() {
                    $(e.currentTarget).trigger('blur');
                });

            }
        };
        $scope.checkSize = function(e, item) {
            item.height = $(e.target).outerHeight();
        };

        $scope.startEditing = function(item) {
            item.tempData = angular.copy(item.text);
            item.isEditing = true;
        };
        $scope.cancelEditing = function(item) {
            item.text = item.tempData;
            item.isEditing = false;
        };
        $scope.saveEditing = function(item) {
            item.isEditing = false;
        };

        $scope.validateSlug = function(slug) {
            suService.checkFormSlug(slug.text).then(function(res) {
                // alert('Slug: "'+slug.text+'" already exists');
                notify('Slug: "'+slug.text+'" already exists');
            }, function(err) {
                $scope.saveEditing(slug);
            });
        };

        var defaultImageSrc = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7';
        var lastBannerLogo = {
            image: {
                // transparent pixel
                src: defaultImageSrc,
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
            $scope.bannerLogo = angular.copy(lastBannerLogo);
            stopEditingBanner(lastBannerLogo);
            $('#banner-preview').css({'left': $scope.bannerLogo.image.left, 'top': $scope.bannerLogo.image.top});
        };

        $scope.startRepositionBanner = function() {
            if (!$scope.bannerLogo.editing) {
                startEditingBanner();
            }
        };

        var $bannerLogo = $('.banner-logo .js-banner-preview');
        function startEditingBanner() {
            $scope.bannerLogo.editing = true;
            $scope.bannerLogo.uploaded = true;

            if ($bannerLogo.hasClass('ui-draggable')) {
                $bannerLogo.draggable('enable');
            }
        }
        function stopEditingBanner() {
            $scope.bannerLogo.editing = false;

            if ($bannerLogo.hasClass('ui-draggable')) {
                $bannerLogo.draggable('disable');
            }
        }

        var lastBackgroundImage = {
            image: {
                // transparent pixel
                src: defaultImageSrc,
                top: 0,
                left: 0
            },
            backgroundColor: '',
            uploaded: false,
            reposition: false,
            editing: false,
        };

        $scope.backgroundImage = angular.copy(lastBackgroundImage);
        $scope.saveEditingBgImage = function() {
            stopEditingBgImage();
            lastBackgroundImage = angular.copy($scope.backgroundImage);
        };

        $scope.cancelEditingBgImage = function() {
            $scope.backgroundImage = angular.copy(lastBackgroundImage);
            stopEditingBgImage(lastBackgroundImage);
            $('#banner-preview').css({'left': $scope.backgroundImage.image.left, 'top': $scope.backgroundImage.image.top});
        };

        $scope.startRepositionBgImage = function() {
            if (!$scope.backgroundImage.editing) {
                startEditingBgImage();
            }
        };

        var $backgroundImage = $('.background-image .js-banner-preview');
        function startEditingBgImage() {
            $scope.backgroundImage.editing = true;
            $scope.backgroundImage.uploaded = true;
            $scope.backgroundImage.reposition = true;

            if ($backgroundImage.hasClass('ui-draggable')) {
                $backgroundImage.draggable('enable');
            }
        }

        function stopEditingBgImage() {
            $scope.backgroundImage.editing = false;
            $scope.backgroundImage.reposition = false;

            if ($backgroundImage.hasClass('ui-draggable')) {
                $backgroundImage.draggable('disable');
            }

            $('.background-image').css('background-color', $scope.backgroundImage.backgroundColor);
            $('#color-picker-anchor').chromoselector('hide');
        }

        $scope.removeBgImage = function() {
            $scope.backgroundImage.image.src = defaultImageSrc;
            $scope.backgroundImage.uploaded = false;
        };

        var $bgImageColorPicker = $('#color-picker-anchor');

        $bgImageColorPicker.chromoselector({
            panel: true,
            autoshow: false,
            // panelAlpha: true,
            panelMode: 'hsl',
            preview: false,
            target: '.color-picker-wrapper',
            update: updateBgImageBgColor
        });

        $scope.changeBgImageBgColor = function() {
            $bgImageColorPicker.chromoselector('show', 0).chromoselector('resize', 200);
            $scope.backgroundImage.editing = true;
            $scope.formAppearanceEditing = false;
        };

        function updateBgImageBgColor() {
            // Show a preview in the background of the input element
            var color = $bgImageColorPicker.chromoselector('getColor').getHexString();
            $('.background-image').css('background-color', color);

            $scope.backgroundImage.backgroundColor = color;
        }

        $scope.form = {};
        var $formBgColorPicker = $('#su-bg-color');
        $formBgColorPicker.chromoselector({
            panel: true,
            autoshow: false,
            // panelAlpha: true,
            panelMode: 'hsl',
            preview: false,
            target: '.su-bg-color',
            update: updateFormBgColor
        });
        function updateFormBgColor() {
            // Show a preview in the background of the input element
            var color = $formBgColorPicker.chromoselector('getColor').getHexString();
            $('.su-form').css('background-color', color);

            $scope.form.backgroundColor = color;
        }

        var $formTextColorPicker = $('#su-text-color');
        $formTextColorPicker.chromoselector({
            panel: true,
            autoshow: false,
            // panelAlpha: true,
            panelMode: 'hsl',
            preview: false,
            target: '.su-text-color',
            update: updateFormTextColor
        });

        function updateFormTextColor() {
            // Show a preview in the background of the input element
            var color = $formTextColorPicker.chromoselector('getColor').getHexString();
            $('.su-form').find('textarea').css('color', color);

            $scope.form.textColor = color;

        }

        $scope.formAppearanceEditing = false;
        $scope.toggleFormAppearance = function() {
            if (!$scope.formAppearanceEditing) {
                $formBgColorPicker.chromoselector('show').chromoselector('resize', 150);
                $formTextColorPicker.chromoselector('show').chromoselector('resize', 150);
            }

            $scope.formAppearanceEditing = !$scope.formAppearanceEditing;
        };

        var cleanBase64 = function(str) {
            return str.replace(/^data:image\/(png|jpg|jpeg|gif);base64,/, '');
        };

        $scope.saveForm = function() {

            // validate slug
            suService.checkFormSlug($scope.permalink.text).then(function(res) {
                notify('Slug: "'+ $scope.permalink.text+ '" already exists');
            }, function(err) {
                saveFormData();
            });
        };

        $scope.saveFormAsPreview = function() {

            // wait for all blur events
            $timeout(function() {
                // validate slug
                suService.checkFormSlug($scope.permalink.text).then(function(res) {
                    notify('Slug: "'+ $scope.permalink.text+ '" already exists');
                }, function(err) {
                    saveFormAsPreviewData();
                });
            }, 100);
        };

        var prepareFormData = function() {
            var defer = $q.defer();

            var formData = {
                pageTitle: $scope.title.text,
                permalink: $scope.permalink.text,

                bannerLogo: {
                    imageSrc: '',
                    position: {
                        top: $scope.bannerLogo.image.top,
                        left: $scope.bannerLogo.image.left
                    }
                },

                backgroundImage: {
                    imageSrc: '',
                    position: {
                        top: $scope.backgroundImage.image.top,
                        left: $scope.backgroundImage.image.left
                    },
                    backgroundColor: $scope.backgroundImage.backgroundColor
                },

                form: {
                    backgroundColor: $scope.form.backgroundColor,
                    textColor: $scope.form.textColor,
                    title: $scope.formTitle.text,
                    titleHeight: $scope.formTitle.height,
                    description: $scope.formDescription.text,
                    descriptionHeight: $scope.formDescription.height
                }
            };
            console.log(formData.form);

            var imagesData = [];

            if ($scope.bannerLogo.image.src !== defaultImageSrc) {
                var bannerLogoImgData = suService.uploadClientImage(
                        cleanBase64($scope.bannerLogo.image.src), // img base64 data
                        $scope.bannerLogo.image.type,             // img type
                        'banner'                                  // img target
                    );
                imagesData.push(bannerLogoImgData);
            }

            if ($scope.backgroundImage.image.src !== defaultImageSrc) {
                var backgroundImageData = suService.uploadClientImage(
                        cleanBase64($scope.backgroundImage.image.src), // img base64 data
                        $scope.backgroundImage.image.type,             // img type
                        'background'                                   // img target
                    );
                imagesData.push(backgroundImageData);
            }

            $q.all(imagesData).then(function(images) {
                _.each(images, function(image) {
                    if (image.data.target === 'banner') {
                        formData.bannerLogo.imageSrc = image.data.url;
                    } else if (image.data.target === 'background') {
                        formData.backgroundImage.imageSrc = image.data.url;
                    }
                });

                defer.resolve(formData);

            }, function(err) {
                console.error(err);
            });

            return defer.promise;
        };

        var saveFormData = function() {
            prepareFormData()
                .then(function(formData) {
                    suService.uploadFormData(formData, $scope.permalink.text)
                        .then(function(res) {
                            alert('FORM Created');
                            console.log('res: ', res);
                        }, function(err) {console.error(err);});
                });

        };
        var saveFormAsPreviewData = function() {
            var previewSlug = 'preview-' + $scope.permalink.text;
            prepareFormData()
                .then(function(formData) {
                    suService.uploadFormData(formData, previewSlug)
                        .then(function(res) {
                            alert('FORM preview Created');
                            suService.goToFormView(previewSlug);
                            // window.open('www.yourdomain.com','_blank');
                            console.log('res: ', res);
                        }, function(err) {console.error(err);});
                });

        };


        $('.js-upload-banner').on('change', function(evt) {

            var $this = $(this),
                files = FileAPI.getFiles(evt), // Retrieve file list
                $container = $this.closest('.js-image-container'),
                $imgEl = $container.find('.js-banner-preview'),
                contWidth = $container.width(),
                contHeight = $container.height(),
                scopeObject = $container.data('scope-object');

            // disabling retina ratio
            Caman.prototype.hiDPIDisabled = function() {return true};

            FileAPI.filterFiles(files, function (file, info){
                if( /^image/.test(file.type) ){
                    if (info.width >= contWidth && info.height >= contHeight) {
                        return true;
                    } else {
                        var msg = 'Your image is too small ('+info.width+'x'+info.height+' pixels). Should be at least ' + contWidth + 'x' + contHeight + ' pixels.';
                        notify(msg);
                    }
                }
                return  false;
            }, function (files, rejected){
                if( files.length ){
                    var file = files[0];
                    FileAPI.Image(file)
                    .resize(contWidth, contHeight, 'min')
                    // .filter('vintage')
                    .get(function (err, img){

                        FileAPI.readAsDataURL(img, function (evt){

                            if( evt.type === 'load' ){
                                // Success
                                // var dataURL = evt.result;
                                var url = img.toDataURL(file.type);

                                // $imgEl.attr('src', url).addClass('in');
                                $imgEl.css({top: 0, left: 0});
                                $container.addClass('image-loaded');

                                // Update angular scope

                                $timeout(function() {
                                    if (scopeObject === 'bannerLogo') {
                                        $scope.bannerLogo.editing = true;
                                        $scope.bannerLogo.image.src = url;
                                        $scope.bannerLogo.image.type = file.type;
                                        startEditingBanner();
                                    } else if (scopeObject === 'backgroundImage') {
                                        $scope.backgroundImage.editing = true;
                                        $scope.backgroundImage.image.src = url;
                                        $scope.backgroundImage.image.type = file.type;
                                        startEditingBgImage();
                                    }
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
                                        $timeout(function() {
                                            if (scopeObject === 'bannerLogo') {
                                                $scope.bannerLogo.image.top = ui.position.top;
                                                $scope.bannerLogo.image.left = ui.position.left;
                                            } else if (scopeObject === 'backgroundImage') {
                                                $scope.backgroundImage.image.top = ui.position.top;
                                                $scope.backgroundImage.image.left = ui.position.left;
                                            }
                                        });
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
        var clientSlug = $('#clientSlug').text(),
            apiClientUrl = '/api/client/'+clientSlug;

        return {
            getClienImages: function() {
                return $http({
                    url: apiClientUrl+'/images',
                    method: 'GET'
                });
            },
            uploadClientImage: function(src, type, target) {
                return $http({
                    url: apiClientUrl+'/images',
                    method: 'POST',
                    data: {
                        data: src,
                        type: type,
                        target: target
                    }
                });
            },
            checkFormSlug: function(slug) {
                return $http({
                    url: apiClientUrl+'/signup_forms/'+slug,
                    method: 'HEAD'
                });
            },
            getClientForms: function() {
                return $http({
                    url: apiClientUrl+'/signup_forms',
                    method: 'GET'
                });
            },
            uploadFormData: function(data, slug) {
                return $http({
                    url: apiClientUrl+'/signup_forms',
                    method: 'POST',
                    data: {
                        data: data,
                        slug: slug
                    }
                });
            },
            goToFormView: function(formSlug) {
                var formUrl = '/'+clientSlug+'/'+formSlug;
                window.open('/');
            }
        };
    }]);

    $('.instructions-wrap').on('selectstart, dragstart', function(e) {
        e.preventdefault();
    });

})(jQuery);
