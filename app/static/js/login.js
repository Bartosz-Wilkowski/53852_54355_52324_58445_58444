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
                    window.location.href = '/'; // Redirect to home page
                }, 100); 
            },
            error: function (xhr, status, error) {
                var errorMessage = xhr.responseJSON.message;
                $('#loginResult').text(errorMessage);
            }
        });
    });
});