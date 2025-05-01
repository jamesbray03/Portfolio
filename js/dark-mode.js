const toggle = document.getElementById('mode-toggle');
const root = document.documentElement;

// initialize theme from localStorage
if (localStorage.getItem('theme') === 'dark') {
    root.classList.add('dark-mode');
    toggle.textContent = '☀️';
}

toggle.addEventListener('click', () => {
    const isDark = root.classList.toggle('dark-mode');
    toggle.textContent = isDark ? '☀️' : '🌙';
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
});