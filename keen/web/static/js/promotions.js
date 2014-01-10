(function ($) {

    $(function () {
        try {
            filepicker.setKey('AlEC17z10RIuLOpyhK2n2z');
        } catch (e) {
        }

        var preview_promotion = function($button) {
            var $this = $button;
            var location = $this.attr('data-location');
            var $modal = $($this.attr('data-target'));
            var $iframe = $($this.attr('data-target') + " iframe");
            var $modal_title = $($this.attr('data-target') + " h4.modal-title");
            $modal_title.text($this.attr("data-title"));
            $iframe.attr("src",location);
            $modal.modal({show:true});
        };

        var hash = window.location.hash;
        if (hash === '#preview') {
            preview_promotion($("#promotionPreviewTrigger"));
        }

        $('.previewPromotionBtn').click(function(){
            preview_promotion($(this));
        });

        // delete promotion handling
        $('.deletePromotionButton').click(function(){
            var obj_id = $(this).attr('data-obj_id');
            $('#promotionDeleteButton').attr('data-obj_id', obj_id);
        });

        $(document).on('click', '#promotionDeleteButton', function(){
            var $this = $(this);
            var obj_id = $this.attr('data-obj_id');
            console.log(obj_id);
            $.ajax({
                type: "POST",
                url: $this.attr('data-location'),
                data: {"obj_id":obj_id},
                success: function (msg) {
                    try{
                        if (msg["success"] == 0) {
                            alert(msg["msg"]);
                        };
                    }catch(e){}
                    window.location.reload();
                },
                error: function (msg) {
                    alert("An error occurred!")
                    window.location.reload();
                }
            });
        });

        $(document).on('click', '.filePickerUpload', function(){
            var $this = $(this);
            var $preview_image = $('#'+$this.attr('data-preview_image_id'));
            var $input_url = $('#'+$this.attr('data-image_input_id'));
            var conversion_params = $this.attr('data-conversion_params');
            $preview_image.attr('src','');
            $preview_image.hide();
            filepicker.pickAndStore({
                    mimetypes: ['image/*'],
                    container: 'modal',
                    services: ['COMPUTER', 'FACEBOOK', 'GMAIL']
                }, {
                    location:"S3"
                },
                function (InkBlobs) {
                    var blob = InkBlobs[0];
                    var final_url = blob["url"]+conversion_params;
                    $preview_image.attr('src', final_url);
                    $input_url.val(final_url);
                    $preview_image.show();
                },
                function (FPError) {
                    console.log(FPError);
                }
            );
        });

        $("input[data-label=later]").change(function () {
            var $send_later = $("input[data-label=later]");
            if($send_later.attr("checked") == "checked") {
                $('#send_later_row').show();
            } else {
                $('#send_later_row').hide();
            }
        });
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
} catch(e){
    console.log(e);
}