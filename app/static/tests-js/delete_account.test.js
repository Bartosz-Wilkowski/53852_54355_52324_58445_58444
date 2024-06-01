// Import the functions to be tested
const $ = require('jquery');
require('../delete_account.js');

describe('Account Deletion Process', () => {
    test('should send AJAX POST request to delete account', () => {
        // Mock the jQuery AJAX function
        $.ajax = jest.fn().mockImplementation((params) => {
            params.success({ message: 'Account deleted successfully', redirect: '/home' });
        });

        // Trigger the click event on #deleteAccountButton
        $('#deleteAccountButton').trigger('click');

        // Verify if the AJAX function was called with the correct parameters
        expect($.ajax).toHaveBeenCalledWith({
            type: 'POST',
            url: '/delete_account',
            contentType: 'application/json',
            success: expect.any(Function),
            error: expect.any(Function)
        });

        // Verify if the deleteResult message is updated
        expect($('#deleteResult').text()).toBe('Account deleted successfully');

        // Verify if the page is redirected to /home after a delay
        jest.useFakeTimers();
        jest.runAllTimers();
        expect(setTimeout).toHaveBeenCalledWith(expect.any(Function), 100);
        expect(window.location.href).toBe('/home');
    });

    test('should handle AJAX error while deleting account', () => {
        // Mock the jQuery AJAX function to simulate an error
        $.ajax = jest.fn().mockImplementation((params) => {
            params.error({}, 'error', 'Internal Server Error');
        });

        // Trigger the click event on #deleteAccountButton
        $('#deleteAccountButton').trigger('click');

        // Verify if the deleteResult message is updated with the error message
        expect($('#deleteResult').text()).toBe('An error occurred');
    });
});

describe('Password Reset Token Generation Process', () => {
    test('should send AJAX GET request to generate reset token', () => {
        // Mock the jQuery AJAX function
        $.ajax = jest.fn().mockImplementation((params) => {
            params.success({ reset_link: '/reset_password' });
        });

        // Trigger the click event on #resetPasswordButton
        $('#resetPasswordButton').trigger('click');

        // Verify if the AJAX function was called with the correct parameters
        expect($.ajax).toHaveBeenCalledWith({
            type: 'GET',
            url: '/generate_reset_token',
            success: expect.any(Function),
            error: expect.any(Function)
        });

        // Verify if the page is redirected to the reset link
        expect(window.location.href).toBe('/reset_password');
    });

    test('should handle AJAX error while generating reset token', () => {
        // Mock the jQuery AJAX function to simulate an error
        $.ajax = jest.fn().mockImplementation((params) => {
            params.error({}, 'error', 'Not Found');
        });

        // Trigger the click event on #resetPasswordButton
        $('#resetPasswordButton').trigger('click');

        // Verify if an alert is shown with the error message
        expect(window.alert).toHaveBeenCalledWith('Error: Not Found');
    });
});