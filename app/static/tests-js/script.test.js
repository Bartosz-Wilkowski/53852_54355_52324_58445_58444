/**
 * @jest-environment jsdom
 */

const { JSDOM } = require('jsdom');
const fs = require('fs');
const path = require('path');

// Load the HTML into the JSDOM environment
const html = fs.readFileSync(path.resolve(__dirname, '../src/index.html'), 'utf8');
let document;

// Function to setup DOM before each test
beforeEach(() => {
    const dom = new JSDOM(html);
    document = dom.window.document;
    global.document = document;
    global.window = dom.window;
    global.navigator = dom.window.navigator;
});

// Import the code to be tested
require('../src/script.js');

describe('Camera Functions', () => {
    // Test to check if startCamera accesses user media
    test('startCamera should access user media', () => {
        const mockGetUserMedia = jest.fn(() =>
            Promise.resolve({
                getTracks: () => [{ stop: jest.fn() }],
            })
        );
        global.navigator.mediaDevices = { getUserMedia: mockGetUserMedia };
        
        const video = document.createElement('video');
        video.setAttribute('id', 'video');
        document.body.appendChild(video);

        startCamera();

        expect(mockGetUserMedia).toHaveBeenCalledWith({ video: true });
    });

    // Test to check if stopCamera stops the video stream
    test('stopCamera should stop the video stream', () => {
        const mockStream = {
            getTracks: jest.fn(() => [
                { stop: jest.fn() },
            ]),
        };

        global.navigator.mediaDevices = {
            getUserMedia: jest.fn(() => Promise.resolve(mockStream)),
        };

        const video = document.createElement('video');
        video.setAttribute('id', 'video');
        document.body.appendChild(video);

        // Start camera to initialize cameraStream
        startCamera();
        // Simulate async behavior
        return new Promise(setImmediate).then(() => {
            stopCamera();
            expect(mockStream.getTracks().forEach).toHaveBeenCalled();
        });
    });
});

describe('Button Functions', () => {
    // Test to check if toggleCameraBtn click calls startCamera or stopCamera
    test('toggleCameraBtn click should call startCamera or stopCamera', () => {
        const startCameraMock = jest.spyOn(global, 'startCamera').mockImplementation(() => {});
        const stopCameraMock = jest.spyOn(global, 'stopCamera').mockImplementation(() => {});

        const toggleCameraBtn = document.createElement('button');
        toggleCameraBtn.setAttribute('id', 'toggleCameraBtn');
        document.body.appendChild(toggleCameraBtn);

        toggleCameraBtn.click();
        expect(startCameraMock).toHaveBeenCalled();

        global.cameraStream = {}; // Simulate that the camera is running
        toggleCameraBtn.click();
        expect(stopCameraMock).toHaveBeenCalled();
    });

    // Test to check if clearHistoryBtn click clears the history
    test('clearHistoryBtn click should clear the history', () => {
        const clearHistoryBtn = document.createElement('button');
        clearHistoryBtn.setAttribute('id', 'clearHistoryBtn');
        document.body.appendChild(clearHistoryBtn);

        const historyElement = document.createElement('textarea');
        historyElement.setAttribute('id', 'history');
        document.body.appendChild(historyElement);

        historyText = 'some text';
        historyElement.value = 'some text';

        clearHistoryBtn.click();

        expect(historyText).toBe('');
        expect(historyElement.value).toBe('');
    });
});

describe('Socket.IO Handlers', () => {
    // Test to check if predictionElement and historyText are updated on receiving prediction
    test('should update predictionElement and historyText', () => {
        const predictionElement = document.createElement('div');
        predictionElement.setAttribute('id', 'prediction');
        document.body.appendChild(predictionElement);

        const historyElement = document.createElement('textarea');
        historyElement.setAttribute('id', 'history');
        document.body.appendChild(historyElement);

        const mockSocket = {
            on: jest.fn((event, handler) => {
                if (event === 'prediction') {
                    handler({ prediction: 'A' });
                }
            }),
            emit: jest.fn(),
        };

        global.io = jest.fn(() => mockSocket);
        require('../src/your-code.js'); // Re-import to bind socket events

        expect(predictionElement.textContent).toBe('Predicted letter: A');
        expect(historyText).toBe('A');
        expect(historyElement.value).toBe('A');
    });
});