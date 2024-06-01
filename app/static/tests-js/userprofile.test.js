// Import the necessary modules for testing
const $ = require('jquery');
const { XMLHttpRequest } = require('xmlhttprequest');

// Mock the jQuery AJAX method
$.ajax = jest.fn();

describe('User Data Retrieval', () => {
    // Test case for successful AJAX request
    it('should fetch user data and update DOM on success', () => {
        // Mock user data response from the server
        const userData = {
            username: 'testUser',
            email: 'test@example.com',
            name: 'John',
            surname: 'Doe',
            plan_name: 'Premium',
            payment_history: [
                { payment_date: '2024-05-01', amount: 10 },
                { payment_date: '2024-04-15', amount: 10 }
            ]
        };

        // Mock the success callback function
        const successCallback = jest.fn().mockImplementation((callback) => callback(userData));

        // Call the AJAX mock function with success callback
        $.ajax.mockImplementationOnce(({ success }) => success(successCallback));

        // Call the function that retrieves user data
        require('./user-data-retrieval');

        // Check if DOM elements are updated with user data
        expect($('#username').text()).toBe(userData.username);
        expect($('#email').text()).toBe(userData.email);
        expect($('#name').text()).toBe(userData.name);
        expect($('#surname').text()).toBe(userData.surname);
        expect($('#plan').text()).toBe(userData.plan_name);

        // Check if payment history is displayed
        userData.payment_history.forEach((payment, index) => {
            expect($('#paymentHistory').html()).toContain(`<strong>Payment Date:</strong> ${payment.payment_date}`);
            expect($('#paymentHistory').html()).toContain(`<strong>Amount:</strong> ${payment.amount}`);
            if (index < userData.payment_history.length - 1) {
                expect($('#paymentHistory').html()).toContain('<hr>');
            }
        });
    });

    // Test case for failed AJAX request
    it('should handle error and redirect on unauthorized request', () => {
        // Mock error response from the server
        const xhr = new XMLHttpRequest();
        xhr.status = 401;
        xhr.responseJSON = { message: 'Unauthorized' };

        // Mock the error callback function
        const errorCallback = jest.fn().mockImplementation((callback) => callback(xhr.status, 'error', xhr.responseJSON.message));

        // Call the AJAX mock function with error callback
        $.ajax.mockImplementationOnce(({ error }) => error(errorCallback));

        // Mock window.location.href to capture redirect
        delete window.location;
        window.location = { href: '' };

        // Call the function that retrieves user data
        require('./user-data-retrieval');

        // Check if the window is redirected to the homepage
        expect(window.location.href).toBe('/');
    });
});