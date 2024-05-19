// Ensure that the code runs only after the entire HTML document has been loaded
$(document).ready(function () { 
  // Form submission event handler
  $('#registrationForm').submit(function (event) { 
      event.preventDefault();
      
      // Collecting form data
      var formData = {
          username: $('#username').val(),
          email: $('#email').val(),
          password: $('#password').val()
      };
      
      // AJAX request to server
      $.ajax({
          url: '/register',
          type: 'POST',
          contentType: 'application/json',
          data: JSON.stringify(formData),
          success: function (response) {
              $('#registerResult').text(response.message);
          },
          error: function (xhr, status, error) {
              console.error('Error:', error);
              var errorMessage = xhr.status + ': ' + xhr.statusText;
              $('#registerResult').text('Something went wrong: ' + errorMessage);
          }
      });
  });
});