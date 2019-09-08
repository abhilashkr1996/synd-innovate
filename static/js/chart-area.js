var chart;

function requestData() {
  $.ajax({
      url: '/get_traffic',
      success: function(point) {
          var series = chart.series[0],
              shift = series.data.length > 30;
          chart.series[0].addPoint(point['value'], true, shift);
      },
      cache: false
     });
}

function live_chart() {
    chart = Highcharts.chart('myAreaChart', {
        chart: {
            type: 'spline',
            events: {
                load: requestData
            }
        },
        title: {
          style : {
            display : 'none'
        }},
        credits: {
          enabled: false
        },
        xAxis: {
            type: 'datetime',
            tickPixelInterval: 150,
            maxZoom: 20 * 1000
        },
        exporting: {
          enabled: false
        },
        yAxis: {
            minPadding: 0.2,
            maxPadding: 0.2,
            title: {
                text: 'Request Count',
                margin: 80
            }
        },
        series: [{
            name: 'Traffic',
            data: []
        }]
    });        
}

function tabValues(){
    $.ajax({
        url: '/tab_values',
        method: "GET",
        cache: false,
        headers: {
          'Accept': 'application/json',
        },
        success: function (data) {
            $('#turntime').html(data['turntime']+' seconds');
            $('#pending').html(data['pending']);
            $('#served').html(data['served']);
        },
        error: function (response) {
            $('#turntime').html("NA");
            $('#pending').html("NA");
            $('#served').html("NA");
        }
    });
}

setInterval(function(){
    requestData();
    tabValues();
},1000);

document.addEventListener('DOMContentLoaded', function() {
    live_chart();
    tabValues();
});