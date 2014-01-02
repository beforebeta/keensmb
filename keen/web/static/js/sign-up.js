
// JS for SignUp page
'use strict';

(function($) {
    angular.module('keen').controller('signUpCtrl', ['$scope', '$timeout', 'signUpFormService', '$q', '$sanitize', function($scope, $timeout, suService, $q, $sanitize){

        // suService.getClienImages().then(function(data) {
        //     console.log(data);
        // });
        // suService.getClientForms().then(function(data) {
        //     console.log(data);
        // });
        $scope.dataLoaded = false;

        suService.getInitialData().then(function(data) {
            var formData = suService.formSlug ? parseFormData(data) : data;
            $scope = angular.extend($scope, formData);
            $scope.clientSlug = suService.clientSlug;
            $scope.formSlug = suService.formSlug;

            if ($scope.formSlug) {
                initDraggableImages();
            }
            $timeout(function() {
                initTextAreasAutosize();
            });

            $scope.dataLoaded = true;
        });

        $scope.$watch('permalink.text', function(newVal, oldVal) {
            var regExp = /[^0-9a-zA-Z-_.]/g;
            if (newVal && newVal.match(regExp)) {
                $scope.permalink.text = newVal.replace(regExp, '-');
            }
        });

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
            // if form is edit:
            if (suService.formSlug) {
                $scope.saveEditing(slug);
                return true;
            }

            suService.checkFormSlug(slug.text).then(function(res) {
                var link = suService.getFormLink(slug.text);
                notify('Form with a slug <a href="'+link+'" target="_blank">'+slug.text+'</a> already exists.');
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
            $bannerLogo.css({'left': $scope.bannerLogo.image.left, 'top': $scope.bannerLogo.image.top});
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
            $backgroundImage.css({'left': $scope.backgroundImage.image.left, 'top': $scope.backgroundImage.image.top});
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
            $timeout(function() {
                $scope.form.backgroundColor = color;
            });
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
            $timeout(function() {
                $scope.form.textColor = color;
            });
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


            // wait for all blur events
            $timeout(function() {
                // validate slug
                suService.checkFormSlug($scope.permalink.text).then(function(res) {
                    if (suService.formSlug) {
                        // update data
                        saveFormData(true);
                        return false;
                    }
                    var link = suService.getFormLink($scope.permalink.text);
                    notify('Form with a slug <a href="'+link+'" target="_blank">'+$scope.permalink.text+'</a> already exists.');
                }, function(err) {
                    suService.formSlug = $scope.permalink.text;
                    saveFormData();
                });
            }, 100);
        };

        $scope.saveFormAsPreview = function() {
            // wait for all blur events
            $timeout(function() {
                // validate slug
                var previewSlug = 'preview-'+$scope.permalink.text;
                suService.checkFormSlug(previewSlug).then(function(res) {
                    // if (suService.formSlug) {
                    if (true) { // temporary solution
                        saveFormAsPreviewData(true);
                        return true;
                    }
                    var link = suService.getFormLink($scope.permalink.text);
                    notify('Form with a slug <a href="'+link+'" target="_blank">'+$scope.permalink.text+'</a> already exists.');
                }, function(err) {
                    saveFormAsPreviewData();
                });
            }, 100);
        };

        $scope.discard = function() {
            window.location.reload();
        };

        var parseFormData = function(formData) {
            var prepared = {};
            prepared.title = {text: formData.pageTitle, isEditing: false};
            prepared.permalink = {text: formData.permalink, isEditing: false};
            prepared.bannerLogo = {
                image: {
                    src: formData.bannerLogo.imageSrc,
                    top: formData.bannerLogo.position.top,
                    left: formData.bannerLogo.position.left
                },
                uploaded: !!formData.bannerLogo.imageSrc
            };
            prepared.backgroundImage = {
                image: {
                    src: formData.backgroundImage.imageSrc,
                    top: formData.backgroundImage.position.top,
                    left: formData.backgroundImage.position.left
                },
                uploaded: !!formData.backgroundImage.imageSrc,
                backgroundColor: formData.backgroundImage.backgroundColor
            };
            prepared.form = {
                backgroundColor: formData.form.backgroundColor,
                textColor: formData.form.textColor
            };
            prepared.formTitle = {
                text: formData.form.title
            };
            prepared.formDescription = {
                text: formData.form.description
            };

            return prepared;
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
                    description: $scope.formDescription.text
                }
            };

            // save images to server
            var imagesData = [];
            if ($scope.bannerLogo.image.src !== defaultImageSrc) {
                if (!$scope.bannerLogo.image.type) {
                    formData.bannerLogo.imageSrc = $scope.bannerLogo.image.src;
                } else {
                    var bannerLogoImgData = suService.uploadClientImage(
                            cleanBase64($scope.bannerLogo.image.src), // img base64 data
                            $scope.bannerLogo.image.type,             // img type
                            'banner'                                  // img target
                        );
                    imagesData.push(bannerLogoImgData);
                }
            }

            if ($scope.backgroundImage.image.src !== defaultImageSrc) {
                if (!$scope.backgroundImage.image.type) {
                    formData.backgroundImage.imageSrc = $scope.backgroundImage.image.src;
                } else {
                    var backgroundImageData = suService.uploadClientImage(
                            cleanBase64($scope.backgroundImage.image.src), // img base64 data
                            $scope.backgroundImage.image.type,             // img type
                            'background'                                   // img target
                        );
                    imagesData.push(backgroundImageData);
                }
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

        var saveFormData = function(update) {
            prepareFormData()
                .then(function(formData) {
                    var method = update ? 'updateFormData' : 'createFormData';
                    suService[method](formData, $scope.permalink.text)
                        .then(function(res) {
                            $scope.createdIsPreview = false;
                            $scope.formCreatedLink = suService.getFormLink($scope.permalink.text);
                            $('#formCreatedModal').modal('show');
                        }, function(err) {
                            console.warn(err);
                            notify('Some error occured while saving your form.');
                        });
                });

        };
        var saveFormAsPreviewData = function(update) {
            var previewSlug = 'preview-' + $scope.permalink.text;
            prepareFormData()
                .then(function(formData) {
                    var method = update ? 'updateFormData' : 'createFormData';
                    suService[method](formData, previewSlug)
                        .then(function(res) {
                            $scope.createdIsPreview = true;
                            $scope.formCreatedLink = suService.getFormLink(previewSlug);
                            $('#formCreatedModal').modal('show');
                        }, function(err) {
                            console.warn(err);
                            notify('Some error occured while saving your form.');
                        });
                });

        };

        var initTextAreasAutosize = function() {
            $('.js-resize-area').autosize().trigger('autosize.resize');
        };

        var initDraggableImages = function() {
            var images = [$scope.backgroundImage.image.src, $scope.bannerLogo.image.src];

            suService.preLoadImages(images).then(function(status) {

                $scope.dataLoaded = status; // true

                if (suService.formSlug) {

                    $('#banner-preview, #background-image').each(function(i, item) {
                        if (item.src === defaultImageSrc) {return true;}
                        var $imgEl = $(item),
                            $container = $imgEl.closest('.js-image-container'),
                            contWidth = $container.width(),
                            contHeight = $container.height(),
                            scopeObject = $container.data('scope-object');

                        var y1 = contHeight,
                            x1 = contWidth,
                            y2 = $imgEl.height(),
                            x2 = $imgEl.width();

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

                        $scope.saveEditingBgImage();
                        $scope.cancelEditingBgImage();
                        $scope.saveEditingBanner();
                        $scope.cancelEditingBanner();
                    });
                }
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
                                var url = img.toDataURL(file.type);

                                $imgEl.css({top: 0, left: 0});

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
                            } else if (evt.type =='progress'){
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
    }]).factory('signUpFormService', ['$http', '$q', '$location', function($http, $q, $location) {
        var clientSlug = $('#clientSlug').text(),
            formSlug = $('#formSlug').val(),
            apiClientUrl = '/api/client/'+clientSlug;

        // Initial data:

        var defaultData = {};
        defaultData.title = {text: 'some title', isEditing: false};
        defaultData.permalink = {text: 'some-perma-link', isEditing: false};
        defaultData.formTitle = {text: 'Header 4 would have max 75 characters', isEditing: false};
        defaultData.formDescription = {text: 'Description would have max 250 characters', isEditing: false};

        return {
            formSlug: formSlug,
            clientSlug: clientSlug,
            getInitialData: function() {
                var defer = $q.defer();

                if (formSlug) {
                    $http({
                        url: apiClientUrl+'/signup_forms/'+formSlug,
                        method: 'GET'
                    }).then(function(res) {
                        defer.resolve(res.data.data);
                    });
                } else {
                    defer.resolve(defaultData);
                }

                return defer.promise;
            },
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
                    method: 'HEAD',
                    cache: true
                });
            },
            getClientForms: function() {
                return $http({
                    url: apiClientUrl+'/signup_forms',
                    method: 'GET'
                });
            },
            createFormData: function(data, slug) {
                return $http({
                    url: apiClientUrl+'/signup_forms',
                    method: 'POST',
                    data: {
                        data: data,
                        slug: slug
                    }
                });
            },
            updateFormData: function(data, slug) {
                return $http({
                    url: apiClientUrl+'/signup_forms/'+slug,
                    method: 'PUT',
                    data: {
                        data: data,
                        slug: slug
                    }
                });
            },
            getFormLink: function(slug) {
                return '/'+clientSlug+'/'+slug;
            },
            preLoadImages: function(images) {
                var defer = $q.defer();

                var imgList = _.compact(images),
                    imgLength = imgList.length;

                _.each(imgList, function(imgSrc, i) {
                    var img = new Image();

                    img.onload = function() {
                        imgLength += -1;

                        if (imgLength === 0) {defer.resolve(true);}
                    };

                    img.src = imgSrc;
                });

                return defer.promise;
            }
        };
    }]).directive('onEnter',function() {

        var linkFn = function(scope,element,attrs) {
            element.bind('keypress', function(e) {
                if(e.which === 13) {
                    scope.$apply(function() {
                        scope.$eval(attrs.onEnter);
                    });
                    element.blur();
                    e.preventDefault();
                }
            });
        };

        return {
            link:linkFn
        };
    });

    $('.instructions-wrap').on('selectstart, dragstart', function(e) {
        e.preventdefault();
    });

})(jQuery);
