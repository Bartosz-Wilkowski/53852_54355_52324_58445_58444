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
    $("#resetPasswordButton").click(function () {
        var newPassword = prompt("Enter your new password:");
        if (newPassword) {
            $.ajax({
                type: "POST",
                url: "/change_password",
                contentType: "application/json",
                data: JSON.stringify({ new_password: newPassword }), // Send new password as JSON
                success: function (response) {
                    alert(response.message);
                },
                error: function (xhr) {
                    var errorMessage = xhr.responseJSON ? xhr.responseJSON.message : "An error occurred";
                    alert(errorMessage);
                    console.error("Error response:", xhr.responseText);  // Debugging statement
                }
            });
        }
    });

});