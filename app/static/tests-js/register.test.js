// Import jQuery library
const $ = require('jquery');

// Import the JavaScript file containing the functions to be tested
require('../register.js'); 

describe('User Registration', () => {
    test('should handle form submission with valid input', () => {
        // Mock the AJAX function
        $.ajax = jest.fn().mockImplementation((params) => {
            params.success({ message: 'Registration successful' });
        });

        // Prepare the form input
        document.body.innerHTML = `
            <form id="registerForm">
                <input id="username" value="testuser">
                <input id="name" value="Test">
                <input id="surname" value="User">
                <input id="email" value="test@example.com">
                <input id="password" value="password123">
                <button type="submit">Register</button>
            </form>
            <div id="registerResult"></div>
        `;

        // Call the function
        $(document).ready();

        // Trigger the form submission
        $('#registerForm').trigger('submit');

        // Verify if registration result message is displayed
        expect($('#registerResult').text()).toBe('Registration successful');

        // Verify if page is redirected after a delay
        jest.useFakeTimers();
        jest.runAllTimers();
        expect(setTimeout).toHaveBeenCalledWith(expect.any(Function), 100);
        expect(window.location.href).toBe('/');
    });
});