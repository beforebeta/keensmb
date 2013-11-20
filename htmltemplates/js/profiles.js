// JS for profiles page
'use strict';

(function($) {


  function checkItemActions(e) {
    var $customersTable = $('#customers-table'),
        checkboxes = $customersTable.find(':checkbox'),
        checkedAny = (checkboxes.filter(':checked').length !== 0);

    $('.js-item-selected')[checkedAny ? 'slideDown' : 'slideUp']();
  }


    // Table: Add class row selected
  $(document).on('toggle', '#customers-table :checkbox', checkItemActions);

})(jQuery);
