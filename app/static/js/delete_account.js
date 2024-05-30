$(document).ready(function () {
    /**
     * Handles the account deletion process.
     * Sends an AJAX POST request to delete the account.
     * Displays the result message and redirects if necessary.
     */
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

    /**
     * Handles the password reset token generation process.
     * Sends an AJAX GET request to generate a reset token.
     * Redirects to the reset link if successful.
     */
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
