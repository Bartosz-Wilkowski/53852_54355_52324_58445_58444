/**
 * @fileoverview This file contains the JavaScript for handling navigation, webcam access, section observation, 
 * and updating the footer year.
 */

const nav = document.querySelector('.nav');
const navBtn = document.querySelector('.burger-btn');
const allNavItems = document.querySelectorAll('.nav__item');
const allNavBoxes = document.querySelectorAll('.nav__box');
const navBtnBars = document.querySelector('.burger-btn__bars');
const allSections = document.querySelectorAll('.section');
const footerYear = document.querySelector('.footer__year');
const translateText = document.querySelector('.translate__box-signs');
const translateBtn = document.getElementById('startbtn');

/**
 * Toggles the navigation menu visibility.
 * Adds a class to open the navigation and removes it to close the navigation.
 */
const handleNav = () => {
    nav.classList.toggle('nav--active');

    // Ensure the navigation button bars remain white.
    navBtnBars.classList.remove('black-bars-color');

    // Close the navigation when a navigation item is clicked.
    allNavItems.forEach((item) => {
        item.addEventListener('click', () => {
            nav.classList.remove('nav--active');
        });
    });

    // Handle animations for navigation items.
    handleNavItemsAnimation();
};

/**
 * Handles the animation for the navigation items.
 * Adds an animation class to each item with a delay.
 */
const handleNavItemsAnimation = () => {
    let delayTime = 0;

    allNavItems.forEach((item) => {
        item.classList.toggle('nav-items-animation');
        item.style.animationDelay = '.' + delayTime + 's';
        delayTime++;
    });

    allNavBoxes.forEach((item) => {
        item.classList.toggle('nav-items-animation');
        item.style.animationDelay = '.' + delayTime + 's';
        delayTime++;
    });
};

/**
 * Opens the webcam and displays the video stream in the video element.
 * Ensures that the user's media devices are accessed.
 */
function openCam() {
    let All_mediaDevices = navigator.mediaDevices;
    if (!All_mediaDevices || !All_mediaDevices.getUserMedia) {
        console.log('getUserMedia() not supported.');
        return;
    }
    All_mediaDevices.getUserMedia({
        audio: false,
        video: true,
    })
    .then(function (vidStream) {
        var video = document.getElementById('videocam');
        if ('srcObject' in video) {
            video.srcObject = vidStream;
        } else {
            video.src = window.URL.createObjectURL(vidStream);
        }
        video.onloadedmetadata = function (e) {
            video.play();
        };
    })
    .catch(function (e) {
        console.log(e.name + ': ' + e.message);
    });
}

/**
 * Observes the user's scroll position and changes the navigation button bars' color
 * based on the section's background color.
 */
const handleObserver = () => {
    const currentSection = window.scrollY;

    allSections.forEach((section) => {
        if (section.classList.contains('white-section') && section.offsetTop <= currentSection + 60) {
            navBtnBars.classList.add('black-bars-color');
        } else if (!section.classList.contains('white-section') && section.offsetTop <= currentSection + 60) {
            navBtnBars.classList.remove('black-bars-color');
        }
    });
};

/**
 * Adds a shadow to the navigation bar when the user scrolls down the page.
 */
document.addEventListener('DOMContentLoaded', function () {
    const nav = document.querySelector('.navbar');

    function addShadow() {
        if (window.scrollY >= 50) {
            nav.classList.add('shadow-bg');
        } else {
            nav.classList.remove('shadow-bg');
        }
    }

    window.addEventListener('scroll', addShadow);
});

/**
 * Updates the footer year to the current year.
 */
const handleCurrentYear = () => {
    const year = new Date().getFullYear();
    footerYear.innerText = year;
};

handleCurrentYear();

navBtn.addEventListener('click', handleNav);
window.addEventListener('scroll', handleObserver);
