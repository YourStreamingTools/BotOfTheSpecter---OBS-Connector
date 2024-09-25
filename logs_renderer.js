const { ipcRenderer } = require('electron');

// Receive logs from the main renderer process and display them
ipcRenderer.on('update-logs', (event, logs) => {
    const logContentDiv = document.getElementById('log-content');
    logContentDiv.innerHTML = ''; // Clear previous logs
    logs.forEach(log => {
        const p = document.createElement('p');
        p.textContent = log;
        logContentDiv.appendChild(p);
    });
});
