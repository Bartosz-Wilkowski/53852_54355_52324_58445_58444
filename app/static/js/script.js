const video = document.getElementById('video');
const predictionElement = document.getElementById('prediction');
const historyElement = document.getElementById('history');
const toggleCameraBtn = document.getElementById('toggleCameraBtn');
let historyText = "";
let cameraStream = null;
let captureInterval = null;

// Function to start the camera
function startCamera() {
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            video.srcObject = stream;
            video.style.display = 'block';
            cameraStream = stream;
            toggleCameraBtn.textContent = 'Turn Camera Off';
            startCapturing();
        })
        .catch(err => console.error('Error accessing webcam:', err));
}

// Function to stop the camera
function stopCamera() {
    if (cameraStream) {
        let tracks = cameraStream.getTracks();
        tracks.forEach(track => track.stop());
        video.srcObject = null;
        video.style.display = 'none';
        cameraStream = null;
        toggleCameraBtn.textContent = 'Turn Camera On';
        stopCapturing();
    }
}

// Function to start capturing images
function startCapturing() {
    captureInterval = setInterval(() => {
        const imageData = captureImage().split(',')[1]; 
        socket.emit('image', { image: imageData });
    }, 1000);
}

// Function to stop capturing images
function stopCapturing() {
    clearInterval(captureInterval);
}

// Event listener for the toggle button
toggleCameraBtn.addEventListener('click', function() {
    if (cameraStream) {
        stopCamera();
    } else {
        startCamera();
    }
});

// Function to capture an image from the video
function captureImage() {
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL('image/jpeg');
}

// Get Socket.IO
const socket = io();

// Get prediction from server
socket.on('prediction', data => {
    predictionElement.textContent = `Predicted letter: ${data.prediction}`;
    historyText += data.prediction;
    historyElement.value = historyText;
});
