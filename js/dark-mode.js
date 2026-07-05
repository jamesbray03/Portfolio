/**
 * Theme toggle (dark-first) + scroll reveal.
 * Dark is the default; html.light-mode opts into light.
 * The inline head script on each page applies the class pre-paint.
 */

const toggle = document.getElementById('mode-toggle');
const root = document.documentElement;

if (toggle) {
    toggle.addEventListener('click', () => {
        const isLight = root.classList.toggle('light-mode');
        localStorage.setItem('theme', isLight ? 'light' : 'dark');
    });
}

// Scroll reveal: elements with .reveal fade in as they enter the viewport.
const revealEls = document.querySelectorAll('.reveal');
if (revealEls.length && 'IntersectionObserver' in window &&
    !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add('in');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.12, rootMargin: '0px 0px -5% 0px' });
    revealEls.forEach((el) => observer.observe(el));
} else {
    revealEls.forEach((el) => el.classList.add('in'));
}
