$(document).ready(function () {
    $('#registerForm').submit(function (event) {
        event.preventDefault();

        var username = $('#username').val().trim();
        var name = $('#name').val().trim();
        var surname = $('#surname').val().trim();
        var email = $('#email').val().trim();
        var password = $('#password').val().trim();

        // Basic validation
        if (!username || !name || !surname || !email || !password) {
            $('#registerResult').text('All fields are required.');
            return;
        }

        if (password.length < 8) {
            $('#registerResult').text('Password must be at least 8 characters long.');
            return;
        }

        if (password.length < 8) {
            $('#registerResult').text('Password must be at least 8 characters long.');
            return;
        }

        var emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailPattern.test(email)) {
            $('#registerResult').text('Invalid email format.');
            return;
        }

        var namePattern = /^[A-Za-z]+$/;
        if (!namePattern.test(name)) {
            $('#registerResult').text('Name must contain only letters.');
            return;
        }

        if (!namePattern.test(surname)) {
            $('#registerResult').text('Surname must contain only letters.');
            return;
        }
        
        var formData = {
            'username': username,
            'name': name,
            'surname': surname,
            'email': email,
            'password': password
        };

        $.ajax({
            type: 'POST',
            url: '/register',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function (response) {
                $('#registerResult').text(response.message);
                setTimeout(function () {
                    window.location.href = '/login';
                }, 100);
            },
            error: function (xhr, status, error) {
                var errorMessage = xhr.responseJSON.message;
                $('#registerResult').text(errorMessage);
            }
        });
    });
});
