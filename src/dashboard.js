const THEMES = {
    LIGHT: 'light',
    DARK: 'dark'
};

function loadTheme() {
    const savedTheme = localStorage.getItem('theme') || THEMES.DARK;
    document.documentElement.setAttribute('data-theme', savedTheme);
}

function toggleTheme() {
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-theme');
    const newTheme = currentTheme === THEMES.LIGHT ? THEMES.DARK : THEMES.LIGHT;
    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
}

function updateBuildStats() {
    fetch('/build_stats')
        .then(response => response.json())
        .then(data => {
            document.getElementById('kompassBuilds').textContent = data.kompass.total;
            document.getElementById('nagareBuilds').textContent = data.nagare.total;
            
            document.getElementById('successfulkompassBuilds').textContent = data.kompass.successful;
            document.getElementById('successfulnagareBuilds').textContent = data.nagare.successful;
            
            document.getElementById('failedkompassBuilds').textContent = data.kompass.failed;
            document.getElementById('failednagareBuilds').textContent = data.nagare.failed;
        })
        .catch(error => console.error('Error fetching build stats:', error));
}

document.addEventListener('DOMContentLoaded', function() {
    loadTheme();
    document.getElementById('themeToggle').addEventListener('click', toggleTheme);
    updateBuildStats();
    setInterval(updateBuildStats, 30000);
});