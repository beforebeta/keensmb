// Some general UI pack related JS
// Extend JS String with repeat method
String.prototype.repeat = function (num) {
    return new Array(num + 1).join(this);
};

var keen = {};
keen.showMessageModal = function(title, message) {
    var $modal = $('#messageModal');
    $modal.find('h4.modal-title').html(title);
    $modal.find('.modal-body .text-default').html(message);
    $modal.modal({show:true});
};

(function ($) {

    //setup support for csrf
    $(document).ajaxSend(function(event, xhr, settings) {
        function getCookie(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie != '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) == (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
        function sameOrigin(url) {
            // url could be relative or scheme relative or absolute
            var host = document.location.host; // host + port
            var protocol = document.location.protocol;
            var sr_origin = '//' + host;
            var origin = protocol + sr_origin;
            // Allow absolute or scheme relative URLs to same origin
            return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
                (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
                // or any other URL that isn't scheme relative or absolute i.e relative.
                !(/^(\/\/|http:|https:).*/.test(url));
        }
        function safeMethod(method) {
            return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
        }

        if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    });

    // Add segments to a slider
    $.fn.addSliderSegments = function (amount) {
        return this.each(function () {
            var segmentGap = 100 / (amount - 1) + "%"
                , segment = "<div class='ui-slider-segment' style='margin-left: " + segmentGap + ";'></div>";
            $(this).prepend(segment.repeat(amount - 2));
        });
    };

    $(function () {

        // Custom Selects
        $("select[name='huge']").selectpicker({style: 'btn-hg btn-primary', menuStyle: 'dropdown-inverse'});
        $("select[name='large']").selectpicker({style: 'btn-lg btn-danger'});
        $("select[name='info']").selectpicker({style: 'btn-info'});
        $("select[name='small']").selectpicker({style: 'btn-sm btn-warning'});
        $("select.simple").selectpicker({style: 'btn-sm btn-default'});

        // Tabs
        $(".nav-tabs a").on('click', function (e) {
            e.preventDefault();
            $(this).tab("show");
        })

        // Tooltips
        $("[data-toggle=tooltip]").tooltip("show");

        // Tags Input
        $(".tagsinput").tagsInput();

        // jQuery UI Sliders
        var $slider = $("#slider");
        if ($slider.length > 0) {
            $slider.slider({
                min: 1,
                max: 5,
                value: 3,
                orientation: "horizontal",
                range: "min"
            }).addSliderSegments($slider.slider("option").max);
        }

        // Add style class name to a tooltips
        $(".tooltip").addClass(function () {
            if ($(this).prev().attr("data-tooltip-style")) {
                return "tooltip-" + $(this).prev().attr("data-tooltip-style");
            }
        });

        // Placeholders for input/textarea
        $("input, textarea").placeholder();

        // Make pagination demo work
        $(".pagination a").on('click', function () {
            $(this).parent().siblings("li").removeClass("active").end().addClass("active");
        });

        $(".btn-group a").on('click', function () {
            $(this).siblings().removeClass("active").end().addClass("active");
        });

        // Disable link clicks to prevent page scrolling
        $('a[href="#fakelink"]').on('click', function (e) {
            e.preventDefault();
        });

        // jQuery UI Spinner
        $.widget("ui.customspinner", $.ui.spinner, {
            widgetEventPrefix: $.ui.spinner.prototype.widgetEventPrefix,
            _buttonHtml: function () { // Remove arrows on the buttons
                return "" +
                    "<a class='ui-spinner-button ui-spinner-up ui-corner-tr'>" +
                    "<span class='ui-icon " + this.options.icons.up + "'></span>" +
                    "</a>" +
                    "<a class='ui-spinner-button ui-spinner-down ui-corner-br'>" +
                    "<span class='ui-icon " + this.options.icons.down + "'></span>" +
                    "</a>";
            }
        });

        // Focus state for append/prepend inputs
        $('.input-group').on('focus', '.form-control',function () {
            $(this).closest('.form-group, .navbar-search').addClass('focus');
        }).on('blur', '.form-control', function () {
                $(this).closest('.form-group, .navbar-search').removeClass('focus');
        });

        // Table: Toggle all checkboxes
        $('.table .toggle-all').on('click', function () {
            var ch = $(this).find(':checkbox').prop('checked');
            $(this).closest('.table').find('tbody :checkbox').checkbox(!ch ? 'check' : 'uncheck');
        });

        // Popovers
        $('.js-popover-hover').popover({
            'trigger': 'hover',
            'container': 'body',
            'html': true
        });

        // Trigger click elements
        $(document).on('click', '.js-trigger', function (e) {
            var target = $(this).data('target');
            $(target).trigger('click');
        });

        // Chromoselector
        if ($('.chromoselector').chromoselector) {
            $('.chromoselector').chromoselector();
        }

        // Table: Add class row selected
//        $(document).on('check uncheck toggle', '.table tbody :checkbox', function (e) {
//            var $this = $(this)
//                , check = $this.prop('checked')
//                , toggle = e.type == 'toggle'
//                , checkboxes = $('.table tbody :checkbox')
//                , checkAll = checkboxes.length == checkboxes.filter(':checked').length
//
//            $this.closest('tr')[check ? 'addClass' : 'removeClass']('selected-row');
//            if (toggle) $this.closest('.table').find('.toggle-all :checkbox').checkbox(checkAll ? 'check' : 'uncheck');
//        });

        // jQuery UI Datepicker
        var setup_date_picker = function(selector, dateFormat, yearRange) {
            $(selector).datepicker({
                showOtherMonths: true,
                selectOtherMonths: true,
                dateFormat: dateFormat,
                yearRange: yearRange,
                changeMonth: true,
                changeYear: true
            }).siblings('.btn, .input-group-btn').on('click', function (e) {
              e && e.preventDefault();
              $(datepickerSelector).focus();
            });
            $.extend($.datepicker, {_checkOffset: function (inst, offset, isFixed) {
                return offset
            }});
            // Now let's align datepicker with the prepend button
            $(selector).datepicker('widget').css({'margin-left': -$(selector).prev('.input-group-btn').find('.btn').outerWidth()});
        };
        setup_date_picker('.datapicker', "mm/dd/yy", "c-99:+0");
        setup_date_picker('.datepickerAlternate', "M d, yy", "c-10:+10");


        // Switch
        $("[data-toggle='switch']").wrap('<div class="switch" />').parent().bootstrapSwitch();

        // Typehead
        // $('.typeahead').typeahead();

        $(document).on('click', '.js-submit-form', function (e) {
            e.preventDefault();
            $(this).closest('form').submit();
        });

        $(".primaryfocus").focus();

        // make code pretty
        window.prettyPrint && prettyPrint();
    });

  $buttonWrap = $('.enrichment-estimated-price .kn-section-content');

  $('.enrichment-checkbox-container .js-estimated-label').on('click', function(){

      var innerText = $(this).children('strong').html(),
          data = $(this).data('label'),
          $buttonBox = $buttonWrap.prev('.button-default').clone();

      $buttonBox.find('span').text(innerText);
      $buttonBox.attr('data-button-name', data);


      if(!$(this).hasClass('checked') || !$(this).hasClass('disabled')) {

          $(this).addClass('checked disabled');

          $buttonWrap.find('.unselect').hide();
          $buttonBox.appendTo($buttonWrap).show();

      }
      else {
          return false;
      }
  });
  $buttonWrap.on('click', '.js-delete', function(){

      var $thisButton = $(this).parent('button'),
          labelName = $thisButton.data('button-name');

      $('.js-estimated-label').each(function() {

        var $this = $(this),
            $dataLabel = $this.data("label");

        if($dataLabel === labelName) {
          $this.removeClass('checked disabled');
        }

      });

      $thisButton.remove();

      if(!$buttonWrap.children('button').length){
        $('.unselect').show();
      }
  });

})(jQuery);

try{
    (function(){
        AmCharts.ready(function () {
            // SERIAL CHART
            chart = new AmCharts.AmSerialChart();
            chart.dataProvider = chartData;
            chart.categoryField = "month";
            chart.startDuration = 1;

            // AXES
            // category
            var categoryAxis = chart.categoryAxis;
            categoryAxis.gridPosition = "start";

            // value
            // in case you don't want to change default settings of value axis,
            // you don't need to create it, as one value axis is created automatically.

            // GRAPH
            var graph = new AmCharts.AmGraph();
            graph.valueField = "visits";
            graph.balloonText = "[[category]]: <b>[[value]]</b>";
            graph.type = "column";
            graph.lineAlpha = 0;
            graph.fillAlphas = 0.8;
            graph.lineColor = '#1abc9c';
            chart.addGraph(graph);

            // CURSOR
            var chartCursor = new AmCharts.ChartCursor();
            chartCursor.cursorAlpha = 0;
            chartCursor.zoomable = false;
            chartCursor.categoryBalloonEnabled = false;
            chart.addChartCursor(chartCursor);

            chart.creditsPosition = "top-right";

            chart.write("chartdiv");
        });
    })(AmCharts);
} catch(e){}
