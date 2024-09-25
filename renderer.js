const axios = require('axios');
const keytar = require('keytar');
const io = require('socket.io-client');
const OBSWebSocket = require('obs-websocket-js');

const VERSION = '1.0';
let socket;
let obs = new OBSWebSocket();

console.log("Renderer script is running!");

// Set up event listener for when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log("Renderer.js: DOM Content Loaded");
    const appDiv = document.getElementById('app');
    appDiv.innerHTML = '<h2>Renderer.js is working!</h2>';
    initApp();  // Initialize the application
});

// Initialize the application
async function initApp() {
    console.log("Initializing the app...");
    const apiKey = await getApiKey();
    console.log("Retrieved API key:", apiKey);
    if (apiKey) {
        const isValid = await validateApiKey(apiKey);
        console.log("API key valid:", isValid);
        if (isValid) {
            showMainView();
        } else {
            showApiKeyEntry();
        }
    } else {
        console.log("No API key found, showing API key entry form.");
        showApiKeyEntry();
    }
}

// Retrieve the API Key from secure storage
async function getApiKey() {
    return await keytar.getPassword('BotOfTheSpecter', 'apiAuthKey');
}

// Save the API Key securely
async function saveApiKey(apiKey) {
    await keytar.setPassword('BotOfTheSpecter', 'apiAuthKey', apiKey);
}

// Validate the API Key by contacting your API server
async function validateApiKey(apiKey) {
    console.log("Validating API key...");
    try {
        const response = await axios.get('https://api.botofthespecter.com/checkkey', {
            params: { api_key: apiKey },
            timeout: 5000,
        });
        console.log("API validation response:", response.data);
        return response.data.status === 'Valid API Key';
    } catch (error) {
        console.error('Error validating API Key:', error);
        alert('Network error while validating API Key. Please check your internet connection.');
        return false;
    }
}

// Display the API Key entry form
function showApiKeyEntry() {
    const appDiv = document.getElementById('app');
    appDiv.innerHTML = `
        <section class="section">
            <h1 class="title">BotOfTheSpecter - OBS Connector</h1>
            <div class="box">
                <form id="api-key-form">
                    <div class="field">
                        <label class="label" for="apiKey">API Auth Key</label>
                        <div class="control">
                            <input class="input" type="text" id="apiKey" name="apiKey" placeholder="Enter your API Key" required />
                        </div>
                    </div>
                    <div class="control">
                        <button class="button is-primary" type="submit">Validate Key</button>
                    </div>
                </form>
                <p id="message" class="help"></p>
            </div>
        </section>
    `;
    document.getElementById('api-key-form').addEventListener('submit', handleApiKeySubmit);
}

// Handle submission of the API Key form
async function handleApiKeySubmit(event) {
    event.preventDefault();
    const apiKey = document.getElementById('apiKey').value.trim();
    const messageDiv = document.getElementById('message');
    messageDiv.textContent = '';
    const isValid = await validateApiKey(apiKey);
    if (isValid) {
        await saveApiKey(apiKey);
        messageDiv.className = 'help is-success';
        messageDiv.textContent = 'API Key is valid!';
        setTimeout(showMainView, 1000);
    } else {
        messageDiv.className = 'help is-danger';
        messageDiv.textContent = 'Invalid API Key. Please try again.';
    }
}

