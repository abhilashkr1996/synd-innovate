$(document).ready(function(){
    var timer = new Timer();
    
    if (localStorage.getItem('time') != null){
        timer.start({precision: 'seconds', startValues: {seconds: parseInt(localStorage.getItem('time'))}});
    }else{
        timer.start();
    }
    timer.addEventListener('secondsUpdated', function (e) {
        $('#timer').html(timer.getTimeValues().toString());
    });

    window.onbeforeunload = function(event) {
        if (timer){
            localStorage.removeItem('time');
            localStorage.setItem('time',timer.getTimeValues().seconds);
        }
        return null;
    };

    $('#next_request').submit(function(eventObj) {
        window.onbeforeunload = null;
        localStorage.clear();
        var time_elapsed = timer.getTimeValues().seconds;
        var req_id = $('#request_id').text();
        var updated_dt = new Date();
        $(this).append('<input type="hidden" name="processing_time" value="'+ time_elapsed +'" /> ');
        $(this).append('<input type="hidden" name="req_id" value="'+ req_id +'" /> ');
        $(this).append('<input type="hidden" name="datetime" value="'+ updated_dt +'" /> ');
        return true;
    });
});