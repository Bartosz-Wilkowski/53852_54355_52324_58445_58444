$(document).ready(function () {
    $('#deleteAccountButton').click(function () {
        $.ajax({
            type: 'POST',
            url: '/delete_account',
            contentType: 'application/json',
            success: function (response) {
                $('#deleteResult').text(response.message);
                setTimeout(function () {
                    window.location.href = '/'; // Redirect to home page
                }, 2000); // Adjust the delay if needed
            },
            error: function (xhr, status, error) {
                var errorMessage = xhr.responseJSON ? xhr.responseJSON.message : "An error occurred";
                $('#deleteResult').text(errorMessage);
            }
        });
    });
});
