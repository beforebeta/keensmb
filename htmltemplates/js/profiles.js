// JS for profiles page
'use strict';

(function($) {

    var checkItemActions = function() {
        var $customersTable = $('#customers-table'),
            checkboxes = $customersTable.find(':checkbox'),
            checkedAny = (checkboxes.filter(':checked').length !== 0);

        $('.js-item-selected')[checkedAny ? 'slideDown' : 'slideUp'](200);
    };

    var deleteCustomer = function() {

        // do ajax call here, with callback:

        $('.js-customer-deleted-name').text('John Smith');
        $('.customer-deleted-alert').show().addClass('in');
    };

    var closeGlobalAlert = function(e) {
        e.preventDefault();
        var $alertBlock = $(this).closest('.global-alert');
        $alertBlock.removeClass('in').hide();
    };



    // Table: Add class row selected
    $(document).on('toggle', '#customers-table :checkbox', checkItemActions);

    $(document).on('click', '.js-delete-customer', deleteCustomer);
    $(document).on('click', '.global-alert .close', closeGlobalAlert);

})(jQuery);
