const video = document.getElementById('video');
const placeholder = document.getElementById('placeholder');
const toggleCameraBtn = document.getElementById('toggleCameraBtn');
const toggleRecognitionBtn = document.getElementById('toggleRecognitionBtn');
const clearHistoryBtn = document.getElementById('clearHistoryBtn');
const predictionElement = document.getElementById('prediction');
const historyElement = document.getElementById('history');
let historyText = '';
let cameraStream = null;
let captureInterval = null;
let recognitionPaused = false;
let limitReached = false;

// Function to start the camera
function startCamera() {
	if (limitReached) return; // Prevent starting camera if limit is reached
	navigator.mediaDevices
		.getUserMedia({ video: true })
		.then((stream) => {
			video.srcObject = stream;
			video.style.display = 'block';
			placeholder.style.display = 'none';
			cameraStream = stream;
			toggleCameraBtn.textContent = 'Turn Camera Off';
			startCapturing();
		})
		.catch((err) => console.error('Error accessing webcam:', err));
}

// Function to stop the camera
function stopCamera() {
	if (cameraStream) {
		let tracks = cameraStream.getTracks();
		tracks.forEach((track) => track.stop());
		video.srcObject = null;
		video.style.display = 'none';
		placeholder.style.display = 'block';
		cameraStream = null;
		toggleCameraBtn.textContent = 'Turn Camera On';
		stopCapturing();
	}
}

// Function to start capturing images
function startCapturing() {
	captureInterval = setInterval(() => {
		if (!recognitionPaused && !limitReached) {
			const imageData = captureImage().split(',')[1];
			socket.emit('image', { image: imageData });
		}
	}, 1000);
}

// Function to stop capturing images
function stopCapturing() {
	clearInterval(captureInterval);
}

// Event listener for the toggle camera button
toggleCameraBtn.addEventListener('click', function () {
	if (cameraStream) {
		stopCamera();
	} else {
		startCamera();
	}
});

// Event listener for the toggle recognition button
toggleRecognitionBtn.addEventListener('click', function () {
	recognitionPaused = !recognitionPaused;
	if (recognitionPaused) {
		toggleRecognitionBtn.textContent = 'Resume Recognition';
	} else {
		toggleRecognitionBtn.textContent = 'Pause Recognition';
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
socket.on('prediction', (data) => {
	if (data.prediction === 'space') {
		predictionElement.textContent = `Predicted letter: ${data.prediction}`;
		historyText += ' ';
	} else if (data.prediction === 'del') {
		predictionElement.textContent = `Predicted letter: ${data.prediction}`;
		historyText = historyText.slice(0, -1);
	} else if (
		data.prediction === 'nothing' ||
		data.prediction === 'No hand detected'
	) {
		predictionElement.textContent = `Predicted letter: ${data.prediction}`;
	} else {
		predictionElement.textContent = `Predicted letter: ${data.prediction}`;
		historyText += data.prediction;
		historyElement.value = historyText;
	}
});

// Handle limit reached from server
socket.on('limit_reached', () => {
	if (!limitReached) {
		limitReached = true;
		disableButtons();
		showDialog();
	}
});

// Disable buttons when limit is reached
function disableButtons() {
	toggleCameraBtn.disabled = true;
	toggleRecognitionBtn.disabled = true;
}

// Function to show dialog using SweetAlert2
function showDialog() {
	Swal.fire({
		title: 'Recognition Limit Reached',
		text: 'You have reached your daily limit of recognized characters. Please wait until tomorrow or upgrade your plan.',
		icon: 'info',
		showCancelButton: true,
		allowOutsideClick: false,
		cancelButtonText: 'Upgrade Plan',
		confirmButtonText: 'Not Now',
		customClass: {
			popup: 'swal-wide',
		},
	}).then((result) => {
		// If Upgrade Plan is clicked
		if (result.dismiss === Swal.DismissReason.cancel) {
			window.location.href = '/register';
			// If Not Now is clicked
		} else if (result.dismiss === Swal.DismissReason.confirm) {
			// Create a new element with the message and icon
			const messageElement = document.createElement('div');
			messageElement.style.textAlign = 'center';

			// Create icon element
			const iconElement = document.createElement('div');
			iconElement.innerHTML = `
                <div class="swal2-icon swal2-info">
                    <div class="swal2-icon-content">i</div>
                </div>`;
			messageElement.appendChild(iconElement);

			// Create text element
			const textElement = document.createElement('div');
			textElement.textContent =
				'You have reached your daily limit of recognized characters. Please wait until tomorrow or upgrade your plan.';
			textElement.style.marginTop = '3em';
			messageElement.appendChild(textElement);

			// Create Upgrade Plan button
			const upgradeButton = document.createElement('button');
			upgradeButton.textContent = 'Upgrade Plan';
			upgradeButton.className = 'swal2-cancel swal2-styled';
			upgradeButton.onclick = function () {
				window.location.href = '/register';
			};
			messageElement.appendChild(upgradeButton); // Append Upgrade Plan button to the message

			// Replace the video element with the message
			const videoElement = document.getElementById('video');
			videoElement.parentNode.replaceChild(messageElement, videoElement);
		}
	});
}

// Event listener for the clear history button
clearHistoryBtn.addEventListener('click', function () {
	historyText = '';
	historyElement.value = '';
});

// Check limit on page load
document.addEventListener('DOMContentLoaded', () => {
	socket.emit('check_limit');
});

// Handle limit status from server
socket.on('limit_status', (status) => {
	if (status.limitReached) {
		limitReached = true;
		disableButtons();
	}
});
