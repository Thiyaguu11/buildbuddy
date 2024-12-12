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

function updateProgress(percent) {
    if (typeof percent !== 'number' || isNaN(percent)) {
        console.error('Invalid progress value:', percent);
        return;
    }
    const progress = document.getElementById('buildProgress');
    const percentText = document.getElementById('progressPercent');
    progress.style.width = Math.min(100, Math.max(0, percent)) + '%';
    percentText.textContent = Math.round(percent) + '%';
}

function start_nagare_build() {
    const field1 = document.getElementById("field1").value.trim();
    const field2 = document.getElementById("field2").value.trim();
    const field3 = document.getElementById("field3").value.trim();
    const specificChecked = document.getElementById("specificCheckbox").checked;

    if (!field1 || !field2) {
        showPopup("Version and Customer are required.");
        return;
    }

    if (specificChecked && !field3) {
        showPopup("Specific build empty");
        return;
    }

    const data = {
        field1: field1,
        field2: field2,
        field3: specificChecked ? field3 : '',
    };

    const terminalOutput = document.getElementById("terminalOutput");
    terminalOutput.innerHTML = "<p class='output-line'>Starting nagare Build...</p>";

    const statusLabel = document.getElementById("status-label");
    const statusIndicator = document.getElementById("status-indicator");
    statusLabel.textContent = `Building ${field1} for ${field2}`;
    statusIndicator.classList.remove("idle");
    statusIndicator.classList.add("running");

    fetch("/start_nagare", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
    })
    .then(response => {
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
 
 
        function read() {
            reader.read().then(({ done, value }) => {
                if (done) return;
                const newContent = decoder.decode(value);
                terminalOutput.innerHTML += newContent;
                terminalOutput.scrollTop = terminalOutput.scrollHeight;
                read();
            });
        }
        read();
    })
    .catch((error) => {
        showPopup('Error: ' + error);
        terminalOutput.innerHTML += "<p class='output-line' style='color:red;'>Error: " + error + "</p>";
        statusLabel.textContent = "Ready to build";
        statusIndicator.classList.remove("running");
        statusIndicator.classList.add("idle");
    });
}

function stop_nagare_build() {
    fetch("/stop_nagare", {
        method: "POST"
    })
    .then(response => response.json())
    .then(data => {
        showPopup(data.message);
        const statusLabel = document.getElementById("status-label");
        const statusIndicator = document.getElementById("status-indicator");
        statusLabel.textContent = "Ready to build";
        statusIndicator.classList.remove("running");
        statusIndicator.classList.add("idle");
    })
    .catch((error) => {
        showPopup('Error: ' + error);
    });
}

let statusPollingInterval;

function startStatusPolling() {
    if (statusPollingInterval) clearInterval(statusPollingInterval);
    statusPollingInterval = setInterval(() => {
        fetch('/status')
        .then(response => response.json())
        .then(data => {
            const statusLabel = document.getElementById("status-label");
            const statusIndicator = document.getElementById("status-indicator");
            const terminalOutput = document.getElementById("terminalOutput");
            
            if (data.status === 'running') {
                statusLabel.textContent = `Building ${data.version} for ${data.customer}`;
                if (data.terminal) {
                    terminalOutput.innerHTML = data.terminal;
                    terminalOutput.scrollTop = terminalOutput.scrollHeight;
                }
                updateProgress(data.progress);
            } else {
                statusLabel.textContent = "Ready to build";
            }
            statusIndicator.className = `status-indicator ${data.status}`;
        })
        .catch((error) => {
            console.error('Error fetching status:', error);
            const statusIndicator = document.getElementById("status-indicator");
            statusIndicator.className = 'status-indicator error';
        });
    }, 1000);
}

function showPopup(message) {
    const popup = document.createElement('div');
    popup.className = 'popup';
    popup.textContent = message;
    document.body.appendChild(popup);
    
    setTimeout(() => popup.remove(), 3000);
}

window.addEventListener('beforeunload', function() {
    if (statusPollingInterval) {
        clearInterval(statusPollingInterval);
    }
});

window.addEventListener('load', function() {
    loadTheme();
    document.getElementById('themeToggle').addEventListener('click', toggleTheme);
    document.getElementById('specificField').style.display = document.getElementById('specificCheckbox').checked ? 'block' : 'none';
    startStatusPolling();
});

document.addEventListener('DOMContentLoaded', function() {
    loadTheme();
    document.getElementById('themeToggle').addEventListener('click', toggleTheme);
});

document.getElementById('specificCheckbox').addEventListener('change', function() {
    document.getElementById('specificField').style.display = this.checked ? 'block' : 'none';
});
