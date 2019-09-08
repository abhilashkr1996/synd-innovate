const loginButton = document.querySelector('#submit_button');
const loginForm = document.querySelector('#login-form');
var idToken = "";
window.localStorage.clear();


loginButton.addEventListener('click', (e) => {
  e.preventDefault();

  const email = loginForm['login-email'].value;
  const password = loginForm['login-password'].value;

  return auth.signInWithEmailAndPassword(email, password).then((cred) => {
        // if (!cred.user.emailVerified){
        //     error = loginForm.querySelector('#error')
        //     error.innerHTML = "Email not Verified. Please verify your email";
        //     $('#error').removeClass('d-none').addClass('d-block').css('color', 'red');
        //     return;
        // }

        return cred.user.getIdToken().then((id) => {
          idToken = id;

          $.ajax({
            url: '/sessionLogin',
            method: "POST",
            dataType: "json",
            data: JSON.stringify({'idToken':id}),
            cache: false,
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json',
            },
            success: function (data) {
                loginForm.submit();
            },
            error: function (response) {
                console.log(response);
                if (response.status == 401){
                  error = loginForm.querySelector('#error')
                  error.innerHTML = response['message'];
                  $('#error').removeClass('d-none').addClass('d-block').css('color', 'red');
                }
            }
        })    
        })
}).catch(err => {
  $('#logout').click();
});

});

