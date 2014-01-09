
// Some general UI pack related JS
// Extend JS String with repeat method
String.prototype.repeat = function(num) {
  return new Array(num + 1).join(this);
};

(function($) {

  // Add segments to a slider
  $.fn.addSliderSegments = function (amount) {
    return this.each(function () {
      var segmentGap = 100 / (amount - 1) + "%"
        , segment = "<div class='ui-slider-segment' style='margin-left: " + segmentGap + ";'></div>";
      $(this).prepend(segment.repeat(amount - 2));
    });
  };

  $(function() {

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
    $(".tooltip").addClass(function() {
      if ($(this).prev().attr("data-tooltip-style")) {
        return "tooltip-" + $(this).prev().attr("data-tooltip-style");
      }
    });

    // Placeholders for input/textarea
    $("input, textarea").placeholder();

    // Make pagination demo work
    $(".pagination a").on('click', function() {
      $(this).parent().siblings("li").removeClass("active").end().addClass("active");
    });

    $(".btn-group a").on('click', function() {
      $(this).siblings().removeClass("active").end().addClass("active");
    });

    // Disable link clicks to prevent page scrolling
    $('a[href="#fakelink"]').on('click', function (e) {
      e.preventDefault();
    });

    // jQuery UI Spinner
    $.widget( "ui.customspinner", $.ui.spinner, {
      widgetEventPrefix: $.ui.spinner.prototype.widgetEventPrefix,
      _buttonHtml: function() { // Remove arrows on the buttons
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
    $('.input-group').on('focus', '.form-control', function () {
      $(this).closest('.form-group, .navbar-search').addClass('focus');
    }).on('blur', '.form-control', function () {
      $(this).closest('.form-group, .navbar-search').removeClass('focus');
    });

    // Table: Toggle all checkboxes
    $('.table .toggle-all').on('click', function() {
      var ch = $(this).find(':checkbox').prop('checked');
      $(this).closest('.table').find('tbody :checkbox').checkbox(!ch ? 'check' : 'uncheck');
    });

    // Popovers
    $('.js-popover-hover').popover({
        'trigger': 'hover',
        'container': 'body'
    });

    // Trigger click elements
    $(document).on('click', '.js-trigger', function(e) {
        var target = $(this).data('target');
        $(target).trigger('click');
    });

    // Chromoselector
    if( $('.chromoselector').chromoselector ) {
      $('.chromoselector').chromoselector();
    }

    // Table: Add class row selected
    // $(document).on('check uncheck toggle', '.table tbody :checkbox', function (e) {
    //   var $this = $(this)
    //     , check = $this.prop('checked')
    //     , toggle = e.type == 'toggle'
    //     , checkboxes = $('.table tbody :checkbox')
    //     , checkAll = checkboxes.length == checkboxes.filter(':checked').length

    //   $this.closest('tr')[check ? 'addClass' : 'removeClass']('selected-row');
    //   if (toggle) $this.closest('.table').find('.toggle-all :checkbox').checkbox(checkAll ? 'check' : 'uncheck');
    // });

    // jQuery UI Datepicker
    var datepickerSelector = '.datapicker';
    $(datepickerSelector).datepicker({
      showOtherMonths: true,
      selectOtherMonths: true,
      dateFormat: "mm/dd/yy",
      yearRange: "c-99:+0",
      changeMonth: true,
      changeYear: true
    }).siblings('.btn, .input-group-btn').on('click', function (e) {
      e && e.preventDefault();
      $(datepickerSelector).focus();
    });
    $.extend($.datepicker, {_checkOffset:function(inst,offset,isFixed){return offset}});

    // Now let's align datepicker with the prepend button
    $(datepickerSelector).datepicker('widget').css({'margin-left': -$(datepickerSelector).prev('.input-group-btn').find('.btn').outerWidth()});

    // Switch
    $("[data-toggle='switch']").wrap('<div class="switch" />').parent().bootstrapSwitch();

    // Typehead
    // $('.typeahead').typeahead();

    $(document).on('click', '.js-submit-form', function(e) {
        e.preventDefault();
        $(this).closest('form').submit();
    });

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


  $sectionWrap = $('.section-segment-wrapper');

  $sectionWrap.find('.section-default').each(function() {

    var innerText =  $(this).find('.kn-section-header span').text();
        data =  $(this).data('section-name');

    var $itemInList = $('.promotion-scroll-menu').prev('li').clone();

    $itemInList.attr('data-item', data);
    $itemInList.text(innerText);
    $itemInList.appendTo($('.promotion-scroll-menu')).show();
  });

  $('.js-trigger-item').on('click', function() {
    var $this = $(this),
        itemData = $this.data('item');

    if(!$this.hasClass('active')) {

      $this.addClass('active');

      $('.promotion-narrow-field').hide();
      $('.section-default').find('select').select2();

      $('.section-default').each(function() {

          var sectionData = $this.data('section-name');

          if(itemData === sectionData) {
              $this.show();
          }
      });
    }
  });



  $sectionWrap.on('click', '.promotion-icon-close-height', function(){

      var $thisSection = $(this).parents('.section-default'),
          itemName = $thisSection.data('section-name');

      $('.js-trigger-item').each(function() {

        var $this = $(this),
            $dataItem = $this.data('item');

        if($dataItem === itemName) {
          $this.removeClass('active');
        }

      });

      $thisSection.hide();

      if(!$sectionWrap.children('.section-default').length){
        $('.promotion-narrow-field').show();
      }
  });

})(jQuery);
