// Import the jQuery library
const $ = require('jquery');

// Import the JavaScript file containing the functions to be tested
require('../login.js'); // Replace 'your-script-file.js' with the actual file name

describe('Login Form Submission', () => {
    test('should handle form submission with valid input', () => {
        // Mock the AJAX function
        $.ajax = jest.fn().mockImplementation((params) => {
            params.success({ message: 'Login successful', redirect: '/' });
        });

        // Prepare the form input
        document.body.innerHTML = `
            <form id="loginForm">
                <input id="username" value="testuser">
                <input id="password" value="password">
                <button type="submit">Submit</button>
            </form>
            <div id="loginResult"></div>
        `;

        // Trigger the form submission
        $('#loginForm').trigger('submit');

        // Verify if the AJAX function was called with the correct parameters
        expect($.ajax).toHaveBeenCalledWith({
            type: 'POST',
            url: '/login',
            contentType: 'application/json',
            data: JSON.stringify({ username: 'testuser', password: 'password' }),
            success: expect.any(Function),
            error: expect.any(Function)
        });

        // Verify if the login result message is updated
        expect($('#loginResult').text()).toBe('Login successful');

        // Verify if the page is redirected after a delay
        jest.useFakeTimers();
        jest.runAllTimers();
        expect(setTimeout).toHaveBeenCalledWith(expect.any(Function), 100);
        expect(window.location.href).toBe('/');
    });

    test('should handle form submission with missing input', () => {
        // Prepare the form input with missing fields
        document.body.innerHTML = `
            <form id="loginForm">
                <input id="username" value="">
                <input id="password" value="">
                <button type="submit">Submit</button>
            </form>
            <div id="loginResult"></div>
        `;

        // Trigger the form submission
        $('#loginForm').trigger('submit');

        // Verify if the login result message is updated with the error message
        expect($('#loginResult').text()).toBe('Both username and password are required.');
    });
});

describe('Forgot Password Form Submission', () => {
    test('should handle form submission with valid email', () => {
        // Mock the AJAX function
        $.ajax = jest.fn().mockImplementation((params) => {
            params.success({ reset_link: '/reset-password' });
        });

        // Prepare the form input
        document.body.innerHTML = `
            <form id="forgotPasswordForm">
                <input id="resetEmail" value="test@example.com">
                <button type="submit">Submit</button>
            </form>
            <div id="resetResult"></div>
            <div id="resetLink"></div>
        `;

        // Trigger the form submission
        $('#forgotPasswordForm').trigger('submit');

        // Verify if the AJAX function was called with the correct parameters
        expect($.ajax).toHaveBeenCalledWith({
            type: 'POST',
            url: '/reset_password_link',
            contentType: 'application/json',
            data: JSON.stringify({ email: 'test@example.com' }),
            success: expect.any(Function),
            error: expect.any(Function)
        });

        // Verify if the reset result message is updated
        expect($('#resetResult').html()).toBe('A reset link has been sent to your email.');

        // Verify if the reset link is displayed
        expect($('#resetLink').html()).toBe('<a href="/reset-password">/reset-password</a>');
    });

    test('should handle form submission with invalid email', () => {
        // Prepare the form input with invalid email
        document.body.innerHTML = `
            <form id="forgotPasswordForm">
                <input id="resetEmail" value="invalidemail">
                <button type="submit">Submit</button>
            </form>
            <div id="resetResult"></div>
        `;

        // Trigger the form submission
        $('#forgotPasswordForm').trigger('submit');

        // Verify if the reset result message is updated with the error message
        expect($('#resetResult').html()).toBe('Invalid email address.');
    });
});

describe('Forgot Password Modal', () => {
    test('should show the modal', () => {
        // Prepare the modal element
        document.body.innerHTML = `
            <div id="forgotPasswordModal" style="display: none;"></div>
        `;

        // Call the showForgotPassword function
        showForgotPassword();

        // Verify if the modal is shown
        expect($('#forgotPasswordModal').css('display')).toBe('block');
    });

    test('should close the modal and clear reset result and link', () => {
        // Prepare the modal element with reset result and link
        document.body.innerHTML = `
            <div id="forgotPasswordModal" style="display: block;"></div>
            <div id="resetResult">Reset result</div>
            <div id="resetLink">Reset link</div>
        `;

        // Call the closeForgotPassword function
        closeForgotPassword();

        // Verify if the modal is closed
        expect($('#forgotPasswordModal').css('display')).toBe('none');

        // Verify if the reset result and link are cleared
        expect($('#resetResult').html()).toBe('');
        expect($('#resetLink').html()).toBe('');
    });
});