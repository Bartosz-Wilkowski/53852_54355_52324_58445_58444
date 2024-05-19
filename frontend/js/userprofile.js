$(document).ready(function () {
    // AJAX request to get user data from the server
    $.ajax({
        url: '/get-user-data',
        type: 'GET',
        success: function (userData) {
            $('#username').text(userData.username);
            $('#email').text(userData.email);
            $('#plan').text(userData.plan);
        },
        error: function (xhr, status, error) {
            console.error('Error:', error);
            $('#userData').html('<p>Error retrieving user data.</p>');
        }
    });
});