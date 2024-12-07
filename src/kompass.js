const THEMES = {
    LIGHT: 'light',
    DARK: 'dark'
};

function loadTheme() {
    const savedTheme = localStorage.getItem('theme') || THEMES.LIGHT;
    document.documentElement.setAttribute('data-theme', savedTheme);
}

function updateProgress(percent) {
    const progress = document.getElementById('buildProgress');
    const percentText = document.getElementById('progressPercent');
    progress.style.width = percent + '%';
    percentText.textContent = percent + '%';
}

function toggleTheme() {
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-theme');
    const newTheme = currentTheme === THEMES.LIGHT ? THEMES.DARK : THEMES.LIGHT;
    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
}

document.addEventListener('DOMContentLoaded', function() {
    loadTheme();
    document.getElementById('themeToggle').addEventListener('click', toggleTheme);
});

document.getElementById('specificCheckbox').addEventListener('change', function() {
    document.getElementById('specificField').style.display = this.checked ? 'block' : 'none';
});

document.getElementById('scalingCheckbox').addEventListener('change', function() {
    document.getElementById('scalingField').style.display = this.checked ? 'block' : 'none';
});

window.addEventListener('load', function() {
    loadTheme();
    document.getElementById('themeToggle').addEventListener('click', toggleTheme);
    document.getElementById('specificField').style.display = document.getElementById('specificCheckbox').checked ? 'block' : 'none';
    document.getElementById('scalingField').style.display = document.getElementById('scalingCheckbox').checked ? 'block' : 'none';
    startStatusPolling();
});

function start_kompass_build() {
    const field1 = document.getElementById("field1").value.trim();
    const field2 = document.getElementById("field2").value.trim();
    const field3 = document.getElementById("field3").value.trim();
    const field4 = document.getElementById("field4").value.trim();
    const specificChecked = document.getElementById("specificCheckbox").checked;
    const scalingChecked = document.getElementById("scalingCheckbox").checked;

    if (!field1 || !field2) {
        alert("Version and Customer are required.");
        return;
    }

    if (specificChecked && !field3) {
        alert("Specific build field is required when checkbox is checked.");
        return;
    }

    if (scalingChecked && !field4) {
        alert("Scaling customer field is required when checkbox is checked.");
        return;
    }

    const data = {
        field1: field1,
        field2: field2,
        field3: specificChecked ? field3 : '',
        field4: scalingChecked ? field4 : ''
    };

    const terminalOutput = document.getElementById("terminalOutput");
    terminalOutput.innerHTML = "<p class='output-line'>Starting Kompass Build...</p>";

    const statusLabel = document.getElementById("status-label");
    const statusIndicator = document.getElementById("status-indicator");
    statusLabel.textContent = `Building ${field1} for ${field2}`;
    statusIndicator.classList.remove("idle");
    statusIndicator.classList.add("running");

    fetch("/start_kompass", {
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
        terminalOutput.innerHTML += "<p class='output-line' style='color:red;'>Error: " + error + "</p>";
        statusLabel.textContent = "Ready to build";
        statusIndicator.classList.remove("running");
        statusIndicator.classList.add("idle");
    });
}

function stop_kompass_build() {
    fetch("/stop_kompass", {
        method: "POST"
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message || data.error);
        const statusLabel = document.getElementById("status-label");
        const statusIndicator = document.getElementById("status-indicator");
        statusLabel.textContent = "Ready to build";
        statusIndicator.classList.remove("running");
        statusIndicator.classList.add("idle");
    })
    .catch((error) => {
        alert('Error: ' + error);
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

window.addEventListener('beforeunload', function() {
    if (statusPollingInterval) {
        clearInterval(statusPollingInterval);
    }
});