$(document).ready(function () {
    // Fetch user data and display it
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
            $('#result').html('<p>Error retrieving user data.</p>');
        }
    });

    // Handle form submission
    $('#purchaseForm').submit(function (event) {
        event.preventDefault();

        var formData = {
            'newplan': $('#newplan').val(),
            'cardNumber': $('#cardNumber').val(),
            'cardName': $('#cardName').val(),
            'expiryDate': $('#expiryDate').val(),
            'cvc': $('#cvc').val()
        };

        $.ajax({
            type: 'POST',
            url: '/purchase_plan',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function (response) {
                $('#result').text(response.message);
                setTimeout(function () {
                    window.location.href = '/userprofile'; // Redirect to user profile after 2 seconds
                }, 100);
            },
            error: function (xhr, status, error) {
                var errorMessage = xhr.responseJSON.message;
                $('#result').text(errorMessage);
            }
        });
    });
});
