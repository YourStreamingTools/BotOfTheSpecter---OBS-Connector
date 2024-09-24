const { app, BrowserWindow, Menu } = require('electron');
const path = require('path');
const url = require('url');

// Disable hardware acceleration
app.disableHardwareAcceleration();

function createWindow() {
    const win = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
            enableRemoteModule: true,
        },
        icon: path.join(__dirname, 'assets/icons/app-icon.png')
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
            label: 'Window',
            submenu: [
                { role: 'minimize' },
                { role: 'close' },
            ]
        },
        {
            label: 'Help',
            submenu: [
                {
                    label: 'About',
                    click: () => {
                        console.log('About clicked');
                    }
                }
            ]
        }
    ]);
    // Set the application menu
    Menu.setApplicationMenu(menu);
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