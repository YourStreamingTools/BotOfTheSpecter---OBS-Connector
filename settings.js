const fs = require('fs');
const path = require('path');
const keytar = require('keytar');
const os = require('os');
const ini = require('ini');
const settingsDir = path.join(os.homedir(), 'AppData', 'Local', 'YourStreamingTools', 'BotOfTheSpecterOBSConnector');
const settingsPath = path.join(settingsDir, 'settings.ini');

// Ensure the settings directory exists
if (!fs.existsSync(settingsDir)) {
    fs.mkdirSync(settingsDir, { recursive: true });
}

// Load settings from the INI file
function loadSettings() {
    if (fs.existsSync(settingsPath)) {
        const rawData = fs.readFileSync(settingsPath, 'utf-8');
        return ini.parse(rawData);
    }
    return {
        OBS: {
            obsUrl: 'ws://localhost',
            obsPort: '4455',
            obsPassword: ''
        }
    };
}

// Save settings to the INI file
function saveSettings(settings) {
    const iniContent = ini.stringify(settings);
    fs.writeFileSync(settingsPath, iniContent);
}

// Load form with saved settings
async function loadForm() {
    const apiKey = await keytar.getPassword('BotOfTheSpecter', 'apiAuthKey');
    const settings = loadSettings();
    document.getElementById('apiKey').value = apiKey || '';
    document.getElementById('obsUrl').value = settings.OBS.obsUrl;
    document.getElementById('obsPort').value = settings.OBS.obsPort;
    document.getElementById('obsPassword').value = settings.OBS.obsPassword || '';
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
    // Save OBS settings to INI file
    const settings = {
        OBS: {
            obsUrl,
            obsPort,
            obsPassword
        }
    };
    saveSettings(settings);
    document.getElementById('message').textContent = 'Settings saved!';
});

// Load settings when page is loaded
window.onload = loadForm;