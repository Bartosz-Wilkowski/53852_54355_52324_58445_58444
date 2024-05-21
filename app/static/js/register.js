$(document).ready(function () {
    $('#registerForm').submit(function (event) {
        event.preventDefault();

        var formData = {
            'username': $('#username').val(),
            'email': $('#email').val(),
            'password': $('#password').val()
        };

        $.ajax({
            type: 'POST',
            url: '/register',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function (response) {
                $('#message').text(response.message);
                setTimeout(function () {
                    window.location.href = '/login';
                }, 2000); // przekierowanie do strony logowania po 2 sekundach
            },
            error: function (xhr, status, error) {
                var errorMessage = xhr.responseJSON.message;
                $('#message').text(errorMessage);
            }
        });
    });
});