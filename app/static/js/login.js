$(document).ready(function () {
    $('#loginForm').submit(function (event) {
        event.preventDefault();

        var formData = {
            'username': $('#username').val(),
            'password': $('#password').val()
        };

        $.ajax({
            type: 'POST',
            url: '/login',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function (response) {
                $('#loginResult').text(response.message);
                setTimeout(function () {
                    window.location.href = '/userprofile'; // Redirect to home page
                }, 2000); // przekierowanie do strony głównej po 2 sekundach
            },
            error: function (xhr, status, error) {
                var errorMessage = xhr.responseJSON.message;
                $('#loginResult').text(errorMessage);
            }
        });
    });
});