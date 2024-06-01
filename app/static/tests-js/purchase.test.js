// Import jQuery library
const $ = require('jquery');

// Import the JavaScript file containing the functions to be tested
require('../purchase.js'); 

describe('Fetch User Data', () => {
    test('should fetch user data and display it on the page', () => {
        // Mock the AJAX function
        $.ajax = jest.fn().mockImplementation((params) => {
            params.success({
                username: 'testuser',
                email: 'test@example.com',
                name: 'Test',
                surname: 'User',
                plan_name: 'Basic'
            });
        });

        // Prepare the HTML structure
        document.body.innerHTML = `
            <div id="username"></div>
            <div id="email"></div>
            <div id="name"></div>
            <div id="surname"></div>
            <div id="plan"></div>
        `;

        // Call the function
        $(document).ready();

        // Verify if user data is displayed on the page
        expect($('#username').text()).toBe('testuser');
        expect($('#email').text()).toBe('test@example.com');
        expect($('#name').text()).toBe('Test');
        expect($('#surname').text()).toBe('User');
        expect($('#plan').text()).toBe('Basic');
    });
});

describe('Fetch Available Plans', () => {
    test('should fetch available plans and populate the select dropdown', () => {
        // Mock the AJAX function
        $.ajax = jest.fn().mockImplementation((params) => {
            params.success([
                { plan_name: 'Basic', price: 10 },
                { plan_name: 'Pro', price: 20 },
                { plan_name: 'Premium', price: 30 }
            ]);
        });

        // Prepare the HTML structure
        document.body.innerHTML = `
            <select id="availableplans"></select>
        `;

        // Call the function
        $(document).ready();

        // Verify if select dropdown is populated with available plans
        expect($('#availableplans option').length).toBe(3);
        expect($('#availableplans option:eq(0)').val()).toBe('Basic');
        expect($('#availableplans option:eq(1)').val()).toBe('Pro');
        expect($('#availableplans option:eq(2)').val()).toBe('Premium');
    });
});

describe('Form Submission', () => {
    test('should handle form submission with valid input', () => {
        // Mock the AJAX function
        $.ajax = jest.fn().mockImplementation((params) => {
            params.success({ message: 'Purchase successful' });
        });

        // Prepare the form input
        document.body.innerHTML = `
            <form id="purchaseForm">
                <select id="availableplans"><option value="Basic">Basic - $10</option></select>
                <input id="cardNumber" value="1234567890123456">
                <input id="cardName" value="Test User">
                <input id="expiryDate" value="12/25">
                <input id="cvc" value="123">
                <button type="submit">Submit</button>
            </form>
            <div id="resultPurchase"></div>
        `;

        // Call the function
        $(document).ready();

        // Trigger the form submission
        $('#purchaseForm').trigger('submit');

        // Verify if purchase result message is displayed
        expect($('#resultPurchase').text()).toBe('Purchase successful');

        // Verify if page is redirected after a delay
        jest.useFakeTimers();
        jest.runAllTimers();
        expect(setTimeout).toHaveBeenCalledWith(expect.any(Function), 100);
        expect(window.location.href).toBe('/userprofile');
    });

});