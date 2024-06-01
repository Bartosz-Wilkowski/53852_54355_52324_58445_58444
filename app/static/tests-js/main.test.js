/**
 * @jest-environment jsdom
 */


// handleNav function test

const handleNav = require('../js/main').handleNav;

document.body.innerHTML = `
    <div class="nav"></div>
    <div class="burger-btn"></div>
    <div class="burger-btn__bars"></div>
    <div class="nav__item"></div>
    <div class="nav__box"></div>
`;

test('toggles navigation menu visibility', () => {
    const nav = document.querySelector('.nav');
    const navBtnBars = document.querySelector('.burger-btn__bars');

    handleNav();

    expect(nav.classList.contains('nav--active')).toBe(true);
    expect(navBtnBars.classList.contains('black-bars-color')).toBe(false);
});

test('closes navigation menu when nav item is clicked', () => {
    const nav = document.querySelector('.nav');
    const navItem = document.querySelector('.nav__item');

    nav.classList.add('nav--active');
    navItem.click();

    expect(nav.classList.contains('nav--active')).toBe(false);
});

// handleNavItemsAnimation test

const handleNavItemsAnimation = require('./path/to/your/code').handleNavItemsAnimation;

document.body.innerHTML = `
    <div class="nav__item"></div>
    <div class="nav__item"></div>
    <div class="nav__box"></div>
    <div class="nav__box"></div>
`;

test('adds animation class to nav items and sets animation delay', () => {
    const navItems = document.querySelectorAll('.nav__item');
    const navBoxes = document.querySelectorAll('.nav__box');

    handleNavItemsAnimation();

    navItems.forEach((item, index) => {
        expect(item.classList.contains('nav-items-animation')).toBe(true);
        expect(item.style.animationDelay).toBe(`.${index}s`);
    });

    navBoxes.forEach((box, index) => {
        expect(box.classList.contains('nav-items-animation')).toBe(true);
        expect(box.style.animationDelay).toBe(`.${navItems.length + index}s`);
    });
});

// openCam function test

const openCam = require('./path/to/your/code').openCam;

test('logs error message if getUserMedia is not supported', () => {
    const logSpy = jest.spyOn(console, 'log').mockImplementation();

    openCam();

    expect(logSpy).toHaveBeenCalledWith('getUserMedia() not supported.');

    logSpy.mockRestore();
});


// handleObserver function test

const handleObserver = require('./path/to/your/code').handleObserver;

document.body.innerHTML = `
    <div class="section"></div>
    <div class="section white-section"></div>
    <div class="burger-btn__bars"></div>
`;

test('adds black-bars-color class to nav button bars based on section', () => {
    const navBtnBars = document.querySelector('.burger-btn__bars');
    const whiteSection = document.querySelector('.white-section');

    Object.defineProperty(window, 'scrollY', { value: whiteSection.offsetTop - 50 });

    handleObserver();

    expect(navBtnBars.classList.contains('black-bars-color')).toBe(true);
});

// handleCurrentYear function test

const handleCurrentYear = require('./path/to/your/code').handleCurrentYear;

document.body.innerHTML = `
    <div class="footer__year"></div>
`;

test('updates footer year to current year', () => {
    const footerYear = document.querySelector('.footer__year');
    const currentYear = new Date().getFullYear();

    handleCurrentYear();

    expect(footerYear.innerText).toBe(currentYear.toString());
});
