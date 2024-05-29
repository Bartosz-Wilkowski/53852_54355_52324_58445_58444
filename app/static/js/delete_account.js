$(document).ready(function () {
    $('#deleteAccountButton').click(function () {
        $.ajax({
            type: 'POST',
            url: '/delete_account',
            contentType: 'application/json',
            success: function (response) {
                $('#deleteResult').text(response.message);
                if (response.redirect) {
                    setTimeout(function () {
                        window.location.href = response.redirect; // Redirect to home page
                    }, 100); // Adjust the delay if needed
                }
            },
            error: function (xhr, status, error) {
                var errorMessage = xhr.responseJSON ? xhr.responseJSON.message : "An error occurred";
                $('#deleteResult').text(errorMessage);
            }
        });
    });
    // Add click event handler for reset password button
    $('#resetPasswordButton').click(function () {
        $.ajax({
            type: 'GET',
            url: '/generate_reset_token',
            success: function (response) {
                if (response.reset_link) {
                    window.location.href = response.reset_link;
                } else {
                    alert("Error: Failed to generate reset token.");
                }
            },
            error: function (xhr, status, error) {
                alert("Error: " + error);
            }
        });
    });

});