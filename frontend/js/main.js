const nav = document.querySelector('.nav');
const navBtn = document.querySelector('.burger-btn');
const allNavItems = document.querySelectorAll('.nav__item');
const allNavBoxes = document.querySelectorAll('.nav__box');
const navBtnBars = document.querySelector('.burger-btn__bars');
const allSections = document.querySelectorAll('.section');
const footerYear = document.querySelector('.footer__year');
const translateText = document.querySelector('.translate__box-signs');

//funkcja, która dodaje klasę nav--active kiedy kliknie się na burger icon (czyli otwiera nawigację)
const handleNav = () => {
	nav.classList.toggle('nav--active');

	//żeby kolor barsów w nawigacji pozostawał biały
	navBtnBars.classList.remove('black-bars-color');

	//żeby nawigacja zamykała się automatycznie po kliknięciu w dany link:
	allNavItems.forEach((item) => {
		item.addEventListener('click', () => {
			nav.classList.remove('nav--active');
		});
	});

	//animacja dla linków znajdujących się w nawigacji
	handleNavItemsAnimation();
};

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

//użycie webcam
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

//zmiana koloru pasków nawigacji (bars) na ciemniejszy (ta funkcja będzie obserwowała, na której sekcji właśnie jest użytkownik)
const handleObserver = () => {
	const currentSection = window.scrollY;

	allSections.forEach((section) => {
		if (
			section.classList.contains('white-section') &&
			section.offsetTop <= currentSection + 60
		) {
			navBtnBars.classList.add('black-bars-color');
		} else if (
			!section.classList.contains('white-section') &&
			section.offsetTop <= currentSection + 60
		) {
			navBtnBars.classList.remove('black-bars-color');
		}
	});
};

// żeby podczas scrollowania pod nawigacją na desktopy dodawał się cień
document.addEventListener('DOMContentLoaded', function () {
	const nav = document.querySelector('.navbar');

	function addShadow() {
		if (window.scrollY >= 50) {
			nav.classList.add('shadow-bg');
		} else {
			nav.classList.remove('shadow-bg');
		}
	}

	window.addEventListener('scroll', addShadow)
});

//żeby w footerze automatycznie był wyświetlany poprawny rok
const handleCurrentYear = () => {
	const year = new Date().getFullYear();
	footerYear.innerText = year;
};

handleCurrentYear();

navBtn.addEventListener('click', handleNav);

//wywołanie funckji zmieniającej kolor pasków nawigacji (barsów):
window.addEventListener('scroll', handleObserver);
