/**
 * @fileoverview This file contains the client-side JavaScript for fetching user data, displaying available plans,
 * and handling the purchase form submission.
 */

$(document).ready(function () {
    // Get plan from URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const selectedPlan = urlParams.get('plan');

    // Fetch user data from the server and display it on the page
  /**
     * Fetch user data from the server and display it on the page.
     */
    $.ajax({
        url: '/get-user-data',
        type: 'GET',
        success: function (userData) {
            $('#username').text(userData.username);
            $('#email').text(userData.email);
            $('#name').text(userData.name);
            $('#surname').text(userData.surname);
            $('#plan').text(userData.plan_name);
        },
        error: function (xhr, status, error) {
            console.error('Error:', error);
            $('#result').html('<p>Error retrieving user data.</p>');
        }
    });

      /**
     * Fetch available plans from the server and populate the select dropdown.
     */
    $.ajax({
        url: '/get-plans',
        type: 'GET',
        success: function (plans) {
            plans.forEach(function (plan) {
                const option = $('<option>', {
                    value: plan.plan_name,
                    text: plan.plan_name + ' - $' + plan.price,
                    selected: plan.plan_name === selectedPlan // Set as selected if it matches the plan in the URL
                });
                $('#availableplans').append(option);
            });
        },
        error: function (xhr, status, error) {
            console.error('Error:', error);
        }
    });

      /**
     * Event listener for the purchase form submission.
     * Prevents the default form submission, performs validation, and sends an AJAX request to purchase a plan.
     * @param {Event} event - The form submission event.
     */
    $('#purchaseForm').submit(function (event) {
        event.preventDefault();
        
        /**
         * The form data to be sent in the AJAX request.
         * @type {Object}
         */
        var formData = {
            'newplan': $('#availableplans').val().trim(),
            'cardNumber': $('#cardNumber').val().trim(),
            'cardName': $('#cardName').val().trim(),
            'expiryDate': $('#expiryDate').val().trim(),
            'cvc': $('#cvc').val().trim()
        };

        // Check if any field exceeds 255 characters
        if (formData.newplan.length > 255 || formData.cardNumber.length > 255 || formData.cardName.length > 255 || formData.expiryDate.length > 255 || formData.cvc.length > 255) {
            $('#resultPurchase').text('One or more fields exceed the maximum character limit of 255.');
            return;
        }

        // Basic validation
        if (!formData.newplan || !formData.cardNumber || !formData.cardName || !formData.expiryDate || !formData.cvc) {
            $('#resultPurchase').text('All fields are required.');
            return;
        }

        // Validate card number (basic Luhn algorithm check could be added for more complexity)
        var cardNumberPattern = /^\d{16}$/;
        if (!cardNumberPattern.test(formData.cardNumber)) {
            $('#resultPurchase').text('Invalid card number. It should be 16 digits.');
            return;
        }

        // Validate card name (only letters and spaces)
        var cardNamePattern = /^[A-Za-z\s]+$/;
        if (!cardNamePattern.test(formData.cardName)) {
            $('#resultPurchase').text('Card name should only contain letters and spaces.');
            return;
        }

        // Validate expiry date (MM/YY)
        var expiryDatePattern = /^(0[1-9]|1[0-2])\/?([0-9]{2})$/;
        if (!expiryDatePattern.test(formData.expiryDate)) {
            $('#resultPurchase').text('Invalid expiry date format. Use MM/YY.');
            return;
        }

        // Validate CVC (3 or 4 digits)
        var cvcPattern = /^[0-9]{3,4}$/;
        if (!cvcPattern.test(formData.cvc)) {
            $('#resultPurchase').text('Invalid CVC. It should be 3 or 4 digits.');
            return;
        }

        // Send AJAX request to purchase the plan
        $.ajax({
            type: 'POST',
            url: '/purchase_plan',
            contentType: 'application/json',
            data: JSON.stringify(formData), // Send data as JSON
            success: function (response) {
                $('#resultPurchase').text(response.message);
                setTimeout(function () {
                    window.location.href = '/userprofile';
                }, 100);
            },
            error: function (xhr, status, error) {
                var errorMessage = xhr.responseJSON.message;
                $('#resultPurchase').text(errorMessage);
            }
        });
    });
});
