// Use waypoints.js jQuery plugin to load next portion of
// customer list once client scrolls down to the bottom of it.
// This is more optimal than using waypoints-infinite.js

$(function() {
  var $customers_container = $('#customers-table tbody');

  $('#load-more-customers').waypoint({
    handler: function(direction) {
      var $this = $(this);

      $this.waypoint('disable');

      $.get($this.attr('href'), function(data) {
        if (data) {
          $customers_container.append($(data)).find(':checkbox').checkbox();
          $this.waypoint('enable');
        } else {
          $this.waypoint('destroy');
          $this.hide();
        }
      });
    },
    offset: 'bottom-in-view'});
  });
