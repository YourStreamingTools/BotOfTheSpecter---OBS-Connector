// Import required modules
const axios = require('axios');
const keytar = require('keytar');
const io = require('socket.io-client');
const fs = require('fs');
const path = require('path');
const os = require('os');
const ini = require('ini');
const VERSION = '1.0';
let socket;

// Set up event listener for when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    initApp();
});

// Initialize the application
async function initApp() {
    const apiKey = await getApiKey();
    if (apiKey) {
        const isValid = await validateApiKey(apiKey);
        if (isValid) {
            showMainView();
        } else {
            showApiKeyEntry();
        }
    } else {
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
    try {
        const response = await axios.get('https://api.botofthespecter.com/checkkey', {
            params: { api_key: apiKey },
            timeout: 5000,
        });
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
        <h1>BotOfTheSpecter OBS Connector</h1>
        <form id="api-key-form">
            <label for="apiKey">API Auth Key:</label>
            <input type="text" id="apiKey" name="apiKey" required />
            <button type="submit">Validate Key</button>
        </form>
        <div id="message"></div>
    `;
    document.getElementById('api-key-form').addEventListener('submit', handleApiKeySubmit);
}

// Handle submission of the API Key form
async function handleApiKeySubmit(event) {
    event.preventDefault();
    const apiKey = document.getElementById('apiKey').value.trim();
    const messageDiv = document.getElementById('message');
    messageDiv.textContent = 'Validating API Key...';
    const isValid = await validateApiKey(apiKey);
    if (isValid) {
        await saveApiKey(apiKey);
        messageDiv.textContent = 'API Key is valid!';
        showMainView();
    } else {
        messageDiv.textContent = 'Invalid API Key. Please try again.';
    }
}

// Display the main application view
function showMainView() {
    const appDiv = document.getElementById('app');
    appDiv.innerHTML = `
        <h1>BotOfTheSpecter OBS Connector</h1>
        <div id="status">
            <p>WebSocket Status: <span id="websocket-status">Disconnected</span></p>
        </div>
        <div id="logs"></div>
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
        socket.emit('REGISTER', { code: apiKey, name: `OBS Connector V${VERSION}` });
        updateStatus('Connected');
        registerEventHandlers();
    });
    socket.on('SUCCESS', (data) => {
        console.log('WebSocket registration successful:', data);
    });
    socket.on('ERROR', (error) => {
        console.error('WebSocket registration failed:', error);
    });
    socket.on('disconnect', (reason) => {
        console.warn('Disconnected from WebSocket server:', reason);
        updateStatus('Disconnected');
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