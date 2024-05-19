$(document).ready(function () {
    $('#purchaseForm').submit(function (event) {
        event.preventDefault();

        var formData = {
            username: $('/#username').val(),
            plan: $('#plan').val(),
            cardNumber: $('#cardNumber').val(),
            cardName: $('#cardName').val(),
            expiryDate: $('#expiryDate').val(),
            cvc: $('#cvc').val()
        };

        $.ajax({
            url: '/purchase',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function (response) {
                $('#result').text(response.message);
            },
            error: function (xhr, status, error) {
                console.error('Error:', error);
                $('#result').text('An error occurred during the purchase.');
            }
        });
    });

    $.ajax({
        url: '/get-user-data',
        type: 'GET',
        success: function (userData) {
            $('#username').text(userData.username);
            $('#email').text(userData.email);
        },
        error: function (xhr, status, error) {
            console.error('Error:', error);
            $('#userData').html('<p>Error retrieving user data.</p>');
        }
    });
});