$(document).ready(function () {
    $('#registerForm').submit(function (event) {
        event.preventDefault();

        var formData = {
            'username': $('#username').val(),
            'name': $('#name').val(),
            'surname': $('#surname').val(),
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
                },100);
            },
            error: function (xhr, status, error) {
                var errorMessage = xhr.responseJSON.message;
                $('#message').text(errorMessage);
            }
        });
    });
});