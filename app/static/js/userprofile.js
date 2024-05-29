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
            $('#plan').text(userData.plan_name);

            // Display payment history
            var paymentHistory = userData.payment_history;
            if (paymentHistory && paymentHistory.length > 0) {
                var paymentHistoryHTML = '';
                paymentHistory.forEach(function(payment) {
                    paymentHistoryHTML += '<p><strong>Payment Date:</strong> ' + payment.payment_date + '</p>';
                    paymentHistoryHTML += '<p><strong>Amount:</strong> ' + payment.amount + '</p>';
                    paymentHistoryHTML += '<hr>'; // Separate each payment entry
                });
                $('#paymentHistory').html(paymentHistoryHTML);
            } else {
                $('#paymentHistory').html('<p>No payment history available</p>');
            }
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
