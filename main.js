const { app, BrowserWindow, Menu } = require('electron');
const path = require('path');
const url = require('url');
let settingsWindow;

// Disable hardware acceleration
app.disableHardwareAcceleration();

// Function to create the main window
function createWindow() {
    const win = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
            enableRemoteModule: true,
        },
        icon: path.join(__dirname, 'assets/icons/app-icon.png'),
    });
    win.loadURL(url.format({
        pathname: path.join(__dirname, 'index.html'),
        protocol: 'file:',
        slashes: true,
    }));

    // Create the custom menu
    const menu = Menu.buildFromTemplate([
        {
            label: 'File',
            submenu: [
                { label: 'Settings', click: createSettingsWindow },
                { label: 'Exit', click: () => { app.quit(); } },
            ]
        },
        {
            label: 'View',
            submenu: [
                { role: 'reload' },
                { label: 'Force Reload', accelerator: 'CmdOrCtrl+Shift+R', click: () => { win.webContents.reloadIgnoringCache(); }},
                { role: 'toggledevtools' }
            ]
        },
        {
            label: 'Help',
            submenu: [
                { label: 'About', click: () => { console.log('About clicked'); } }
            ]
        }
    ]);
    // Set the application menu
    Menu.setApplicationMenu(menu);
}

// Create a new settings window
function createSettingsWindow() {
    if (settingsWindow) {
        settingsWindow.focus();
        return;
    }

    settingsWindow = new BrowserWindow({
        width: 400,
        height: 300,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
        }
    });

    settingsWindow.loadURL(url.format({
        pathname: path.join(__dirname, 'settings.html'),
        protocol: 'file:',
        slashes: true,
    }));

    settingsWindow.on('closed', () => {
        settingsWindow = null;
    });
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});