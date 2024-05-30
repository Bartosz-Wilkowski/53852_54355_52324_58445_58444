/**
 * @fileoverview This file contains the client-side JavaScript for handling user registration.
 * It includes form validation and AJAX request submission to register a new user.
 */

$(document).ready(function () {
    /**
     * Event listener for the registration form submission.
     * Prevents the default form submission, performs validation, and sends an AJAX request to register the user.
     * @param {Event} event - The form submission event.
     */
    $('#registerForm').submit(function (event) {
        event.preventDefault();
        
        /**
         * The username entered by the user.
         * @type {string}
         */
        var username = $('#username').val().trim();

        /**
         * The name entered by the user.
         * @type {string}
         */
        var name = $('#name').val().trim(); 

        /**
         * The surname entered by the user.
         * @type {string}
         */
        var surname = $('#surname').val().trim(); 

        /**
         * The email entered by the user.
         * @type {string}
         */
        var email = $('#email').val().trim(); 

        /**
         * The password entered by the user.
         * @type {string}
         */
        var password = $('#password').val().trim(); 
        
        // Check if any field exceeds 255 characters
        if (username.length > 255 || name.length > 255 || surname.length > 255 || email.length > 255 || password.length > 255) {
            $('#registerResult').text('One or more fields exceed the maximum character limit of 255.');
            return;
        }

        // Basic validation
        if (!username || !name || !surname || !email || !password) {
            $('#registerResult').text('All fields are required.');
            return;
        }

        if (password.length < 8) {
            $('#registerResult').text('Password must be at least 8 characters long.');
            return;
        }

        var emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailPattern.test(email)) {
            $('#registerResult').text('Invalid email format.');
            return;
        }

        var namePattern = /^[A-Za-z]+$/;
        if (!namePattern.test(name)) {
            $('#registerResult').text('Name must contain only letters.');
            return;
        }

        if (!namePattern.test(surname)) {
            $('#registerResult').text('Surname must contain only letters.');
            return;
        }
        
        /**
         * The form data to be sent in the AJAX request.
         * @type {Object}
         */
        var formData = {
            'username': username,
            'name': name,
            'surname': surname,
            'email': email,
            'password': password
        };

        // Send AJAX request to register the user
        $.ajax({
            type: 'POST',
            url: '/register',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function (response) {
                $('#registerResult').text(response.message);
                setTimeout(function () {
                    window.location.href = '/';
                }, 100);
            },
            error: function (xhr, status, error) {
                var errorMessage = xhr.responseJSON.message;
                $('#registerResult').text(errorMessage);
            }
        });
    });
});
