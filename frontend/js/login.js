document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault();

    var formData = {
        username: document.getElementById('username').value,
        password: document.getElementById('password').value
    };

    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('loginResult').textContent = data.message;
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('loginResult').textContent = 'Something went wrong.';
    });
});