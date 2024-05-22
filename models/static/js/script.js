const video = document.getElementById('video');
const predictionElement = document.getElementById('prediction');
const historyElement = document.getElementById('history');
let historyText = "";

// get video from webcam
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
    })
    .catch(err => console.error('Error accessing webcam:', err));

// get Socket.IO
const socket = io();

// get img from vid
function captureImage() {
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL('image/jpeg');
}

// sent img to server / 1 sec
setInterval(() => {
    const imageData = captureImage().split(',')[1]; 

    socket.emit('image', { image: imageData });
}, 1000);

// get predicition from server
socket.on('prediction', data => {
    predictionElement.textContent = `Predicted letter: ${data.prediction}`;
    historyText += data.prediction;
    historyElement.value = historyText;
});
