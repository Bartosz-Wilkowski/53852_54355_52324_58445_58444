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
});