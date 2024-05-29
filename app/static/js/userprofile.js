$(document).ready(function () {
    // AJAX request to get user data from the server
    $.ajax({
        url: '/get-user-data',
        type: 'GET',
        success: function (userData) {
            $('#username').text(userData.username);
            $('#email').text(userData.email);
            $('#name').text(userData.name);
            $('#surname').text(userData.surname);
            $('#plan').text(userData.plan);
        },
        error: function (xhr, status, error) {
            console.error('Error:', error);
            if (xhr.status === 401) { // Check for unauthorized status
                window.location.href = '/'; // Redirect
            } else {
                $('#userData').html('<p>Error retrieving user data.</p>');
            }
        }
    });
});
