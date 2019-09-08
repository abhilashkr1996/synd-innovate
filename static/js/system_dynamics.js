
function set(){
    $("#p_value").html($('#p_slider').val());
    $("#a_value").html($('#a_slider').val());
    $("#cvp_value").html($('#cvp_slider').val());
    $("#cva_value").html($('#cva_slider').val());
    $("#m_value").html($('#m_slider').val());
}

function average_arrival_time(a_val){
    $('#ar').html((1/a_val).toFixed(3));
}

function avg_wt_lq(a, p, m, cvp, cva){
    u = (p / (a * m));
    T = (p/m) * (Math.pow(u, Math.sqrt(2 * m + 1)-1)/(1-u)) * ((cva * cva + cvp * cvp)/2)
    $("#awt").html(T.toFixed(3)+" minutes");
    $("#alq").html((T/a).toFixed(3));
}

function utilization_rate(p_val, a_val, m_val){
    $('#ur').html((p_val/(a_val * m_val)*100).toFixed(3)+" %");
}

function cycle_time(p_val, m_val){
    $('#ct').html((p_val/m_val).toFixed(3));
}

function pipeline(){
    var a_val = $('#a_slider').val(), p_val = $('#p_slider').val(), m_val = $('#m_slider').val(), cva_val = $("#cva_slider").val(), cvp_val = $("#cvp_slider").val();
    set();
    average_arrival_time(a_val);
    cycle_time(p_val, m_val);
    utilization_rate(p_val, a_val, m_val);
    avg_wt_lq(a_val, p_val, m_val, cvp_val, cva_val);
}

$("input[type=range]").on("input", function(){
    pipeline();
});

$(document).ready(function(){
    pipeline();
});