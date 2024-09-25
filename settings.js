const fs = require('fs');
const path = require('path');
const keytar = require('keytar');
const settingsPath = path.join(__dirname, 'settings.json');

// Load settings from the file or create default settings
function loadSettings() {
    if (fs.existsSync(settingsPath)) {
        const rawData = fs.readFileSync(settingsPath);
        return JSON.parse(rawData);
    }
    return {
        obsUrl: 'ws://localhost',
        obsPort: '4455',
        obsPassword: ''
    };
}

// Save settings to file
function saveSettings(settings) {
    fs.writeFileSync(settingsPath, JSON.stringify(settings, null, 2));
}

// Load form with saved settings
async function loadForm() {
    const apiKey = await keytar.getPassword('BotOfTheSpecter', 'apiAuthKey');
    const settings = loadSettings();
    document.getElementById('apiKey').value = apiKey || '';
    document.getElementById('obsUrl').value = settings.obsUrl;
    document.getElementById('obsPort').value = settings.obsPort;
    document.getElementById('obsPassword').value = settings.obsPassword || '';
}

// Save settings when form is submitted
document.getElementById('settings-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const apiKey = document.getElementById('apiKey').value;
    const obsUrl = document.getElementById('obsUrl').value;
    const obsPort = document.getElementById('obsPort').value;
    const obsPassword = document.getElementById('obsPassword').value;
    // Save API key securely
    await keytar.setPassword('BotOfTheSpecter', 'apiAuthKey', apiKey);
    // Save OBS settings to file
    const settings = {
        obsUrl,
        obsPort,
        obsPassword
    };
    saveSettings(settings);
    document.getElementById('message').textContent = 'Settings saved!';
});

// Load settings when page is loaded
window.onload = loadForm;
