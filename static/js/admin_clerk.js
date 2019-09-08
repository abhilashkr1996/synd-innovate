$('#admin_clerk').submit(function(event){
    $('#server_msg').addClass('d-none');

    if ($('[name="new_password"]').val().length < 6){
        $('#error').html('Password Length less than 6').removeClass('d-none').addClass('d-block').css('color', 'red');  
        return false;
    }
    if ($('[name="new_password"]').val() == $('[name="confirm_password"]').val()) {
        $('#error').html('Passwords Matching').removeClass('d-none').addClass('d-block').css('color', 'green');
        return true;
    } else {
        $('#error').html('Passwords Not Matching').removeClass('d-none').addClass('d-block').css('color', 'red');
        return false;
    }
});