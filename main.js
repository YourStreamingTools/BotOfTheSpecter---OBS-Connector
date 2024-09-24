const { app, BrowserWindow } = require('electron');
const path = require('path');

// Disable hardware acceleration
app.disableHardwareAcceleration();

// Additional command-line switches to disable GPU features
app.commandLine.appendSwitch('disable-gpu');
app.commandLine.appendSwitch('disable-gpu-compositing');
app.commandLine.appendSwitch('disable-d3d11');
app.commandLine.appendSwitch('disable-d3d11-debug-layer');
app.commandLine.appendSwitch('disable-es3-gl-context');

function createWindow() {
    const win = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            contextIsolation: true,
            nodeIntegration: false,
        },
    });
    win.loadFile(path.join(__dirname, 'index.html'));
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