const axios = require('axios');
const keytar = require('keytar');
const io = require('socket.io-client');

const VERSION = '1.0';
let socket;

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
function showMainView() {
    const appDiv = document.getElementById('app');
    appDiv.innerHTML = `
        <section class="section">
            <h1 class="title">BotOfTheSpecter OBS Connector</h1>
            <div id="status" class="content">
                <p><strong>WebSocket Status:</strong> <span id="websocket-status">Disconnected</span></p>
            </div>
            <div id="logs" class="content">
                <h2 class="subtitle">Logs</h2>
            </div>
        </section>
    `;
    updateStatus('Disconnected');
    // Start connection to the WebSocket server
    connectToWebSocket();
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
        updateStatus('Connected');
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
        updateStatus('Disconnected');
    });
    socket.on('connect_error', (error) => {
        console.error('WebSocket connection error:', error);
        logMessage('WebSocket connection error.');
        updateStatus('Connection Error');
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
function updateStatus(status) {
    document.getElementById('websocket-status').textContent = status;
}

// Log messages to the UI
function logMessage(message) {
    const logsDiv = document.getElementById('logs');
    const p = document.createElement('p');
    p.textContent = message;
    logsDiv.appendChild(p);
}