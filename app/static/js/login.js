$(document).ready(function () {
    $('#loginForm').submit(function (event) {
        event.preventDefault();

        var username = $('#username').val().trim();
        var password = $('#password').val().trim();

        if (!username || !password) {
            $('#loginResult').text('Both username and password are required.');
            return;
        }

        var formData = {
            'username': username,
            'password': password
        };

        $.ajax({
            type: 'POST',
            url: '/login',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function (response) {
                $('#loginResult').text(response.message);
                setTimeout(function () {
                    window.location.href = '/';
                }, 100);
            },
            error: function (xhr) {
                var errorMessage = xhr.responseJSON.message;
                $('#loginResult').text(errorMessage);
            }
        });
    });

    $("#forgotPasswordForm").submit(function (event) {
        event.preventDefault();
        var email = $("#resetEmail").val();

        $.ajax({
            type: "POST",
            url: "/reset_password_link",
            contentType: "application/json",
            data: JSON.stringify({ email: email }),
            success: function (response) {
                $("#resetResult").html("A reset link has been sent to your email.");
                if (response.reset_link) {
                    $("#resetLink").html(`<a href="${response.reset_link}">${response.reset_link}</a>`);
                }
            },
            error: function (xhr) {
                $("#resetResult").html(xhr.responseJSON.message);
            }
        });
    });
});

function showForgotPassword() {
    $("#forgotPasswordModal").show();
}

function closeForgotPassword() {
    $("#forgotPasswordModal").hide();
    $("#resetResult").html("");
    $("#resetLink").html("");
}