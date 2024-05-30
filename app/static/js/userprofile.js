/**
 * @fileoverview This file contains the client-side JavaScript for handling user data retrieval and display on the web page.
 * It uses jQuery for making AJAX requests to the server and updating the DOM with user information.
 */

$(document).ready(function () {
    /**
     * AJAX request to get user data from the server.
     */
    $.ajax({
        url: '/get-user-data',
        type: 'GET',
        /**
         * Callback function for successful AJAX request.
         * @param {Object} userData - The user data returned from the server.
         * @param {string} userData.username - The username of the user.
         * @param {string} userData.email - The email of the user.
         * @param {string} userData.name - The first name of the user.
         * @param {string} userData.surname - The surname of the user.
         * @param {string} userData.plan_name - The subscription plan of the user.
         * @param {Array<Object>} userData.payment_history - The payment history of the user.
         */
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
                paymentHistory.forEach(function (payment) {
                    paymentHistoryHTML += '<p><strong>Payment Date:</strong> ' + formatDate(payment.payment_date) + '</p>';
                    function formatDate(dateString) {
                        var date = new Date(dateString);
                        var options = { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' };
                        return date.toLocaleDateString('en-GB', options);
                    }
                    paymentHistoryHTML += '<p><strong>Amount:</strong> ' + payment.amount + '</p>';
                    paymentHistoryHTML += '<hr>'; // Separate each payment entry
                });
                $('#paymentHistory').html(paymentHistoryHTML);
            } else {
                $('#paymentHistory').html('<p>No payment history available</p>');
            }
        },
        /**
         * Callback function for failed AJAX request.
         * @param {Object} xhr - The XMLHttpRequest object.
         * @param {string} status - The status of the request.
         * @param {string} error - The error message.
         */
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