// Display the main application view
async function showMainView() {
    const appDiv = document.getElementById('app');
    appDiv.innerHTML = `
        <section class="section">
            <h1 class="title">BotOfTheSpecter OBS Connector</h1>
            <div id="status" class="content">
                <p>WebSocket Status: <span id="websocket-status">Disconnected</span></p>
                <p>OBS Status: <span id="obs-status">Disconnected</span></p>
            </div>
            <div id="logs" class="content">
                <h2 class="subtitle">Logs</h2>
            </div>
            <div class="box">
                <form id="obs-connection-form">
                    <div class="field">
                        <label class="label" for="obsUrl">OBS WebSocket URL</label>
                        <div class="control">
                            <input class="input" type="text" id="obsUrl" name="obsUrl" placeholder="ws://localhost" value="ws://localhost" required />
                        </div>
                    </div>
                    <div class="field">
                        <label class="label" for="obsPort">Port</label>
                        <div class="control">
                            <input class="input" type="number" id="obsPort" name="obsPort" placeholder="4455" value="4455" required />
                        </div>
                    </div>
                    <div class="field">
                        <label class="label" for="obsPassword">Password</label>
                        <div class="control">
                            <input class="input" type="password" id="obsPassword" name="obsPassword" placeholder="OBS WebSocket Password (optional)" />
                        </div>
                    </div>
                    <div class="control">
                        <button class="button is-primary" type="submit">Connect to OBS</button>
                    </div>
                </form>
                <p id="obs-message" class="help"></p>
            </div>
        </section>
    `;
    updateStatus('Disconnected', 'websocket-status');
    updateStatus('Disconnected', 'obs-status');
    // Start connection to the WebSocket server
    connectToWebSocket();
    // Handle the OBS connection form
    document.getElementById('obs-connection-form').addEventListener('submit', handleOBSConnectionFormSubmit);
}

// Handle OBS connection form submission
async function handleOBSConnectionFormSubmit(event) {
    event.preventDefault();
    const obsUrl = document.getElementById('obsUrl').value.trim();
    const obsPort = document.getElementById('obsPort').value.trim();
    const obsPassword = document.getElementById('obsPassword').value.trim();
    const fullWebSocketURL = `${obsUrl}:${obsPort}`;
    console.log(`Connecting to OBS WebSocket at ${fullWebSocketURL}`);
    // Connect to OBS using the provided details
    await connectToOBS(fullWebSocketURL, obsPassword);
}

// Connect to OBS
async function connectToOBS(url, password = null) {
    try {
        const connectionDetails = password ? { address: url, password } : { address: url };
        // Attempt to connect to OBS WebSocket
        await obs.connect(connectionDetails);
        console.log('Connected to OBS');
        updateStatus('Connected', 'obs-status');
        // Listen for OBS disconnection
        obs.on('ConnectionClosed', () => {
            console.log('OBS Disconnected');
            updateStatus('Disconnected', 'obs-status');
        });
    } catch (error) {
        console.error('Failed to connect to OBS:', error);
        updateStatus('Connection Error', 'obs-status');
        document.getElementById('obs-message').textContent = 'Failed to connect to OBS. Check your WebSocket settings.';
    }
}

// Connect to your WebSocket server
async function connectToWebSocket() {
    const apiKey = await getApiKey();
    if (!apiKey) {
        console.error('API Key not found.');
        return;
    }
    socket = io('wss://websocket.botofthespecter.com', {
        secure: true,
        reconnection: true,
        reconnectionAttempts: Infinity,
        reconnectionDelay: 1000,
        timeout: 5000,
        transports: ['websocket'],
    });
    socket.on('connect', () => {
        console.log('Connected to WebSocket server.');
        // Emit the 'REGISTER' event with 'code' and 'name'
        socket.emit('REGISTER', { code: apiKey, name: `OBS Connector V${VERSION}` });
        updateStatus('Connected', 'websocket-status');
        registerEventHandlers();
    });
    socket.on('SUCCESS', (data) => {
        console.log('WebSocket registration successful:', data);
        logMessage('WebSocket registration successful.');
    });
    socket.on('ERROR', (error) => {
        console.error('WebSocket registration failed:', error);
        logMessage('WebSocket registration failed.');
    });
    socket.on('disconnect', (reason) => {
        console.warn('Disconnected from WebSocket server:', reason);
        updateStatus('Disconnected', 'websocket-status');
    });
    socket.on('connect_error', (error) => {
        console.error('WebSocket connection error:', error);
        updateStatus('Connection Error', 'websocket-status');
    });
}

// Register event handlers for WebSocket events
function registerEventHandlers() {
    // Add event handlers as needed
    // For now, we'll log incoming events
    socket.onAny((event, data) => {
        logMessage(`Received event '${event}' with data: ${JSON.stringify(data)}`);
    });
}

// Update the connection status displayed in the UI
function updateStatus(status, elementId) {
    document.getElementById(elementId).textContent = status;
}

// Log messages to the UI
function logMessage(message) {
    const logsDiv = document.getElementById('logs');
    const p = document.createElement('p');
    p.textContent = message;
    logsDiv.appendChild(p);
}